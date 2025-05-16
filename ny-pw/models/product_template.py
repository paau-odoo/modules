from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # New fields
    pairs_per_case = fields.Integer(string="Pairs of Shoes per Case")
    price_per_pair = fields.Monetary(string="Price per Pair of Shoes")

    # Update price if prompt conditions are met
    @api.onchange("pairs_per_case", "price_per_pair")
    def _onchange_pairs_prices(self):
        for rec in self:
            # If both fields are != 0, set the list price to it
            if rec.pairs_per_case > 0 and rec.price_per_pair > 0:
                rec.list_price = rec.pairs_per_case * rec.price_per_pair
