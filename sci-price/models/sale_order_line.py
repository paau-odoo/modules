from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Compute field for requirement
    price_changed = fields.Boolean(
        string="Price changed since last sale to customer",
        compute="_compute_price_changed",
    )

    # Adding date field directly on this model so that i can .search() and use it to order results
    date_order = fields.Datetime(related="order_id.date_order")

    @api.depends("order_partner_id", "product_id", "price_unit")
    def _compute_price_changed(self):
        for rec in self:
            # Get most recent sale order line with same partner and product
            timestamp = rec.date_order
            prev_line = self.search(
                [
                    ("order_partner_id.id", "=", rec.order_partner_id.id),
                    ("product_id.id", "=", rec.product_id.id),
                    ("date_order", "<", timestamp),
                ],
                order="date_order desc",
                limit=1,
            )
            # If there was a previous relevant sale order line, compare the prices
            if prev_line:
                rec.price_changed = rec.price_unit != prev_line.price_unit
            else:
                rec.price_changed = False
