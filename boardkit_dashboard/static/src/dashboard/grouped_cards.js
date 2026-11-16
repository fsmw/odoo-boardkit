// Copyright 2026 SMWLAB
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import {formatItemValue, formatNumber, getPaletteColor} from "./utils";
import {Component} from "@odoo/owl";

// HTML presentations of grouped data. They read the same payload as charts
// (labels + datasets) and plot the first series, which keeps text crisp,
// selectable and reachable by keyboard.

const GROUPED_CARD_PROPS = {
    config: Object,
    data: Object,
    currency: {type: Object, optional: true},
    onSectionClicked: {type: Function, optional: true},
};

function primarySeries(data) {
    const values = data.datasets?.[0]?.data || [];
    return (data.labels || []).map((label, index) => ({
        index,
        label,
        value: Number(values[index]) || 0,
    }));
}

class GroupedCard extends Component {
    static props = GROUPED_CARD_PROPS;

    get clickable() {
        return Boolean(this.props.onSectionClicked);
    }

    formatValue(value) {
        return formatItemValue(value, this.props.config, this.props.currency);
    }

    onEntryClicked(entry) {
        if (this.props.onSectionClicked) {
            this.props.onSectionClicked(0, entry.index);
        }
    }

    onEntryKeydown(ev, entry) {
        if (ev.key === "Enter" || ev.key === " ") {
            ev.preventDefault();
            this.onEntryClicked(entry);
        }
    }
}

/** Ranked rows: label, inline bar scaled to the largest value, amount. */
export class RankingCard extends GroupedCard {
    static template = "boardkit_dashboard.RankingCard";

    get rows() {
        const series = primarySeries(this.props.data);
        const max = Math.max(...series.map((entry) => Math.abs(entry.value)), 0);
        const color = getPaletteColor(this.props.config, 0);
        return series.map((entry) => {
            const share = max ? (Math.abs(entry.value) / max) * 100 : 0;
            return {
                ...entry,
                formatted: this.formatValue(entry.value),
                barStyle: `width: ${share.toFixed(2)}%; background-color: ${color};`,
            };
        });
    }
}

/** One bar split by share of the total, with a legend row per segment. */
export class SegmentedCard extends GroupedCard {
    static template = "boardkit_dashboard.SegmentedCard";

    get total() {
        return primarySeries(this.props.data).reduce(
            (sum, entry) => sum + Math.max(entry.value, 0),
            0
        );
    }

    get formattedTotal() {
        return this.formatValue(this.total);
    }

    get segments() {
        const total = this.total;
        return primarySeries(this.props.data).map((entry) => {
            const share = total ? (Math.max(entry.value, 0) / total) * 100 : 0;
            const color = getPaletteColor(this.props.config, entry.index);
            return {
                ...entry,
                formatted: this.formatValue(entry.value),
                percent: `${formatNumber(Math.round(share), "exact")}%`,
                swatchStyle: `background-color: ${color};`,
                segmentStyle: `flex-grow: ${share.toFixed(2)}; background-color: ${color};`,
                visible: share > 0,
            };
        });
    }
}
