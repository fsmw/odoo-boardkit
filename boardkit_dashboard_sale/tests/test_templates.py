# Copyright 2026 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase, tagged

from odoo.addons.boardkit_dashboard.tests.common import BoardkitTemplateSmokeMixin


@tagged("post_install", "-at_install")
class TestSaleDashboardTemplates(BoardkitTemplateSmokeMixin, TransactionCase):
    template_xmlids = (
        "boardkit_dashboard_sale.template_sale_overview",
        "boardkit_dashboard_sale.template_sale_overview_es_cl",
    )

    def test_es_cl_template_is_localized_and_functionally_equivalent(self):
        english = self.env.ref("boardkit_dashboard_sale.template_sale_overview")
        spanish = self.env.ref("boardkit_dashboard_sale.template_sale_overview_es_cl")
        self.assertIn("es_CL", spanish.name)
        self.assertEqual(spanish.key, "sale_overview_es_cl")
        self.assertEqual(spanish.group_ids, english.group_ids)

        def without_labels(value):
            if isinstance(value, dict):
                return {
                    key: without_labels(item)
                    for key, item in value.items()
                    if key not in {"name", "description", "tags"}
                }
            if isinstance(value, list):
                return [without_labels(item) for item in value]
            return value

        self.assertEqual(
            without_labels(spanish.payload), without_labels(english.payload)
        )
        english_board = english.payload["dashboards"][0]
        spanish_board = spanish.payload["dashboards"][0]
        self.assertEqual(spanish_board["tags"], ["Ventas"])
        self.assertNotEqual(spanish_board["name"], english_board["name"])
        self.assertNotEqual(spanish_board["description"], english_board["description"])
        self.assertNotEqual(
            [item["name"] for item in spanish_board["items"]],
            [item["name"] for item in english_board["items"]],
        )
        self.assertNotEqual(
            [item["name"] for item in spanish_board["filters"]],
            [item["name"] for item in english_board["filters"]],
        )

    def test_create_from_template_sale_overview(self):
        template = self.env.ref("boardkit_dashboard_sale.template_sale_overview")
        dashboard_ids = self.env["boardkit.dashboard"].create_from_template(template.id)
        dashboard = self.env["boardkit.dashboard"].browse(dashboard_ids)
        self.assertEqual(len(dashboard), 1)
        self.assertEqual(dashboard.name, "Sales Overview")
        self.assertFalse(dashboard.published)
        self.assertFalse(dashboard.menu_id)
        self.assertEqual(
            dashboard.group_ids,
            self.env.ref("sales_team.group_sale_salesman_all_leads"),
        )
        self.assertEqual(len(dashboard.item_ids), 13)
        self.assertFalse(dashboard.item_ids.filtered(lambda i: i.item_type == "gauge"))
        self.assertEqual(len(dashboard.filter_ids), 4)
        self.assertTrue(
            all(item.model_name == "sale.order" for item in dashboard.item_ids)
        )

        untaxed = dashboard.item_ids.filtered(lambda i: i.name == "Untaxed Total")
        self.assertEqual(untaxed.aggregation, "sum")
        self.assertEqual(untaxed.measure_field_id.name, "amount_untaxed")
        self.assertEqual(untaxed.unit_type, "monetary")
        self.assertTrue(untaxed.compare_previous_period)

        quotations = dashboard.item_ids.filtered(lambda i: i.name == "Quotations")
        self.assertFalse(quotations.date_field_id)

        average = dashboard.item_ids.filtered(lambda i: i.name == "Average Order Value")
        self.assertEqual(average.aggregation, "avg")
        self.assertEqual(average.measure_field_id.name, "amount_untaxed")
        self.assertTrue(average.compare_previous_period)

        confirmation = dashboard.item_ids.filtered(
            lambda i: i.name == "Confirmation Rate"
        )
        self.assertEqual(confirmation.kpi_mode, "comparison")
        self.assertEqual(confirmation.kpi_display, "percent")
        self.assertEqual(confirmation.model_2_name, "sale.order")
        # The rate needs the whole period as denominator, not only the orders
        # that were already decided.
        self.assertIn("draft", confirmation.domain_2)
        self.assertEqual(confirmation.date_field_id, confirmation.date_field_2_id)

        status_chart = dashboard.item_ids.filtered(
            lambda i: i.name == "Orders by Status"
        )
        self.assertEqual(status_chart.item_type, "doughnut")
        self.assertEqual(status_chart.group_by_field_id.name, "state")
        # A status snapshot must not be cut by the dashboard date filter.
        self.assertFalse(status_chart.date_field_id)

        recent = dashboard.item_ids.filtered(lambda i: i.name == "Recent Orders")
        column_names = recent.list_column_ids.mapped("field_id.name")
        self.assertIn("invoice_status", column_names)
        self.assertIn("user_id", column_names)
        self.assertIn("amount_untaxed", column_names)
