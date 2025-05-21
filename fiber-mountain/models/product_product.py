from odoo import models, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model_create_multi
    def create(self, vals_list):

        # I copied what the create method does, and then added some functionality
        products = super(
            ProductProduct, self.with_context(create_product_product=False)
        ).create(vals_list)
        self.env.registry.clear_cache()

        # Change the reference codes for each unique types
        for p in products:
            # Extract the attribute value IDs from the product that was created to build code
            attr_ids = p.product_template_attribute_value_ids

            # Indicies to insert hyphens
            hyphens = (3, 4)

            # Build the ref code for the unique product
            name = ""
            for i in range(len(attr_ids)):
                name += attr_ids[i].product_attribute_value_id.code

                if i in hyphens:
                    name += "-"

            # Set code for variant
            p.default_code = name

        return products
