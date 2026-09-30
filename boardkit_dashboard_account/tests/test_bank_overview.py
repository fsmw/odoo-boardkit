# Copyright 2026 Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBankOverview(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "BoardKit Bank",
                "code": "BKBK",
                "type": "bank",
                "company_id": cls.company.id,
                "show_on_dashboard": True,
            }
        )
        cls.item = cls.env["boardkit.dashboard.item"].create(
            {
                "name": "Bank overview test",
                "dashboard_id": cls.env["boardkit.dashboard"]
                .create({"name": "Bank overview test", "published": True})
                .id,
                "item_type": "bank_overview",
                "model_id": cls.env.ref("account.model_account_journal").id,
            }
        )

    def test_empty_bank_journal_returns_summary_and_empty_activity(self):
        data = self.item._get_data({"bank_journal_id": self.journal.id})
        bank = next(item for item in data["journals"] if item["id"] == self.journal.id)
        standard_data = self.journal._get_journal_dashboard_data_batched()[
            self.journal.id
        ]
        direct_payment_balance = self.journal._get_direct_bank_payments()[
            self.journal.id
        ][1]

        self.assertEqual(data["selected_journal_id"], self.journal.id)
        self.assertEqual(data["selected_journal"]["id"], self.journal.id)
        self.assertEqual(data["transactions"], [])
        self.assertEqual(
            bank["number_to_reconcile"], standard_data["number_to_reconcile"]
        )
        self.assertEqual(bank["number_to_check"], standard_data["number_to_check"])
        self.assertEqual(bank["currency"]["id"], self.company.currency_id.id)
        self.assertEqual(
            bank["balance"],
            self.journal.current_statement_balance + direct_payment_balance,
        )

    def test_only_accessible_selected_journal_is_returned(self):
        data = self.item._get_data({"bank_journal_id": "999999999"})

        self.assertIn(self.journal.id, [row["id"] for row in data["journals"]])
        self.assertIn(
            data["selected_journal_id"],
            [row["id"] for row in data["journals"]],
        )
        self.assertEqual(
            data["actions"]["transactions"]["domain"][0],
            ("journal_id", "=", data["selected_journal_id"]),
        )

    def test_statement_lines_are_limited_to_ten_and_current_journal(self):
        lines = self.env["account.bank.statement.line"]
        for index in range(12):
            lines.create(
                {
                    "payment_ref": f"BoardKit transaction {index}",
                    "journal_id": self.journal.id,
                    "amount": index + 1,
                    "date": "2026-01-%02d" % (index + 1),
                }
            )

        data = self.item._get_data({"bank_journal_id": self.journal.id})

        self.assertEqual(len(data["transactions"]), 10)
        self.assertEqual(data["transactions"][0]["label"], "BoardKit transaction 11")
        self.assertTrue(all(row["currency"]["id"] for row in data["transactions"]))

    def test_restricted_user_gets_empty_overview(self):
        user = self.env["res.users"].create(
            {
                "name": "BoardKit Restricted User",
                "login": "boardkit_restricted_user",
                "company_id": self.company.id,
                "company_ids": [(6, 0, self.company.ids)],
                "groups_id": [
                    (
                        6,
                        0,
                        (
                            self.env.ref("base.group_user")
                            | self.env.ref("boardkit_dashboard.group_dashboard_user")
                        ).ids,
                    )
                ],
            }
        )

        data = self.item.with_user(user)._get_data({})

        self.assertEqual(data["journals"], [])
        self.assertFalse(data["selected_journal_id"])
        self.assertFalse(data["can_reconcile"])

    def test_reconciliation_action_is_scoped_for_accounting_user(self):
        groups = (
            self.env.ref("base.group_user")
            | self.env.ref("boardkit_dashboard.group_dashboard_user")
            | self.env.ref("account.group_account_user")
        )
        user = self.env["res.users"].create(
            {
                "name": "BoardKit Accounting User",
                "login": "boardkit_accounting_user",
                "company_id": self.company.id,
                "company_ids": [(6, 0, self.company.ids)],
                "groups_id": [(6, 0, groups.ids)],
            }
        )

        data = self.item.with_user(user)._get_data({"bank_journal_id": self.journal.id})

        self.assertTrue(data["can_reconcile"])
        self.assertEqual(
            data["actions"]["reconcile"]["domain"],
            [
                ("journal_id", "=", self.journal.id),
                ("is_reconciled", "=", False),
                ("move_id.state", "=", "posted"),
            ],
        )

    def test_journals_are_scoped_to_active_companies(self):
        other_company = self.env["res.company"].create(
            {"name": "BoardKit Other Company"}
        )
        other_journal = self.env["account.journal"].create(
            {
                "name": "BoardKit Other Bank",
                "code": "BKOB",
                "type": "bank",
                "company_id": other_company.id,
                "show_on_dashboard": True,
            }
        )

        data = self.item.with_context(allowed_company_ids=[self.company.id])._get_data(
            {"bank_journal_id": other_journal.id}
        )

        journal_ids = [row["id"] for row in data["journals"]]
        self.assertNotIn(other_journal.id, journal_ids)
        self.assertIn(data["selected_journal_id"], journal_ids)


@tagged("post_install", "-at_install")
class TestBankOverviewTour(HttpCase):
    def test_bank_overview_render_and_transaction_navigation(self):
        company = self.env.company
        self.env["account.journal"].create(
            {
                "name": "BoardKit Tour Bank",
                "code": "BKTR",
                "type": "bank",
                "company_id": company.id,
                "show_on_dashboard": True,
            }
        )
        dashboard = self.env["boardkit.dashboard"].create(
            {
                "name": "Bank overview tour",
                "published": True,
                "menu_parent_id": self.env.ref(
                    "boardkit_dashboard.menu_dashboard_root"
                ).id,
            }
        )
        self.env["boardkit.dashboard.item"].create(
            {
                "name": "Bank overview",
                "dashboard_id": dashboard.id,
                "item_type": "bank_overview",
                "model_id": self.env.ref("account.model_account_journal").id,
            }
        )

        self.start_tour(
            f"/odoo/action-{dashboard.client_action_id.id}",
            "boardkit_bank_overview_tour",
            login="admin",
        )
