# Copyright 2026 Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re


_ACTION_RE = re.compile(r"^(ir\.actions\.[a-z_]+)\((\d+),?\)$")
_SUPPORTED_ACTION_MODELS = {
    "ir.actions.report",
    "ir.actions.act_window",
    "ir.actions.act_url",
    "ir.actions.server",
    "ir.actions.client",
}


def migrate(cr, version):
    """Convert the legacy Char repr into the textual value of a Reference."""
    cr.execute(
        """
        SELECT id, menu_replace_original_action
          FROM boardkit_dashboard
         WHERE menu_replace_original_action IS NOT NULL
           AND menu_replace_original_action != ''
        """
    )
    for dashboard_id, legacy_value in cr.fetchall():
        match = _ACTION_RE.fullmatch(legacy_value)
        if not match:
            continue
        action_model, action_id = match.groups()
        if action_model not in _SUPPORTED_ACTION_MODELS:
            continue
        cr.execute(
            "SELECT 1 FROM ir_actions WHERE id = %s AND type = %s",
            (int(action_id), action_model.removeprefix("ir.actions.")),
        )
        if not cr.fetchone():
            continue
        cr.execute(
            "UPDATE boardkit_dashboard SET menu_replace_original_action = %s "
            "WHERE id = %s",
            (f"{action_model},{action_id}", dashboard_id),
        )
