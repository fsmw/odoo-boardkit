// Copyright 2026 SMWLAB
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import {Component, onWillStart, useState} from "@odoo/owl";
import {ensurePhosphor, resolveIcon} from "../dashboard/icon_map";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

const ICON_NAMES_URL = "/boardkit_dashboard/static/lib/phosphor/icons.json";
// Enough to fill the grid without rendering all 1,500 glyphs at once.
const MAX_RESULTS = 72;

let iconNames = null;

async function loadIconNames() {
    if (!iconNames) {
        const response = await fetch(ICON_NAMES_URL);
        if (!response.ok) {
            throw new Error(`Icon list request failed (${response.status})`);
        }
        iconNames = await response.json();
    }
    return iconNames;
}

/**
 * Text field for an icon name with a searchable Phosphor grid.
 *
 * The stored value stays a plain class name (``ph-*``, or a legacy ``fa-*``),
 * so typing a name by hand keeps working.
 */
export class IconPickerField extends Component {
    static template = "boardkit_dashboard.IconPickerField";
    static props = {...standardFieldProps};

    setup() {
        this.state = useState({open: false, query: "", names: [], failed: false});
        onWillStart(() => ensurePhosphor());
    }

    get value() {
        return this.props.record.data[this.props.name] || "";
    }

    get previewClass() {
        return resolveIcon(this.value, true).className;
    }

    get results() {
        const query = this.state.query.trim().toLowerCase().replace(/\s+/g, "-");
        const matches = query
            ? this.state.names.filter((name) => name.includes(query))
            : this.state.names;
        return matches.slice(0, MAX_RESULTS);
    }

    get emptyMessage() {
        if (this.state.failed) {
            return _t("The icon list could not be loaded. Type the icon name instead.");
        }
        return _t("No icon matches this search.");
    }

    async toggle() {
        this.state.open = !this.state.open;
        if (this.state.open && !this.state.names.length) {
            try {
                this.state.names = await loadIconNames();
                this.state.failed = false;
            } catch (error) {
                this.state.failed = true;
                console.warn("Boardkit: icon list could not be loaded", error);
            }
        }
    }

    onSearch(ev) {
        this.state.query = ev.target.value;
    }

    onInput(ev) {
        this.props.record.update({[this.props.name]: ev.target.value.trim()});
    }

    select(name) {
        this.props.record.update({[this.props.name]: name});
        this.state.open = false;
    }

    label(name) {
        return name.replace(/^ph-/, "").replaceAll("-", " ");
    }
}

export const iconPickerField = {
    component: IconPickerField,
    displayName: _t("Icon Picker"),
    supportedTypes: ["char"],
};

registry.category("fields").add("boardkit_icon_picker", iconPickerField);
