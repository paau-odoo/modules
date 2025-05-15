from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _cron_auto_cancel(self):
        # Filter sale orders for validity date which has passed
        today = fields.Date.today()
        orders = self.search([("validity_date", "<", today)])

        # Cancel those orders
        for o in orders:
            o["state"] = "cancel"
