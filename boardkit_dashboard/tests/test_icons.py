# Copyright 2026 SMWLAB
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
import re
from pathlib import Path

from odoo.modules import get_module_path
from odoo.tests import tagged
from odoo.tools import file_open

from .common import BoardkitDashboardCommon

ICON_MAP_FILE = "boardkit_dashboard/static/src/dashboard/icon_map.js"
ICON_NAMES_FILE = "boardkit_dashboard/static/lib/phosphor/icons.json"
DEFAULT_ITEM_ICON = "fa-bar-chart"


@tagged("post_install", "-at_install")
class TestIcons(BoardkitDashboardCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with file_open(ICON_MAP_FILE) as source:
            cls.icon_map = dict(
                re.findall(r'"(fa-[a-z0-9-]+)":\s*"(ph-[a-z0-9-]+)"', source.read())
            )
        with file_open(ICON_NAMES_FILE) as source:
            cls.phosphor_names = set(json.load(source))

    def _template_icons(self):
        """Font Awesome icons used by every template shipped in this repo."""
        repo = Path(get_module_path("boardkit_dashboard")).parent
        icons = set()
        for path in repo.glob("boardkit_dashboard*/data/*.xml"):
            icons.update(re.findall(r'"icon": "(fa-[a-z0-9-]+)"', path.read_text()))
        return icons

    def test_icon_map_only_targets_vendored_phosphor_icons(self):
        self.assertTrue(self.icon_map)

        unknown = set(self.icon_map.values()) - self.phosphor_names

        self.assertFalse(unknown)

    def test_icon_map_covers_default_and_template_icons(self):
        expected = self._template_icons() | {DEFAULT_ITEM_ICON}

        missing = expected - set(self.icon_map)

        self.assertFalse(missing)

    def test_single_value_items_get_consecutive_accent_indexes(self):
        second = self._create_item(name="Second Tile", item_type="tile", sequence=20)
        chart = self._create_item(
            name="Chart",
            item_type="bar",
            sequence=30,
            group_by_field_id=self._field("res.partner", "country_id").id,
        )
        third = self._create_item(name="KPI", item_type="kpi", sequence=40)

        indexes = [
            item._get_config()["accent_index"] for item in (self.tile, second, third)
        ]

        self.assertEqual(indexes, [0, 1, 2])
        self.assertEqual(chart._get_config()["accent_index"], 0)

    def test_unsaved_item_preview_has_an_accent_index(self):
        draft = self.env["boardkit.dashboard.item"].new(
            {"name": "Draft", "item_type": "tile"}
        )

        self.assertEqual(draft._get_config()["accent_index"], 0)
