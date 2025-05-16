from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Add a field which can be read to act as conditional for certain read only fields
    is_restricted = fields.Boolean(
        string="Restrict modification", compute="_compute_is_restricted"
    )

    # Restrict if user is not an admin in sales app && the id of record has been saved in db
    def _compute_is_restricted(self):
        for rec in self:
            rec.is_restricted = (
                not self.env.user.has_group("sales_team.group_sale_manager")
            ) and (not isinstance(self.id, models.NewId))
