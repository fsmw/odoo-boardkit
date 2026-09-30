# Copyright 2026 Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    """Allow the canonical es_CL template payload to update on upgrade."""
    cr.execute(
        """
        UPDATE ir_model_data
           SET noupdate = FALSE
         WHERE module = 'boardkit_dashboard_account'
           AND name = 'template_account_invoicing_es_cl'
           AND model = 'boardkit.dashboard.template'
        """
    )
