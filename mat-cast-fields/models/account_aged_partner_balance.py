import datetime

from odoo import models, fields, _
from odoo.tools import SQL
from odoo.tools.misc import format_date

from dateutil.relativedelta import relativedelta
from itertools import chain


class AgedPartnerBalanceCustomHandler(models.AbstractModel):
    _inherit = "account.report.custom.handler"

    def _report_custom_engine_get_salesperson(
        self,
        expressions,
        options,
        date_scope,
        current_groupby,
        next_groupby,
        offset=0,
        limit=None,
        warnings=None,
    ):
        # aging_date_field = SQL.identifier("invoice_date")
        # return aging_date_field
        return {"salesperson": "hello"}
