from odoo import fields, models, api
import random


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # When product group changes, generate a barcode for the product prepended with the group
    @api.onchange("product_group")
    def _onchange_product_group(self):
        for r in self:
            if r.product_group:
                # Make a 6 digit random code
                r.barcode = f"{r.product_group[:2].upper()}.{format(random.randint(0, 999999), "06d")}"

    # New field for product group
    product_group = fields.Selection(
        [
            ("printer", "Printer"),
            ("reader", "Reader"),
            ("scanner", "Scanner"),
        ],
        required=True,
        onchange=_onchange_product_group,
    )
