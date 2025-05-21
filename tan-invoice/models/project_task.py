from odoo import models, fields, api, Command
from datetime import timedelta


class Task(models.Model):
    _inherit = "project.task"

    # New fields
    delivery_date = fields.Date(string="Delivery date")
    invoice_number = fields.Many2one(comodel_name="account.move", string="Invoice")

    @api.depends("delivery_date")
    def _onchange_delivery_date(self):
        # Trigger creating an invoice for billable tasks if a delivery date has been set, AND there is no prior associated invoice
        if self.sale_line_id and self.delivery_date and not self.invoice_number:
            # Create the invoice
            inv = self.env["account.move"].create(
                {
                    "state": "draft",
                    "move_type": "out_invoice",
                    "partner_id": self.partner_id.id,
                    "invoice_date": self.delivery_date,
                    "line_ids": [
                        Command.create(
                            {
                                "product_id": self.sale_line_id.product_id.id,
                                "price_unit": self.sale_line_id.price_unit,
                                "quantity": 1,  # They said always q = 1, otherwise would come from sale line id
                            }
                        )
                    ],
                    "invoice_date_due": self.delivery_date
                    + timedelta(days=7),  # Make the due date 7 days out or something
                }
            )
            # Increment quantity delivered on SO
            self.sale_line_id.qty_delivered += 1
            # Attach invoice to this task
            self.invoice_number = inv
