/* TPSL site script — no third-party code, no tracking. */
(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.remove("no-js");

  function store(key, val) {
    try {
      if (val === undefined) return window.localStorage.getItem(key);
      if (val === null) window.localStorage.removeItem(key);
      else window.localStorage.setItem(key, val);
    } catch (e) { return null; }
  }

  /* ---------- Mobile navigation ---------- */
  var toggle = document.querySelector(".menu-toggle");
  var nav = document.getElementById("primary-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      document.body.classList.toggle("nav-open", open);
    });
  }

  /* ---------- Dropdowns ---------- */
  var subs = document.querySelectorAll(".has-sub");
  subs.forEach(function (li) {
    var btn = li.querySelector("button.nav-link");
    if (!btn) return;
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var isOpen = li.getAttribute("data-open") === "true";
      subs.forEach(function (o) { o.setAttribute("data-open", "false"); o.querySelector("button").setAttribute("aria-expanded", "false"); });
      li.setAttribute("data-open", isOpen ? "false" : "true");
      btn.setAttribute("aria-expanded", isOpen ? "false" : "true");
    });
  });
  document.addEventListener("click", function () {
    subs.forEach(function (o) { o.setAttribute("data-open", "false"); var b = o.querySelector("button"); if (b) b.setAttribute("aria-expanded", "false"); });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      subs.forEach(function (o) { o.setAttribute("data-open", "false"); });
      var p = document.querySelector(".a11y-panel.show"); if (p) p.classList.remove("show");
    }
  });

  /* ---------- Carousels ---------- */
  document.querySelectorAll(".carousel").forEach(function (c) {
    var track = c.querySelector(".carousel-track");
    var prev = c.querySelector("[data-dir='prev']");
    var next = c.querySelector("[data-dir='next']");
    function step() { var item = track.children[0]; return item ? item.getBoundingClientRect().width + 20 : 300; }
    if (prev) prev.addEventListener("click", function () { track.scrollBy({ left: -step(), behavior: "smooth" }); });
    if (next) next.addEventListener("click", function () { track.scrollBy({ left: step(), behavior: "smooth" }); });
  });

  /* ---------- Sub-nav active state ---------- */
  var subLinks = document.querySelectorAll(".subnav a[href^='#']");
  if (subLinks.length && "IntersectionObserver" in window) {
    var map = {};
    subLinks.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && map[en.target.id]) {
          subLinks.forEach(function (a) { a.classList.remove("active"); });
          map[en.target.id].classList.add("active");
        }
      });
    }, { rootMargin: "-40% 0px -55% 0px" });
    Object.keys(map).forEach(function (id) { var el = document.getElementById(id); if (el) io.observe(el); });
  }

  /* ---------- Reveal on scroll ---------- */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var ro = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); ro.unobserve(en.target); } });
    }, { threshold: 0.12 });
    reveals.forEach(function (el) { ro.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---------- Cookie notice (essential cookies only) ---------- */
  var banner = document.querySelector(".cookie-banner");
  if (banner && !store("tpsl_cookie_ack")) {
    banner.classList.add("show");
    var ack = banner.querySelector("[data-cookie-ack]");
    if (ack) ack.addEventListener("click", function () { store("tpsl_cookie_ack", "1"); banner.classList.remove("show"); });
  }

  /* ---------- Accessibility tools ---------- */
  var aBtn = document.querySelector(".a11y-btn");
  var aPanel = document.querySelector(".a11y-panel");
  var opts = { large: "a11y-large", contrast: "a11y-contrast", links: "a11y-links" };
  Object.keys(opts).forEach(function (k) { if (store("tpsl_" + k) === "1") doc.classList.add(opts[k]); });
  if (aBtn && aPanel) {
    aBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = aPanel.classList.toggle("show");
      aBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    aPanel.addEventListener("click", function (e) { e.stopPropagation(); });
    document.addEventListener("click", function () { aPanel.classList.remove("show"); aBtn.setAttribute("aria-expanded", "false"); });
    aPanel.querySelectorAll("button[data-a11y]").forEach(function (b) {
      var k = b.getAttribute("data-a11y");
      if (k === "reset") {
        b.addEventListener("click", function () {
          Object.keys(opts).forEach(function (o) { doc.classList.remove(opts[o]); store("tpsl_" + o, null); });
          aPanel.querySelectorAll("button[aria-pressed]").forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
        });
        return;
      }
      b.setAttribute("aria-pressed", doc.classList.contains(opts[k]) ? "true" : "false");
      b.addEventListener("click", function () {
        var on = doc.classList.toggle(opts[k]);
        b.setAttribute("aria-pressed", on ? "true" : "false");
        store("tpsl_" + k, on ? "1" : null);
      });
    });
  }

  /* ---------- Enquiry forms ---------- */
  var EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  var PHONE = /^[+]?[0-9][0-9\s-]{7,15}$/;
  document.querySelectorAll("form.enquiry-form").forEach(function (form) {
    var status = form.querySelector(".form-status");
    function setErr(field, bad) { var w = field.closest(".field"); if (w) w.classList.toggle("invalid", bad); field.setAttribute("aria-invalid", bad ? "true" : "false"); }
    function validate() {
      var ok = true;
      form.querySelectorAll("[required]").forEach(function (f) {
        var v = (f.type === "checkbox") ? f.checked : f.value.trim();
        var bad = !v;
        if (!bad && f.type === "email") bad = !EMAIL.test(f.value.trim());
        if (!bad && f.type === "tel") bad = !PHONE.test(f.value.trim());
        if (f.type !== "checkbox") setErr(f, bad);
        if (bad) ok = false;
      });
      var consent = form.querySelector("input[name='consent']");
      if (consent && !consent.checked) { ok = false; consent.closest(".consent").classList.add("invalid"); }
      return ok;
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      status.className = "form-status";
      status.textContent = "";
      if (!validate()) {
        status.className = "form-status err";
        status.textContent = "Please complete the highlighted fields and accept the Privacy Policy to continue.";
        var first = form.querySelector(".invalid input, .invalid select, .invalid textarea");
        if (first) first.focus();
        return;
      }
      var btn = form.querySelector("button[type='submit']");
      btn.disabled = true; var label = btn.textContent; btn.textContent = "Submitting…";
      fetch(form.getAttribute("action"), {
        method: "POST",
        body: new FormData(form),
        headers: { "Accept": "application/json", "X-Requested-With": "fetch" },
        credentials: "same-origin"
      }).then(function (r) { return r.json().catch(function () { return { ok: r.ok }; }); })
        .then(function (data) {
          if (data && data.ok) {
            form.reset();
            status.className = "form-status ok";
            status.textContent = "Thank you. Your enquiry has been received and our team will get in touch with you shortly.";
          } else {
            status.className = "form-status err";
            status.textContent = (data && data.message) || "We could not submit your enquiry right now. Please try again or write to us directly.";
          }
        })
        .catch(function () {
          status.className = "form-status err";
          status.textContent = "We could not submit your enquiry right now. Please try again or write to us directly.";
        })
        .finally(function () { btn.disabled = false; btn.textContent = label; });
    });
    form.querySelectorAll("input, select, textarea").forEach(function (f) {
      f.addEventListener("input", function () { var w = f.closest(".field, .consent"); if (w) w.classList.remove("invalid"); });
    });
  });

  /* ---------- Pre-select enquiry type from ?enquiry= ---------- */
  try {
    var q = new URLSearchParams(window.location.search).get("enquiry");
    var groupsMap = { pos: 0, softpos: 0, soundbox: 0, gateway: 1, recurring: 1, links: 1, hub: 2, onboarding: 2, dcc: 2, upi: 2, transit: 2, embedded: 2 };
    if (q && Object.prototype.hasOwnProperty.call(groupsMap, q)) {
      document.querySelectorAll("select[name='enquiry_type']").forEach(function (sel) { sel.selectedIndex = groupsMap[q] + 1; });
    }
  } catch (e) { /* ignore */ }

  /* ---------- Year ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
