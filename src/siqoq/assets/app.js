/* Shared DOM helpers + header wiring for the siqoq dashboard (/) and guide
 * (/guide) pages. Served as a static asset at /assets/app.js (see ui.py's
 * route allowlist). Depends on SiqoqI18n from /assets/i18n.js, which must be
 * loaded first.
 *
 * DOM is built only through el()/clear() with textContent, never innerHTML
 * with data, so nothing served here can turn snapshot data into markup.
 */
(function (global) {
  "use strict";

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (key) {
        if (key === "class") node.className = attrs[key];
        else if (key === "text") node.textContent = attrs[key];
        else node.setAttribute(key, attrs[key]);
      });
    }
    (children || []).forEach(function (child) {
      if (child) node.appendChild(child);
    });
    return node;
  }

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function setBody(id, node) {
    var container = document.getElementById(id);
    clear(container);
    container.appendChild(node);
  }

  function truncate(text, max) {
    if (text.length <= max) return text;
    return text.slice(0, max - 1) + "…";
  }

  function statusBox(message, opts) {
    opts = opts || {};
    var t = global.SiqoqI18n.t;
    var children = [el("p", { text: message })];
    if (opts.hint) {
      var hint = el("p", { style: "margin:0.4rem 0 0;" });
      hint.appendChild(document.createTextNode(t("common.enableWith")));
      hint.appendChild(el("code", { text: opts.hint }));
      children.push(hint);
    }
    if (opts.retry) {
      var btn = el("button", { type: "button", text: t("common.retry") });
      btn.addEventListener("click", opts.retry);
      children.push(btn);
    }
    var classes = "status" + (opts.error ? " is-error" : "");
    return el("div", { class: classes }, children);
  }

  // Wires the language toggle buttons and keeps their pressed/active state
  // in sync, including when another tab or the ?lang= bootstrap changes it.
  function initLangToggle() {
    var buttons = document.querySelectorAll(".lang-btn");
    function sync() {
      var lang = global.SiqoqI18n.getLang();
      buttons.forEach(function (btn) {
        var isActive = btn.getAttribute("data-lang") === lang;
        btn.classList.toggle("is-active", isActive);
        btn.setAttribute("aria-pressed", isActive ? "true" : "false");
      });
    }
    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        global.SiqoqI18n.setLang(btn.getAttribute("data-lang"));
      });
    });
    document.addEventListener("siqoq:lang-changed", sync);
    sync();
  }

  // Wires every ".info-toggle" button to show/hide the "info-body" element
  // it names via aria-controls, and keeps aria-expanded in sync.
  function initInfoToggles() {
    document.querySelectorAll(".info-toggle").forEach(function (btn) {
      var target = document.getElementById(btn.getAttribute("aria-controls"));
      if (!target) return;
      btn.addEventListener("click", function () {
        var expanded = btn.getAttribute("aria-expanded") === "true";
        btn.setAttribute("aria-expanded", expanded ? "false" : "true");
        target.hidden = expanded;
      });
    });
  }

  function initHeader() {
    global.SiqoqI18n.applyStaticI18n();
    initLangToggle();
    initInfoToggles();
  }

  global.SiqoqApp = {
    el: el,
    clear: clear,
    setBody: setBody,
    truncate: truncate,
    statusBox: statusBox,
    initHeader: initHeader
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initHeader);
  } else {
    initHeader();
  }
})(window);
