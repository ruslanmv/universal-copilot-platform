(function () {
  function mountWidget() {
    var el = document.getElementById("ucp-support-chat");
    if (!el) return;

    // Assume you bundle SupportChat via a UMD build or expose window.SupportChat
    const apiBaseUrl = el.getAttribute("data-api-base-url");
    const tenantId = el.getAttribute("data-tenant-id");

    window.UCP_SUPPORT_CHAT.mount(el, {
      apiBaseUrl,
      tenantId,
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountWidget);
  } else {
    mountWidget();
  }
})();
