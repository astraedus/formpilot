"use strict";
// FormPilot content script — renders overlays and handles autofill
// --- Field Matcher (inlined to avoid module import issues in content scripts) ---
function normalize(s) {
    return s
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, "")
        .replace(/\s+/g, " ")
        .trim();
}
function similarity(a, b) {
    const na = normalize(a);
    const nb = normalize(b);
    if (!na || !nb)
        return 0;
    if (na === nb)
        return 1;
    if (na.includes(nb) || nb.includes(na))
        return 0.85;
    const wordsA = new Set(na.split(" "));
    const wordsB = new Set(nb.split(" "));
    const intersection = new Set([...wordsA].filter((w) => wordsB.has(w)));
    const union = new Set([...wordsA, ...wordsB]);
    if (union.size === 0)
        return 0;
    return intersection.size / union.size;
}
function matchFields(analysisFields, domFields) {
    const matched = [];
    const usedDomIndices = new Set();
    for (const af of analysisFields) {
        let bestScore = 0;
        let bestIndex = -1;
        for (let i = 0; i < domFields.length; i++) {
            if (usedDomIndices.has(i))
                continue;
            const df = domFields[i];
            const labelScore = similarity(af.field_name, df.label) * 1.0;
            const nameScore = similarity(af.field_name, df.name) * 0.8;
            const idScore = similarity(af.field_name, df.id) * 0.7;
            const placeholderScore = similarity(af.field_name, df.placeholder) * 0.6;
            const score = Math.max(labelScore, nameScore, idScore, placeholderScore);
            if (score > bestScore) {
                bestScore = score;
                bestIndex = i;
            }
        }
        if (bestIndex >= 0 && bestScore >= 0.3) {
            usedDomIndices.add(bestIndex);
            matched.push({
                analysis: af,
                domField: domFields[bestIndex],
                domIndex: bestIndex,
                score: bestScore,
            });
        }
    }
    return matched;
}
// --- Overlay rendering ---
let shadowHost = null;
let shadowRoot = null;
let currentMatches = [];
let activeTooltip = null;
function getOrCreateShadowRoot() {
    if (shadowRoot)
        return shadowRoot;
    shadowHost = document.createElement("div");
    shadowHost.id = "formpilot-root";
    shadowHost.style.cssText =
        "position: absolute; top: 0; left: 0; width: 0; height: 0; z-index: 2147483647; pointer-events: none;";
    document.body.appendChild(shadowHost);
    shadowRoot = shadowHost.attachShadow({ mode: "open" });
    const style = document.createElement("style");
    style.textContent = `
    * { box-sizing: border-box; margin: 0; padding: 0; }

    .fp-circle {
      position: absolute;
      width: 24px;
      height: 24px;
      background: #2563eb;
      color: #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 700;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      cursor: pointer;
      pointer-events: auto;
      box-shadow: 0 2px 8px rgba(37, 99, 235, 0.4);
      transition: transform 0.15s, box-shadow 0.15s;
      z-index: 2147483646;
    }

    .fp-circle:hover {
      transform: scale(1.15);
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.6);
    }

    .fp-circle.has-warning {
      background: #f59e0b;
      box-shadow: 0 2px 8px rgba(245, 158, 11, 0.4);
    }

    .fp-tooltip {
      position: absolute;
      width: 320px;
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.05);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      pointer-events: auto;
      z-index: 2147483647;
      overflow: hidden;
      animation: fp-fade-in 0.15s ease-out;
    }

    @keyframes fp-fade-in {
      from { opacity: 0; transform: translateY(-4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .fp-tooltip-header {
      padding: 12px 16px;
      background: #2563eb;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .fp-tooltip-title {
      font-size: 14px;
      font-weight: 600;
    }

    .fp-tooltip-badge {
      font-size: 11px;
      background: rgba(255,255,255,0.2);
      padding: 2px 8px;
      border-radius: 12px;
    }

    .fp-tooltip-body {
      padding: 14px 16px;
    }

    .fp-suggested {
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      border-radius: 8px;
      padding: 10px 12px;
      margin-bottom: 10px;
    }

    .fp-suggested-label {
      font-size: 11px;
      font-weight: 600;
      color: #15803d;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
    }

    .fp-suggested-value {
      font-size: 14px;
      color: #166534;
      font-weight: 500;
      word-break: break-word;
    }

    .fp-instructions {
      font-size: 13px;
      color: #374151;
      line-height: 1.5;
      margin-bottom: 10px;
    }

    .fp-warning {
      background: #fffbeb;
      border: 1px solid #fde68a;
      border-radius: 8px;
      padding: 8px 12px;
      font-size: 12px;
      color: #92400e;
      margin-bottom: 10px;
    }

    .fp-warning::before {
      content: "\\26A0\\FE0F ";
    }

    .fp-fill-btn {
      width: 100%;
      padding: 8px 16px;
      background: #2563eb;
      color: #fff;
      border: none;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.15s;
      font-family: inherit;
    }

    .fp-fill-btn:hover {
      background: #1d4ed8;
    }

    .fp-close-btn {
      background: none;
      border: none;
      color: rgba(255,255,255,0.8);
      cursor: pointer;
      font-size: 18px;
      padding: 0 4px;
      line-height: 1;
      font-family: inherit;
    }

    .fp-close-btn:hover {
      color: #fff;
    }

    .fp-action-bar {
      position: fixed;
      bottom: 20px;
      right: 20px;
      display: flex;
      gap: 8px;
      align-items: center;
      pointer-events: auto;
      z-index: 2147483647;
    }

    .fp-action-btn {
      padding: 10px 20px;
      border-radius: 24px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      border: none;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
      transition: transform 0.15s, box-shadow 0.15s;
    }

    .fp-action-btn:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
    }

    .fp-autofill-btn {
      background: #2563eb;
      color: #fff;
    }

    .fp-clear-btn {
      background: #fff;
      color: #374151;
      border: 1px solid #d1d5db;
    }

    .fp-field-count {
      background: #f0fdf4;
      color: #15803d;
      padding: 8px 14px;
      border-radius: 24px;
      font-size: 13px;
      font-weight: 600;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1);
    }
  `;
    shadowRoot.appendChild(style);
    return shadowRoot;
}
function findDomElement(domField) {
    // Try by id first
    if (domField.id) {
        const el = document.getElementById(domField.id);
        if (el)
            return el;
    }
    // Try by name
    if (domField.name) {
        const el = document.querySelector(`[name="${CSS.escape(domField.name)}"]`);
        if (el)
            return el;
    }
    // Fallback: find by position (closest element to stored rect)
    const elements = document.querySelectorAll("input, select, textarea, [contenteditable=true]");
    let bestEl = null;
    let bestDist = Infinity;
    elements.forEach((el) => {
        const rect = el.getBoundingClientRect();
        const dx = rect.left + window.scrollX - domField.rect.left;
        const dy = rect.top + window.scrollY - domField.rect.top;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < bestDist && dist < 50) {
            bestDist = dist;
            bestEl = el;
        }
    });
    return bestEl;
}
function setFieldValue(el, value) {
    const tagName = el.tagName.toLowerCase();
    const input = el;
    if (tagName === "select") {
        const select = el;
        // Find matching option by text or value
        const options = Array.from(select.options);
        const match = options.find((o) => o.value.toLowerCase() === value.toLowerCase() ||
            o.text.toLowerCase().includes(value.toLowerCase()) ||
            value.toLowerCase().includes(o.text.toLowerCase()));
        if (match) {
            select.value = match.value;
        }
        select.dispatchEvent(new Event("change", { bubbles: true }));
        return;
    }
    if (input.type === "checkbox" || input.type === "radio") {
        const shouldCheck = value.toLowerCase() === "true" ||
            value.toLowerCase() === "yes" ||
            value === "1";
        input.checked = shouldCheck;
        input.dispatchEvent(new Event("change", { bubbles: true }));
        return;
    }
    // Text-like inputs — use native setter to work with React/Angular/Vue
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
    const nativeTextareaValueSetter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, "value")?.set;
    if (tagName === "textarea" && nativeTextareaValueSetter) {
        nativeTextareaValueSetter.call(el, value);
    }
    else if (nativeInputValueSetter) {
        nativeInputValueSetter.call(el, value);
    }
    else {
        input.value = value;
    }
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
    el.dispatchEvent(new Event("blur", { bubbles: true }));
}
function dismissTooltip() {
    if (activeTooltip && shadowRoot) {
        activeTooltip.remove();
        activeTooltip = null;
    }
}
function showTooltip(match, circleEl) {
    dismissTooltip();
    const root = getOrCreateShadowRoot();
    const tooltip = document.createElement("div");
    tooltip.className = "fp-tooltip";
    // Position near the circle
    const circleRect = circleEl.getBoundingClientRect();
    let tooltipLeft = circleRect.right + window.scrollX + 8;
    let tooltipTop = circleRect.top + window.scrollY - 10;
    // Keep tooltip on screen
    if (tooltipLeft + 340 > window.innerWidth + window.scrollX) {
        tooltipLeft = circleRect.left + window.scrollX - 330;
    }
    if (tooltipTop + 300 > window.innerHeight + window.scrollY) {
        tooltipTop = window.innerHeight + window.scrollY - 310;
    }
    tooltip.style.left = tooltipLeft + "px";
    tooltip.style.top = tooltipTop + "px";
    const { analysis } = match;
    let html = `
    <div class="fp-tooltip-header">
      <span class="fp-tooltip-title">${escapeHtml(analysis.field_name)}</span>
      <span class="fp-tooltip-badge">${escapeHtml(analysis.field_type)}</span>
      <button class="fp-close-btn" data-action="close">&times;</button>
    </div>
    <div class="fp-tooltip-body">
  `;
    if (analysis.suggested_value) {
        html += `
      <div class="fp-suggested">
        <div class="fp-suggested-label">Suggested Value</div>
        <div class="fp-suggested-value">${escapeHtml(analysis.suggested_value)}</div>
      </div>
    `;
    }
    html += `<div class="fp-instructions">${escapeHtml(analysis.instructions)}</div>`;
    if (analysis.warning) {
        html += `<div class="fp-warning">${escapeHtml(analysis.warning)}</div>`;
    }
    if (analysis.suggested_value) {
        html += `<button class="fp-fill-btn" data-action="fill">Fill this field</button>`;
    }
    html += `</div>`;
    tooltip.innerHTML = html;
    // Event handlers
    tooltip.querySelector('[data-action="close"]')?.addEventListener("click", dismissTooltip);
    tooltip.querySelector('[data-action="fill"]')?.addEventListener("click", () => {
        const el = findDomElement(match.domField);
        if (el && analysis.suggested_value) {
            setFieldValue(el, analysis.suggested_value);
            // Flash the field green briefly
            el.style.transition = "background-color 0.3s";
            el.style.backgroundColor = "#dcfce7";
            setTimeout(() => {
                el.style.backgroundColor = "";
            }, 1000);
        }
        dismissTooltip();
    });
    root.appendChild(tooltip);
    activeTooltip = tooltip;
}
function escapeHtml(s) {
    const div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
}
function renderOverlays(matches) {
    clearOverlays();
    currentMatches = matches;
    const root = getOrCreateShadowRoot();
    matches.forEach((match, i) => {
        const el = findDomElement(match.domField);
        if (!el)
            return;
        const rect = el.getBoundingClientRect();
        const circle = document.createElement("div");
        circle.className = "fp-circle" + (match.analysis.warning ? " has-warning" : "");
        circle.textContent = String(i + 1);
        circle.style.left = rect.right + window.scrollX - 12 + "px";
        circle.style.top = rect.top + window.scrollY - 12 + "px";
        circle.addEventListener("click", (e) => {
            e.stopPropagation();
            showTooltip(match, circle);
        });
        root.appendChild(circle);
    });
    // Action bar
    const bar = document.createElement("div");
    bar.className = "fp-action-bar";
    bar.innerHTML = `
    <span class="fp-field-count">${matches.length} fields</span>
    <button class="fp-action-btn fp-autofill-btn" data-action="autofill-all">Autofill All</button>
    <button class="fp-action-btn fp-clear-btn" data-action="clear-all">Clear</button>
  `;
    bar.querySelector('[data-action="autofill-all"]')?.addEventListener("click", () => {
        autofillAll();
    });
    bar.querySelector('[data-action="clear-all"]')?.addEventListener("click", () => {
        clearOverlays();
    });
    root.appendChild(bar);
    // Dismiss tooltip on outside click
    document.addEventListener("click", () => {
        dismissTooltip();
    }, { once: false });
    // Reposition on scroll/resize
    const repositionHandler = throttle(() => {
        repositionCircles();
    }, 100);
    window.addEventListener("scroll", repositionHandler);
    window.addEventListener("resize", repositionHandler);
}
function repositionCircles() {
    if (!shadowRoot)
        return;
    const circles = shadowRoot.querySelectorAll(".fp-circle");
    circles.forEach((circle, i) => {
        if (i >= currentMatches.length)
            return;
        const match = currentMatches[i];
        const el = findDomElement(match.domField);
        if (!el)
            return;
        const rect = el.getBoundingClientRect();
        circle.style.left = rect.right + window.scrollX - 12 + "px";
        circle.style.top = rect.top + window.scrollY - 12 + "px";
    });
}
function throttle(fn, ms) {
    let timer = null;
    return () => {
        if (timer)
            return;
        timer = setTimeout(() => {
            fn();
            timer = null;
        }, ms);
    };
}
function autofillAll() {
    let filled = 0;
    currentMatches.forEach((match) => {
        if (!match.analysis.suggested_value)
            return;
        const el = findDomElement(match.domField);
        if (!el)
            return;
        setFieldValue(el, match.analysis.suggested_value);
        filled++;
        // Flash green
        el.style.transition = "background-color 0.3s";
        el.style.backgroundColor = "#dcfce7";
        setTimeout(() => {
            el.style.backgroundColor = "";
        }, 1500);
    });
    console.log(`FormPilot: Autofilled ${filled} fields`);
}
function clearOverlays() {
    dismissTooltip();
    if (shadowHost) {
        shadowHost.remove();
        shadowHost = null;
        shadowRoot = null;
    }
    currentMatches = [];
}
// --- Message listener ---
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg.action === "showOverlays") {
        const matches = matchFields(msg.fields, msg.domFields);
        renderOverlays(matches);
        sendResponse({ matched: matches.length });
    }
    else if (msg.action === "autofillAll") {
        autofillAll();
        sendResponse({ ok: true });
    }
    else if (msg.action === "clearOverlays") {
        clearOverlays();
        sendResponse({ ok: true });
    }
    return true;
});
