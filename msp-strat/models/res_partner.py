from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class Partner(models.Model):
    _inherit = "res.partner"

    # New properties
    strategic_account = fields.Boolean(string="Strategic Account")
    verified_strategic = fields.Boolean(string="Verified Strategic")
    strategic_duration = fields.Integer(default=10, string="Strategic Duration (Days)")

    # New dates
    approval_date = fields.Date(string="Approval Date")
    strategic_start_date = fields.Date(
        string="Strategic Start", default=datetime.today().date()
    )
    strategic_end_date = fields.Date(
        string="Strategic End", compute="_compute_strategic_end_date"
    )

    def _cron_check_strategic_dates(self):
        # Filter partners by expired strategic date
        today = fields.Date.today()
        partners = self.search([("strategic_end_date", "<", today)])

        # Uncheck the new bool fields for the expired partners
        partners.write({"strategic_account": False, "verified_strategic": False})

    # Compute the end date from start + duration
    @api.depends("strategic_duration", "strategic_start_date")
    def _compute_strategic_end_date(self):
        for rec in self:
            rec.strategic_end_date = rec.strategic_start_date + timedelta(
                days=rec.strategic_duration
            )

    # Make sure you cant put negative duration
    @api.constrains("strategic_duration")
    def _check_strategic_duration(self):
        if self.strategic_duration < 0:
            raise ValidationError("Duration must not be negative!")
