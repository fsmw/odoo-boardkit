// Copyright 2026 SMWLAB
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

// Font Awesome 4 names stored on existing items, mapped to their Phosphor
// equivalent. The Clean style renders the Phosphor icon, so boards created
// before Phosphor was available upgrade without touching their data. Names
// missing here keep rendering with Font Awesome.
import {loadBundle} from "@web/core/assets";

export const FA_TO_PHOSPHOR = {
    "fa-archive": "ph-archive",
    "fa-area-chart": "ph-chart-line",
    "fa-arrows-h": "ph-arrows-horizontal",
    "fa-balance-scale": "ph-scales",
    "fa-ban": "ph-prohibit",
    "fa-bank": "ph-bank",
    "fa-bar-chart": "ph-chart-bar",
    "fa-bar-chart-o": "ph-chart-bar",
    "fa-barcode": "ph-barcode",
    "fa-bell": "ph-bell",
    "fa-bell-o": "ph-bell",
    "fa-bolt": "ph-lightning",
    "fa-book": "ph-book",
    "fa-bookmark": "ph-bookmark",
    "fa-briefcase": "ph-briefcase",
    "fa-bug": "ph-bug",
    "fa-building": "ph-buildings",
    "fa-building-o": "ph-buildings",
    "fa-bullseye": "ph-target",
    "fa-calculator": "ph-calculator",
    "fa-calendar": "ph-calendar-blank",
    "fa-calendar-check-o": "ph-calendar-check",
    "fa-calendar-o": "ph-calendar-blank",
    "fa-calendar-times-o": "ph-calendar-x",
    "fa-camera": "ph-camera",
    "fa-car": "ph-car",
    "fa-check": "ph-check",
    "fa-check-circle": "ph-check-circle",
    "fa-check-square-o": "ph-check-square",
    "fa-clipboard": "ph-clipboard-text",
    "fa-clock-o": "ph-clock",
    "fa-clone": "ph-copy",
    "fa-cloud": "ph-cloud",
    "fa-code": "ph-code",
    "fa-cog": "ph-gear",
    "fa-cogs": "ph-gear-six",
    "fa-comment": "ph-chat-circle",
    "fa-comment-o": "ph-chat-circle",
    "fa-comments": "ph-chats-circle",
    "fa-comments-o": "ph-chats-circle",
    "fa-credit-card": "ph-credit-card",
    "fa-cube": "ph-cube",
    "fa-cubes": "ph-cube",
    "fa-database": "ph-database",
    "fa-dollar": "ph-currency-dollar",
    "fa-download": "ph-download-simple",
    "fa-envelope": "ph-envelope",
    "fa-envelope-o": "ph-envelope-simple",
    "fa-exchange": "ph-arrows-left-right",
    "fa-exclamation-triangle": "ph-warning",
    "fa-eye": "ph-eye",
    "fa-file": "ph-file",
    "fa-file-o": "ph-file",
    "fa-file-text": "ph-file-text",
    "fa-file-text-o": "ph-file-text",
    "fa-files-o": "ph-files",
    "fa-filter": "ph-funnel",
    "fa-flag": "ph-flag",
    "fa-flag-checkered": "ph-flag-checkered",
    "fa-folder": "ph-folder",
    "fa-folder-open": "ph-folder-open",
    "fa-gavel": "ph-gavel",
    "fa-gift": "ph-gift",
    "fa-globe": "ph-globe",
    "fa-graduation-cap": "ph-graduation-cap",
    "fa-handshake-o": "ph-handshake",
    "fa-headphones": "ph-headphones",
    "fa-heart": "ph-heart",
    "fa-heart-o": "ph-heart",
    "fa-home": "ph-house",
    "fa-hourglass-end": "ph-hourglass-low",
    "fa-hourglass-half": "ph-hourglass-medium",
    "fa-id-card-o": "ph-identification-card",
    "fa-image": "ph-image",
    "fa-inbox": "ph-tray",
    "fa-industry": "ph-factory",
    "fa-info-circle": "ph-info",
    "fa-key": "ph-key",
    "fa-leaf": "ph-leaf",
    "fa-life-ring": "ph-lifebuoy",
    "fa-line-chart": "ph-chart-line-up",
    "fa-list": "ph-list-bullets",
    "fa-list-alt": "ph-list-dashes",
    "fa-lock": "ph-lock",
    "fa-map-marker": "ph-map-pin",
    "fa-medkit": "ph-first-aid-kit",
    "fa-microphone": "ph-microphone",
    "fa-money": "ph-money",
    "fa-paper-plane": "ph-paper-plane-tilt",
    "fa-pencil": "ph-pencil-simple",
    "fa-pencil-square-o": "ph-note-pencil",
    "fa-percent": "ph-percent",
    "fa-phone": "ph-phone",
    "fa-pie-chart": "ph-chart-pie",
    "fa-plane": "ph-airplane",
    "fa-play-circle": "ph-play-circle",
    "fa-plus-circle": "ph-plus-circle",
    "fa-plus-square": "ph-plus-square",
    "fa-print": "ph-printer",
    "fa-qrcode": "ph-qr-code",
    "fa-question-circle": "ph-question",
    "fa-refresh": "ph-arrows-clockwise",
    "fa-reply": "ph-arrow-bend-up-left",
    "fa-rocket": "ph-rocket",
    "fa-search": "ph-magnifying-glass",
    "fa-shield": "ph-shield",
    "fa-ship": "ph-boat",
    "fa-shopping-basket": "ph-basket",
    "fa-shopping-cart": "ph-shopping-cart",
    "fa-sign-in": "ph-sign-in",
    "fa-sign-out": "ph-sign-out",
    "fa-sitemap": "ph-tree-structure",
    "fa-spinner": "ph-spinner",
    "fa-star": "ph-star",
    "fa-star-o": "ph-star",
    "fa-suitcase": "ph-suitcase",
    "fa-tachometer": "ph-gauge",
    "fa-tag": "ph-tag",
    "fa-tags": "ph-tag",
    "fa-tasks": "ph-list-checks",
    "fa-th-large": "ph-squares-four",
    "fa-thumbs-up": "ph-thumbs-up",
    "fa-ticket": "ph-ticket",
    "fa-times": "ph-x",
    "fa-times-circle": "ph-x-circle",
    "fa-trophy": "ph-trophy",
    "fa-truck": "ph-truck",
    "fa-undo": "ph-arrow-counter-clockwise",
    "fa-university": "ph-bank",
    "fa-usd": "ph-currency-dollar",
    "fa-user": "ph-user",
    "fa-user-o": "ph-user",
    "fa-user-plus": "ph-user-plus",
    "fa-user-secret": "ph-detective",
    "fa-user-times": "ph-user-minus",
    "fa-users": "ph-users",
    "fa-wrench": "ph-wrench",
};

