# Copyright 2026 SMWLAB
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from odoo.tests import tagged
from odoo.tools import file_open

from ..tools.palettes import PRESET_PALETTE_COLORS, PRESET_PALETTE_SELECTION
from .common import BoardkitDashboardCommon

TONAL_PRESETS = ("indigo", "teal")


@tagged("post_install", "-at_install")
class TestVisualStyle(BoardkitDashboardCommon):
    def test_new_dashboard_defaults_to_clean_style(self):
        dashboard = self.env["boardkit.dashboard"].create({"name": "Fresh Board"})

        self.assertEqual(dashboard.visual_style, "clean")

    def test_dashboard_payload_exposes_visual_style(self):
        self.dashboard.visual_style = "classic"

        payload = self.env["boardkit.dashboard"].get_dashboard_data(self.dashboard.id)

        self.assertEqual(payload["visual_style"], "classic")

    def test_item_config_follows_dashboard_visual_style(self):
        self.dashboard.visual_style = "clean"
        self.assertEqual(self.tile._get_config()["visual_style"], "clean")

        self.dashboard.visual_style = "classic"

        self.assertEqual(self.tile._get_config()["visual_style"], "classic")

    def test_visual_style_survives_export_import(self):
        self.dashboard.visual_style = "classic"

        payload = self.dashboard.export_config()
        imported = self.env["boardkit.dashboard"].browse(
            self.env["boardkit.dashboard"].import_config(payload)
        )

        self.assertEqual(payload["dashboards"][0]["visual_style"], "classic")
        self.assertEqual(imported.visual_style, "classic")

    def test_import_without_or_with_unknown_style_falls_back_to_clean(self):
        payload = self.dashboard.export_config()
        legacy = dict(payload["dashboards"][0])
        legacy.pop("visual_style")
        unknown = dict(payload["dashboards"][0], visual_style="neon")

        imported = self.env["boardkit.dashboard"].browse(
            self.env["boardkit.dashboard"].import_config(
                {"version": payload["version"], "dashboards": [legacy, unknown]}
            )
        )

        self.assertEqual(imported.mapped("visual_style"), ["clean", "clean"])

    def test_tonal_presets_are_selectable(self):
        keys = [key for key, _label in PRESET_PALETTE_SELECTION]

        for preset in TONAL_PRESETS:
            self.assertIn(preset, keys)
            self.assertGreaterEqual(len(PRESET_PALETTE_COLORS[preset]), 6)

    def test_python_and_js_palettes_stay_in_sync(self):
        with file_open("boardkit_dashboard/static/src/dashboard/utils.js") as source:
            content = source.read()
        block = content.split("export const PALETTES = {", 1)[1].split("\n};", 1)[0]
        js_palettes = {
            match.group(1): re.findall(r"#[0-9A-Fa-f]{6}", match.group(2))
            for match in re.finditer(r"(\w+): \[(.*?)\]", block, re.S)
        }

        self.assertEqual(js_palettes, PRESET_PALETTE_COLORS)
