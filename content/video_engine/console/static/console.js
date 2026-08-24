/* Triage keyboard layer.
 *
 * Keys are shortcuts to controls that already exist on the page — every action
 * is reachable by a visible button or link, so the tool is keyboard-complete
 * rather than keyboard-only. No framework: the server renders state, keys
 * click it.
 */
(function () {
  "use strict";

  var nav = document.getElementById("nav-data");
  if (!nav) return;

  var selected = document.getElementById("strip-selected");
  if (selected && selected.scrollIntoView) {
    // The focused row must be fully visible, not half behind an edge.
    selected.scrollIntoView({ block: "nearest" });
  }

  function go(url) {
    if (url) window.location.assign(url);
  }
  function submit(id) {
    var form = document.getElementById(id);
    if (form) {
      var button = form.querySelector("button");
      if (button && button.disabled) return; // a failed asset cannot be promoted
      form.submit();
    }
  }

  document.addEventListener("keydown", function (event) {
    if (event.target && /^(INPUT|TEXTAREA|SELECT)$/.test(event.target.tagName)) return;
    if (event.ctrlKey || event.altKey || event.metaKey) return;

    switch (event.key) {
      case "j": case "J": go(nav.dataset.next); break;
      case "k": case "K": go(nav.dataset.prev); break;
      case "1": submit("form-promote"); break;
      case "0": submit("form-reject"); break;
      case ".": submit("form-skip"); break;
      case " ":
        if (nav.dataset.compositable) { event.preventDefault(); go(nav.dataset.toggle); }
        break;
      case "c": case "C":
        if (nav.dataset.compositable) go(nav.dataset.cycle);
        break;
      // Ground is a link, not client state: it survives a reload, a shared URL
      // and a browser with scripting off, like every other control here.
      case "g": case "G": go(nav.dataset.ground); break;
      case "g": case "G": go(nav.dataset.ground); break;
      case "Enter": {
        var commit = document.getElementById("commit-link");
        if (commit) go(commit.getAttribute("href"));
        break;
      }
      default: return;
    }
  });
})();
