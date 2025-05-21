from odoo import fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    # Code field to build the variant name from
    code = fields.Char(string="Code")