const PHOSPHOR_PREFIX = "ph-";
const PHOSPHOR_WEIGHT_CLASS = "ph-duotone";
const DEFAULT_ICON = "fa-bar-chart";

/**
 * Resolve the CSS classes that draw ``icon``.
 *
 * @param {String} icon stored icon name (``fa-*`` or ``ph-*``)
 * @param {Boolean} preferPhosphor translate known Font Awesome names
 * @returns {{className: String, phosphor: Boolean}}
 */
export function resolveIcon(icon, preferPhosphor) {
    const name = icon || DEFAULT_ICON;
    const phosphorName = name.startsWith(PHOSPHOR_PREFIX)
        ? name
        : preferPhosphor && FA_TO_PHOSPHOR[name];
    if (phosphorName) {
        return {className: `${PHOSPHOR_WEIGHT_CLASS} ${phosphorName}`, phosphor: true};
    }
    return {className: `fa ${name}`, phosphor: false};
}

let phosphorBundle = null;

/** Load the Phosphor font once; later calls share the same promise. */
export function ensurePhosphor() {
    if (!phosphorBundle) {
        phosphorBundle = loadBundle("boardkit_dashboard.phosphor").catch((error) => {
            // A failed download must not break the card: icons fall back to
            // empty glyphs and the next render retries.
            phosphorBundle = null;
            console.warn("Boardkit: Phosphor icons could not be loaded", error);
        });
    }
    return phosphorBundle;
}
