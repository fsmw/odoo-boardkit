# Copyright 2026 Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class BoardkitDashboardItem(models.Model):
    _inherit = "boardkit.dashboard.item"

    item_type = fields.Selection(
        selection_add=[("bank_overview", "Bank Overview")],
        ondelete={"bank_overview": "cascade"},
    )

    def _get_data(self, params):
        self.ensure_one()
        if self.item_type == "bank_overview":
            return self._get_bank_overview_data(params or {})
        return super()._get_data(params)

    def _get_bank_overview_data(self, params):
        """Return the current user's visible bank journals and one journal's lines."""
        Journal = self.env["account.journal"]
        StatementLine = self.env["account.bank.statement.line"]
        if not Journal.has_access("read"):
            return self._empty_bank_overview()

        journals = Journal.search(
            [
                ("type", "in", ("bank", "cash", "credit")),
                ("show_on_dashboard", "=", True),
                ("company_id", "in", self.env.companies.ids),
            ],
            order="name, id",
        )
        if not journals:
            return self._empty_bank_overview()

        # Match the balance and counts shown by Odoo's standard journal card.
        standard_data = journals._get_journal_dashboard_data_batched()
        direct_payments = journals._get_direct_bank_payments()
        journal_options = []
        for journal in journals:
            currency = journal.currency_id or journal.company_id.currency_id
            direct_balance = direct_payments.get(journal.id, (0, 0))[1]
            journal_options.append(
                {
                    "id": journal.id,
                    "name": journal.display_name,
                    "type": journal.type,
                    "balance": journal.current_statement_balance + direct_balance,
                    "number_to_reconcile": standard_data[journal.id].get(
                        "number_to_reconcile", 0
                    ),
                    "number_to_check": standard_data[journal.id].get(
                        "number_to_check", 0
                    ),
                    "currency": self._bank_currency_payload(currency),
                }
            )

        requested_id = params.get("bank_journal_id")
        try:
            requested_id = int(requested_id)
        except (TypeError, ValueError):
            requested_id = False
        selected = journals.filtered(lambda journal: journal.id == requested_id)[:1]
        if not selected:
            selected = journals[:1]

        transactions = []
        if StatementLine.has_access("read"):
            lines = StatementLine.search(
                [
                    ("journal_id", "=", selected.id),
                    ("company_id", "in", self.env.companies.ids),
                ],
                order="date desc, id desc",
                limit=10,
            )
            for line in lines:
                currency = (
                    line.currency_id
                    or selected.currency_id
                    or selected.company_id.currency_id
                )
                if line.is_reconciled:
                    status = "reconciled"
                elif line.move_id.state != "posted":
                    status = "draft"
                elif not line.move_id.checked:
                    status = "to_check"
                else:
                    status = "to_reconcile"
                transactions.append(
                    {
                        "id": line.id,
                        "date": fields.Date.to_string(line.date),
                        "label": line.payment_ref or line.name or "",
                        "amount": line.amount,
                        "currency": self._bank_currency_payload(currency),
                        "status": status,
                    }
                )

        selected_summary = next(
            option for option in journal_options if option["id"] == selected.id
        )
        can_reconcile = self.env.user.has_group("account.group_account_user")
        actions = {
            "transactions": self._bank_statement_line_action(selected),
            "reconcile": self._bank_reconciliation_action(selected)
            if can_reconcile
            else False,
        }
        return {
            "type": "bank_overview",
            "journals": journal_options,
            "selected_journal_id": selected.id,
            "selected_journal": selected_summary,
            "transactions": transactions,
            "actions": actions,
            "can_reconcile": can_reconcile,
            "refreshed_at": fields.Datetime.to_string(fields.Datetime.now()),
        }

    @api.model
    def _empty_bank_overview(self):
        return {
            "type": "bank_overview",
            "journals": [],
            "selected_journal_id": False,
            "selected_journal": False,
            "transactions": [],
            "actions": {},
            "can_reconcile": False,
            "refreshed_at": fields.Datetime.to_string(fields.Datetime.now()),
        }

    @api.model
    def _bank_currency_payload(self, currency):
        return {
            "id": currency.id,
            "code": currency.name,
            "symbol": currency.symbol,
            "position": currency.position,
            "digits": currency.decimal_places,
        }

    @api.model
    def _bank_statement_line_action(self, journal):
        """Open lines, using the Enterprise transaction action when available."""
        action_method = getattr(journal, "action_open_bank_transactions", None)
        if action_method:
            return action_method()
        return {
            "type": "ir.actions.act_window",
            "name": _("Bank Transactions"),
            "res_model": "account.bank.statement.line",
            "view_mode": "list,form",
            "domain": [("journal_id", "=", journal.id)],
            "context": {"default_journal_id": journal.id, "create": False},
        }

    @api.model
    def _bank_reconciliation_action(self, journal):
        """Open Odoo's reconciliation widget or the core unreconciled line view."""
        action_method = getattr(journal, "action_open_reconcile", None)
        if action_method:
            return action_method()
        return {
            "type": "ir.actions.act_window",
            "name": _("Transactions to Reconcile"),
            "res_model": "account.bank.statement.line",
            "view_mode": "list,form",
            "domain": [
                ("journal_id", "=", journal.id),
                ("is_reconciled", "=", False),
                ("move_id.state", "=", "posted"),
            ],
            "context": {"default_journal_id": journal.id, "create": False},
        }
