// Copyright 2026 SMWLAB
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import {hexToRGBA} from "./utils";

// Chart restyling for the Clean visual style: quiet axes, hairline grid,
// rounded marks and a card-like tooltip, so color is left to the data.

const PIE_LIKE = ["pie", "doughnut", "polar"];
const BAR_TYPES = ["bar", "bar_horizontal"];
const LINE_TYPES = ["line", "area"];
const RADIAL_SCALE_TYPES = ["polar", "radar"];

const FONT_SIZE = 12;
const MUTED_ALPHA = 0.62;
const GRID_ALPHA = 0.1;
const TOOLTIP_BORDER_ALPHA = 0.14;
const AREA_FILL_ALPHA = 0.14;
const MAX_BAR_THICKNESS = 44;
const BAR_RADIUS = 6;
const STACKED_BAR_RADIUS = 3;
const VALUE_TICKS_LIMIT = 5;
const DOUGHNUT_CUTOUT = "66%";
const FALLBACK_TEXT = "rgb(17, 24, 39)";
const FALLBACK_SURFACE = "#FFFFFF";

function withAlpha(rgbColor, alpha) {
    const channels = (rgbColor.match(/[\d.]+/g) || []).slice(0, 3);
    if (channels.length < 3) {
        return rgbColor;
    }
    return `rgba(${channels.join(", ")}, ${alpha})`;
}

/**
 * Resolve the colors of the card the canvas lives in, so charts follow the
 * card (neutral, manual color or dark mode) instead of hardcoded values.
 */
export function readChartTokens(canvas) {
    const style = canvas ? getComputedStyle(canvas) : null;
    const text = style?.color || FALLBACK_TEXT;
    return {
        text,
        muted: withAlpha(text, MUTED_ALPHA),
        grid: withAlpha(text, GRID_ALPHA),
        tooltipBorder: withAlpha(text, TOOLTIP_BORDER_ALPHA),
        surface: style?.getPropertyValue("--esc-card-bg").trim() || FALLBACK_SURFACE,
        fontFamily: style?.fontFamily || "sans-serif",
    };
}

function themeTooltip(plugins, tokens) {
    plugins.tooltip = {
        ...plugins.tooltip,
        backgroundColor: tokens.surface,
        titleColor: tokens.text,
        bodyColor: tokens.text,
        borderColor: tokens.tooltipBorder,
        borderWidth: 1,
        padding: 10,
        cornerRadius: 8,
        boxPadding: 4,
        usePointStyle: true,
    };
}

function themeLegend(plugins, itemType, seriesCount, tokens) {
    if (!plugins.legend) {
        return;
    }
    const cartesian = BAR_TYPES.includes(itemType) || LINE_TYPES.includes(itemType);
    // A lone series is already named by the card title.
    const redundant = cartesian && seriesCount < 2;
    plugins.legend = {
        ...plugins.legend,
        display: Boolean(plugins.legend.display) && !redundant,
        position: cartesian ? "top" : "bottom",
        align: cartesian ? "end" : "center",
        labels: {
            ...plugins.legend.labels,
            boxWidth: 8,
            boxHeight: 8,
            usePointStyle: true,
            pointStyle: "rectRounded",
            padding: 14,
            color: tokens.muted,
        },
    };
}

function categoryAxis(axis, tokens) {
    return {
        ...axis,
        grid: {display: false},
        border: {display: false},
        ticks: {
            maxRotation: 0,
            autoSkipPadding: 12,
            ...axis.ticks,
            color: tokens.muted,
        },
    };
}

function valueAxis(axis, tokens) {
    return {
        ...axis,
        grid: {color: tokens.grid, drawTicks: false},
        border: {display: false},
        ticks: {
            maxTicksLimit: VALUE_TICKS_LIMIT,
            padding: 8,
            ...axis.ticks,
            color: tokens.muted,
        },
    };
}

function themeScales(options, itemType, tokens) {
    if (RADIAL_SCALE_TYPES.includes(itemType)) {
        options.scales = {
            ...options.scales,
            r: {
                ...options.scales?.r,
                grid: {color: tokens.grid},
                angleLines: {color: tokens.grid},
                pointLabels: {color: tokens.muted},
                ticks: {display: false},
            },
        };
        return;
    }
    if (!options.scales?.x || !options.scales?.y) {
        return;
    }
    const horizontal = options.indexAxis === "y";
    const bothValues = itemType === "scatter";
    const xIsValue = bothValues || horizontal;
    const yIsValue = bothValues || !horizontal;
    options.scales.x = (xIsValue ? valueAxis : categoryAxis)(options.scales.x, tokens);
    options.scales.y = (yIsValue ? valueAxis : categoryAxis)(options.scales.y, tokens);
}

function themeDataset(dataset, itemType, stacked, tokens) {
    if (dataset.escOverlay) {
        return {...dataset, borderWidth: 1.5};
    }
    if (BAR_TYPES.includes(itemType)) {
        return {
            ...dataset,
            borderWidth: 0,
            borderRadius: stacked ? STACKED_BAR_RADIUS : BAR_RADIUS,
            maxBarThickness: MAX_BAR_THICKNESS,
        };
    }
    if (LINE_TYPES.includes(itemType)) {
        // A single point has no segment to draw, so it keeps a visible dot.
        const singlePoint = (dataset.data || []).length < 2;
        const themed = {
            ...dataset,
            borderWidth: 2,
            tension: 0.3,
            pointRadius: singlePoint ? 4 : 0,
            pointHoverRadius: 4,
            pointHitRadius: 12,
        };
        if (itemType === "area" && typeof dataset.borderColor === "string") {
            themed.backgroundColor = hexToRGBA(dataset.borderColor, AREA_FILL_ALPHA);
        }
        return themed;
    }
    if (PIE_LIKE.includes(itemType)) {
        return {
            ...dataset,
            borderColor: tokens.surface,
            borderWidth: 2,
            hoverOffset: 4,
        };
    }
    if (itemType === "radar") {
        return {...dataset, borderWidth: 2, pointRadius: 0, pointHoverRadius: 4};
    }
    return dataset;
}

/**
 * Return a restyled copy of a built Chart.js configuration.
 *
 * Only presentation changes: data, callbacks and click handlers built by the
 * renderer are preserved.
 */
export function applyCleanChartTheme(chartConfig, itemType, tokens) {
    const options = {...chartConfig.options};
    const plugins = {...options.plugins};
    options.font = {family: tokens.fontFamily, size: FONT_SIZE};
    options.color = tokens.muted;
    themeTooltip(plugins, tokens);
    const sourceDatasets = chartConfig.data?.datasets || [];
    themeLegend(plugins, itemType, sourceDatasets.length, tokens);
    if (plugins.boardkitGaugeCenter) {
        plugins.boardkitGaugeCenter = {
            ...plugins.boardkitGaugeCenter,
            color: tokens.text,
        };
    }
    options.plugins = plugins;
    if (options.scales) {
        options.scales = {...options.scales};
    }
    themeScales(options, itemType, tokens);
    if (LINE_TYPES.includes(itemType)) {
        options.interaction = {mode: "index", intersect: false};
    }
    if (itemType === "doughnut") {
        options.cutout = DOUGHNUT_CUTOUT;
    }
    const stacked = Boolean(options.scales?.x?.stacked);
    const datasets = sourceDatasets.map((dataset) =>
        themeDataset(dataset, itemType, stacked, tokens)
    );
    return {
        ...chartConfig,
        data: {...chartConfig.data, datasets},
        options,
    };
}
