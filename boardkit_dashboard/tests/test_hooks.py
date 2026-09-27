# Copyright 2026 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.boardkit_dashboard.hooks import uninstall_hook

from .common import BoardkitDashboardCommon


@tagged("post_install", "-at_install")
class TestUninstallHook(BoardkitDashboardCommon):
    def test_uninstall_hook_removes_runtime_menus_and_actions(self):
        menu = self.dashboard.menu_id
        action = self.dashboard.client_action_id
        self.assertTrue(menu.exists())
        self.assertTrue(action.exists())
        # Keep the dashboard record but drop the FK links so the hook is the
        # one responsible for cleaning the generated menu/action.
        self.dashboard.write({"menu_id": False, "client_action_id": False})
        uninstall_hook(self.env)
        self.assertFalse(menu.exists())
        self.assertFalse(action.exists())

    def test_uninstall_hook_restores_overridden_app_actions(self):
        target = self.env.ref("contacts.menu_contacts")
        original_action = target.action
        self.dashboard.write(
            {
                "menu_parent_id": False,
                "menu_replace_app": True,
                "menu_replace_app_menu_id": target.id,
            }
        )
        self.assertNotEqual(target.action, original_action)

        uninstall_hook(self.env)

        self.assertTrue(target.exists())
        self.assertEqual(target.action, original_action)
