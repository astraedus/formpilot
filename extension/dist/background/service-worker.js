"use strict";
// FormPilot service worker — handles message routing
// The popup handles screenshot capture and API calls directly via chrome.tabs APIs
// This service worker handles any background messaging if needed
chrome.runtime.onInstalled.addListener(() => {
    console.log("FormPilot extension installed");
});
