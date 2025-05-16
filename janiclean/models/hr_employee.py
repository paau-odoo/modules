from odoo import fields, models


class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"

    # Action for sending the birthday email
    def _cron_send_birthday_email(self):
        # Get people who have birthday == today
        today = fields.Date.today()
        birthday_people = self.search([("birthday", "=", today)])

        # Grab the email template
        template = self.env.ref("janiclean.email_birthday")

        # Send it off to anyone with a birthday
        for person in birthday_people:
            template.send_mail(person.id, force_send=True)
