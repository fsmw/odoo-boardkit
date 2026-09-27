# Copyright 2026 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase, tagged

from odoo.addons.boardkit_dashboard.tests.common import BoardkitTemplateSmokeMixin


@tagged("post_install", "-at_install")
class TestCrmDashboardTemplates(BoardkitTemplateSmokeMixin, TransactionCase):
    template_xmlids = (
        "boardkit_dashboard_crm.template_crm_pipeline",
        "boardkit_dashboard_crm.template_crm_pipeline_es_cl",
    )

    def test_es_cl_template_is_localized_and_functionally_equivalent(self):
        english = self.env.ref("boardkit_dashboard_crm.template_crm_pipeline")
        spanish = self.env.ref("boardkit_dashboard_crm.template_crm_pipeline_es_cl")
        self.assertIn("es_CL", spanish.name)
        self.assertEqual(spanish.key, "crm_pipeline_es_cl")
        self.assertEqual(spanish.group_ids, english.group_ids)

        def without_labels(value):
            if isinstance(value, dict):
                return {
                    key: without_labels(item)
                    for key, item in value.items()
                    if key not in {"name", "description", "tags", "number_style"}
                }
            if isinstance(value, list):
                return [without_labels(item) for item in value]
            return value

        self.assertEqual(
            without_labels(spanish.payload), without_labels(english.payload)
        )
        english_board = english.payload["dashboards"][0]
        spanish_board = spanish.payload["dashboards"][0]
        self.assertEqual(spanish_board["tags"], ["CRM"])
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

    def test_create_from_template_crm_pipeline(self):
        template = self.env.ref("boardkit_dashboard_crm.template_crm_pipeline")
        dashboard_ids = self.env["boardkit.dashboard"].create_from_template(template.id)
        dashboard = self.env["boardkit.dashboard"].browse(dashboard_ids)
        self.assertEqual(len(dashboard), 1)
        self.assertEqual(dashboard.name, "CRM Pipeline")
        self.assertFalse(dashboard.published)
        self.assertFalse(dashboard.menu_id)
        self.assertEqual(
            dashboard.group_ids,
            self.env.ref("sales_team.group_sale_salesman_all_leads"),
        )
        self.assertEqual(len(dashboard.item_ids), 12)
        maps = dashboard.item_ids.filtered(lambda i: i.item_type == "map")
        self.assertEqual(len(maps), 1)
        self.assertEqual(maps.name, "Opportunities by Country")
        self.assertEqual(maps.map_mode, "regions")
        self.assertEqual(maps.group_by_field_id.name, "country_id")
        self.assertEqual(len(dashboard.filter_ids), 4)
        self.assertTrue(
            all(item.model_name == "crm.lead" for item in dashboard.item_ids)
        )

        expected = dashboard.item_ids.filtered(lambda i: i.name == "Expected Revenue")
        self.assertEqual(expected.aggregation, "sum")
        self.assertEqual(expected.measure_field_id.name, "expected_revenue")
        self.assertEqual(expected.unit_type, "monetary")
        self.assertFalse(expected.date_field_id)

        won_revenue = dashboard.item_ids.filtered(lambda i: i.name == "Won Revenue")
        self.assertEqual(won_revenue.date_field_id.name, "date_closed")
        self.assertTrue(won_revenue.compare_previous_period)

        win_rate = dashboard.item_ids.filtered(lambda i: i.name == "Win Rate")
        self.assertEqual(win_rate.kpi_mode, "comparison")
        self.assertEqual(win_rate.kpi_display, "percent")
        self.assertEqual(win_rate.model_2_name, "crm.lead")
        self.assertEqual(win_rate.date_field_id, win_rate.date_field_2_id)

        by_user = dashboard.item_ids.filtered(
            lambda i: i.name == "Open Revenue by Salesperson"
        )
        # Expected revenue is only meaningful while the deal is open.
        self.assertIn("probability", by_user.domain)

        funnel = dashboard.item_ids.filtered(lambda i: i.name == "Pipeline Funnel")
        self.assertEqual(funnel.item_type, "funnel")
        self.assertEqual(funnel.group_by_field_id.name, "stage_id")
        self.assertEqual(funnel.sort_field_id.name, "sequence")
        self.assertEqual(funnel.sort_field_id.model, "crm.stage")

        recent = dashboard.item_ids.filtered(lambda i: i.name == "Recent Opportunities")
        column_names = recent.list_column_ids.mapped("field_id.name")
        self.assertIn("probability", column_names)
        self.assertIn("date_deadline", column_names)
        self.assertIn("user_id", column_names)
