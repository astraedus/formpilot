"use strict";
// FormPilot popup — orchestrates analyze flow
const API_URL = "https://formpilot-api-93135657352.us-central1.run.app";
function show(id) {
    document.querySelectorAll(".state").forEach((el) => el.classList.add("hidden"));
    document.getElementById(id)?.classList.remove("hidden");
}
async function getCurrentTab() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    return tab;
}
async function captureScreenshot() {
    const dataUrl = await chrome.tabs.captureVisibleTab(undefined, {
        format: "png",
    });
    return dataUrl;
}
async function extractFields(tabId) {
    const results = await chrome.scripting.executeScript({
        target: { tabId },
        func: () => {
            const fields = [];
            const elements = document.querySelectorAll("input, select, textarea, [contenteditable=true]");
            elements.forEach((el) => {
                const htmlEl = el;
                const input = el;
                // Skip hidden/invisible fields
                const style = window.getComputedStyle(htmlEl);
                if (style.display === "none" ||
                    style.visibility === "hidden" ||
                    input.type === "hidden")
                    return;
                // Find label
                let label = "";
                if (input.id) {
                    const labelEl = document.querySelector(`label[for="${input.id}"]`);
                    if (labelEl)
                        label = labelEl.textContent?.trim() || "";
                }
                if (!label) {
                    const parent = htmlEl.closest("label");
                    if (parent) {
                        label = parent.textContent?.trim() || "";
                        // Remove the input's own value from label text
                        if (input.value)
                            label = label.replace(input.value, "").trim();
                    }
                }
                if (!label)
                    label = input.getAttribute("aria-label") || "";
                if (!label)
                    label = input.placeholder || "";
                if (!label)
                    label = input.name || "";
                const rect = htmlEl.getBoundingClientRect();
                fields.push({
                    label,
                    name: input.name || "",
                    id: input.id || "",
                    type: input.type || htmlEl.tagName.toLowerCase(),
                    tagName: htmlEl.tagName.toLowerCase(),
                    placeholder: input.placeholder || "",
                    value: input.value || "",
                    rect: {
                        top: rect.top + window.scrollY,
                        left: rect.left + window.scrollX,
                        width: rect.width,
                        height: rect.height,
                    },
                });
            });
            return fields;
        },
    });
    return results[0]?.result || [];
}
function dataUrlToBlob(dataUrl) {
    const parts = dataUrl.split(",");
    const mime = parts[0].match(/:(.*?);/)?.[1] || "image/png";
    const binary = atob(parts[1]);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return new Blob([bytes], { type: mime });
}
async function analyzeForm(screenshot, userContext, domFields) {
    // Build enriched context with DOM field metadata
    const fieldSummary = domFields
        .map((f, i) => `[${i}] label="${f.label}" name="${f.name}" id="${f.id}" type="${f.type}" placeholder="${f.placeholder}"`)
        .join("\n");
    const enrichedContext = `${userContext}\n\nDOM_FIELDS:\n${fieldSummary}`;
    const blob = dataUrlToBlob(screenshot);
    const formData = new FormData();
    formData.append("file", blob, "screenshot.png");
    formData.append("user_context", enrichedContext);
    const resp = await fetch(`${API_URL}/api/analyze`, {
        method: "POST",
        body: formData,
    });
    if (!resp.ok) {
        const text = await resp.text();
        throw new Error(`API error ${resp.status}: ${text}`);
    }
    return resp.json();
}
async function sendToContentScript(tabId, action, data) {
    return chrome.tabs.sendMessage(tabId, { action, ...data });
}
// --- Main flow ---
document.addEventListener("DOMContentLoaded", () => {
    const analyzeBtn = document.getElementById("analyze-btn");
    const autofillBtn = document.getElementById("autofill-btn");
    const clearBtn = document.getElementById("clear-btn");
    const reanalyzeBtn = document.getElementById("reanalyze-btn");
    const retryBtn = document.getElementById("retry-btn");
    const contextInput = document.getElementById("context-input");
    const fieldCountEl = document.getElementById("field-count");
    const errorMessageEl = document.getElementById("error-message");
    let currentTabId;
    let lastAnalysis;
    // Restore saved context
    chrome.storage?.local?.get(["userContext"], (result) => {
        if (result.userContext)
            contextInput.value = result.userContext;
    });
    analyzeBtn.addEventListener("click", async () => {
        const userContext = contextInput.value.trim();
        // Save context for next time
        chrome.storage?.local?.set({ userContext });
        show("state-loading");
        try {
            const tab = await getCurrentTab();
            if (!tab.id)
                throw new Error("No active tab");
            currentTabId = tab.id;
            // Capture screenshot
            const loadingSub = document.querySelector(".loading-sub");
            loadingSub.textContent = "Capturing page screenshot...";
            const screenshot = await captureScreenshot();
            // Extract DOM fields
            loadingSub.textContent = "Extracting form fields...";
            const domFields = await extractFields(currentTabId);
            if (domFields.length === 0) {
                throw new Error("No form fields detected on this page. Navigate to a page with a form and try again.");
            }
            // Call API
            loadingSub.textContent = `Analyzing ${domFields.length} fields with AI...`;
            const analysis = await analyzeForm(screenshot, userContext, domFields);
            lastAnalysis = analysis;
            // Send results to content script for overlay rendering
            await sendToContentScript(currentTabId, "showOverlays", {
                fields: analysis.fields,
                domFields,
            });
            fieldCountEl.textContent = String(analysis.fields.length);
            show("state-success");
        }
        catch (err) {
            errorMessageEl.textContent = err.message || "Analysis failed";
            show("state-error");
        }
    });
    autofillBtn.addEventListener("click", async () => {
        if (!currentTabId || !lastAnalysis)
            return;
        await sendToContentScript(currentTabId, "autofillAll");
    });
    clearBtn.addEventListener("click", async () => {
        if (!currentTabId)
            return;
        await sendToContentScript(currentTabId, "clearOverlays");
        show("state-idle");
    });
    reanalyzeBtn.addEventListener("click", () => {
        show("state-idle");
    });
    retryBtn.addEventListener("click", () => {
        show("state-idle");
    });
});
