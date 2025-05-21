from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # New cost & profit fields. Store cost so it is not recalculated with bad price data
    cost = fields.Monetary(string="Cost", compute="_compute_cost", store=True)
    profit = fields.Monetary(string="Profit", compute="_compute_profit")

    # Date field for parent sale order
    date = fields.Datetime(string="Order Date", related="order_id.date_order")

    # If the cost hasnt been set, or is 0, set the cost to whatever the most recent cost is from the product, via the suggested field
    @api.depends("product_id.avg_cost")
    def _compute_cost(self):
        for rec in self:
            if (not rec.cost) and rec.product_id.avg_cost:
                rec.cost = rec.product_id.avg_cost

    # Compute profit based on given formula
    @api.depends("cost", "price_unit", "qty_invoiced")
    def _compute_profit(self):
        for rec in self:
            rec.profit = rec.qty_invoiced * (rec.price_unit - rec.cost)
