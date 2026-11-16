# Copyright 2026 SMWLAB
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from .common import BoardkitDashboardCommon


@tagged("post_install", "-at_install")
class TestItemPresentations(BoardkitDashboardCommon):
    def _grouped_item(self, item_type):
        return self._create_item(
            name=f"By Country {item_type}",
            item_type=item_type,
            group_by_field_id=self._field("res.partner", "country_id").id,
        )

    def test_ranking_aggregates_like_horizontal_bars(self):
        ranking = self._grouped_item("ranking")
        bars = self._grouped_item("bar_horizontal")

        data = ranking.get_data()

        self.assertEqual(data["labels"], bars.get_data()["labels"])
        self.assertEqual(data["datasets"], bars.get_data()["datasets"])
        self.assertEqual(sorted(data["datasets"][0]["data"]), [1, 2])

    def test_segmented_aggregates_like_pie(self):
        segmented = self._grouped_item("segmented")
        pie = self._grouped_item("pie")

        data = segmented.get_data()

        self.assertEqual(data["labels"], pie.get_data()["labels"])
        self.assertEqual(data["datasets"], pie.get_data()["datasets"])

    def test_headline_returns_single_value(self):
        headline = self._create_item(name="Partners", item_type="headline")

        data = headline.get_data()

        self.assertEqual(data["value"], 3)
        self.assertEqual(data["count"], 3)

    def test_headline_config_exposes_sentence_templates(self):
        headline = self._create_item(
            name="Partners",
            item_type="headline",
            headline_template="We have {value} partners",
            headline_delta_suffix=", {delta} vs previous period",
        )

        config = headline._get_config()

        self.assertEqual(config["type"], "headline")
        self.assertEqual(
            config["headline"],
            {
                "template": "We have {value} partners",
                "delta_suffix": ", {delta} vs previous period",
            },
        )

    def test_headline_exports_like_a_tile(self):
        headline = self._create_item(name="Partners", item_type="headline")

        export = headline.get_export_data()

        self.assertEqual(export["rows"], [["Partners", 3, 3]])

    def test_headline_templates_survive_export_import(self):
        self._create_item(
            name="Partners",
            item_type="headline",
            headline_template="We have {value} partners",
            headline_delta_suffix=", {delta} more",
        )

        payload = self.dashboard.export_config()
        imported = self.env["boardkit.dashboard"].browse(
            self.env["boardkit.dashboard"].import_config(payload)
        )

        headline = imported.item_ids.filtered(lambda item: item.item_type == "headline")
        self.assertEqual(headline.headline_template, "We have {value} partners")
        self.assertEqual(headline.headline_delta_suffix, ", {delta} more")
