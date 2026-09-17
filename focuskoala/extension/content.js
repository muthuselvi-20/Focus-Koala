/**
 * FocusKoala Content Script
 * Displays subtle on-screen warning banner when user approaches configured limit.
 */

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "show_warning") {
    showWarningBanner(request.message);
  }
});

function showWarningBanner(text) {
  let banner = document.getElementById("focuskoala-warning-banner");
  if (!banner) {
    banner = document.createElement("div");
    banner.id = "focuskoala-warning-banner";
    banner.style.cssText = `
      position: fixed;
      top: 18px;
      right: 18px;
      z-index: 2147483647;
      background: rgba(30, 27, 24, 0.95);
      color: #FFFFFF;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      padding: 12px 18px;
      border-radius: 12px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.3);
      border: 1px solid #E2A03F;
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 14px;
      font-weight: 500;
      transition: opacity 0.3s ease, transform 0.3s ease;
      animation: koalaSlideIn 0.3s ease-out;
    `;

    const styleEl = document.createElement("style");
    styleEl.textContent = `
      @keyframes koalaSlideIn {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
      }
    `;
    document.head.appendChild(styleEl);
    document.body.appendChild(banner);
  }

  banner.innerHTML = `
    <span style="font-size: 20px;">🐨</span>
    <div>
      <div style="color: #F8C162; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">FocusKoala Warning</div>
      <div>${text || "You have 5 minutes left."}</div>
    </div>
    <button id="focuskoala-close-btn" style="background: none; border: none; color: #999; cursor: pointer; font-size: 16px; margin-left: 8px;">✕</button>
  `;

  document.getElementById("focuskoala-close-btn").onclick = () => {
    banner.style.opacity = "0";
    setTimeout(() => banner.remove(), 300);
  };

  // Auto hide after 8 seconds
  clearTimeout(banner._hideTimer);
  banner._hideTimer = setTimeout(() => {
    if (banner) {
      banner.style.opacity = "0";
      setTimeout(() => banner.remove(), 300);
    }
  }, 8000);
}
