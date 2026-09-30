# Copyright 2026 Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Boardkit Dashboard Account",
    "summary": "Invoicing dashboard template for Boardkit",
    "category": "Accounting",
    "version": "18.0.1.1.0",
    "website": "https://github.com/Escodoo/odoo-boardkit",
    "author": "Escodoo",
    "maintainers": ["marcelsavegnago"],
    "development_status": "Beta",
    "license": "AGPL-3",
    "depends": ["boardkit_dashboard", "account"],
    "data": [
        "data/boardkit_dashboard_templates.xml",
        "data/boardkit_dashboard_templates_es_cl.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
    "demo": ["demo/boardkit_dashboard_demo.xml"],
    "assets": {
        "web.assets_tests": [
            "boardkit_dashboard_account/static/tests/tours/**/*",
        ],
    },
    "auto_install": True,
    "installable": True,
}
