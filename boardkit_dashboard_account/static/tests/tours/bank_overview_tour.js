// Copyright 2026 Escodoo
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("boardkit_bank_overview_tour", {
    steps: () => [
        {
            content: "The bank overview is rendered",
            trigger: ".o_boardkit_bank_overview",
        },
        {
            content: "The selected journal balance is displayed",
            trigger: ".o_boardkit_bank_balance",
        },
        {
            content: "The empty transaction state is visible",
            trigger: ".o_boardkit_bank_empty_transactions",
        },
        {
            content: "Open the selected journal transactions",
            trigger: ".o_boardkit_bank_actions button:first-child",
            run: "click",
        },
        {
            content: "The standard transaction list opens",
            trigger: ".o_list_view",
        },
    ],
});
