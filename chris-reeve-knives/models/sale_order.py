from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Add a compute field which is same as order_line but filters out qty = 0 records
    order_line_filter = fields.One2many(
        comodel_name="sale.order.line",
        inverse_name="order_id",
        string="Filtered Order Lines",
        copy=True,
        auto_join=True,
        compute="_compute_order_line_filter",
    )

    # Compute for filtered order lines
    @api.depends("order_line")
    def _compute_order_line_filter(self):
        # Filter to only order lines with quantity != 0
        for r in self:
            r.order_line_filter = r.order_line.filtered(
                lambda o: o.product_uom_qty != 0
            )

    # I copied over the original _get_order_lines_to_report function and am overriding it to use my filtered compute field instead of order_line to populate the PDF report

    # Another (probably better/ more DRY but more involved) approach could be to override the report xml to point to a custom function which calls & filters the results of the original _get_order_lines_to_report function
    def _get_order_lines_to_report(self):
        down_payment_lines = self.order_line_filter.filtered(
            lambda line: line.is_downpayment
            and not line.display_type
            and not line._get_downpayment_state()
        )

        def show_line(line):
            if not line.is_downpayment:
                return True
            elif line.display_type and down_payment_lines:
                return True
            elif line in down_payment_lines:
                return True
            else:
                return False

        return self.order_line_filter.filtered(show_line)
