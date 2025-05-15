from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.onchange("quantity")
    def _onchange_quantity_check(self):
        # Only do this on receipts
        if self.picking_id.picking_type_code == "incoming":
            # If the q is larger than demand, show the warning
            if self.quantity > self.product_uom_qty:
                return {
                    "warning": {
                        "title": "Warning",
                        "message": "You can't receive more than the ordered quantity. Please, enter another quantity",
                    }
                }
