#!/usr/bin/env python3
"""
TPSL static site generator.
Edit the content below and run:  python3 build/build.py
Output is written to ../public_html (plain HTML, no server-side runtime needed
except enquiry.php for the contact form).
"""
import os, json, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = ROOT  # pages are served from the repository root
SITE = "https://www.tpsl.in"
UPDATED = "4 November 2026"
YEAR = 2026


def ph(text):
    """Visible placeholder for details the client still has to supply."""
    return f'<span class="placeholder">[{text}]</span>'


# --------------------------------------------------------------------------- icons
ICON = {
    "store": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 9l1.5-5h15L21 9"/><path d="M3 9h18v2a3 3 0 0 1-6 0 3 3 0 0 1-6 0 3 3 0 0 1-6 0z"/><path d="M5 13v7h14v-7"/><path d="M10 20v-4h4v4"/></svg>',
    "globe": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="14" rx="2"/><path d="M2 8h20"/><path d="M6 13h4"/><path d="M8 21h8"/></svg>',
    "spark": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v4M12 17v4M3 12h4M17 12h4"/><path d="M12 8l1.8 2.2L16 12l-2.2 1.8L12 16l-1.8-2.2L8 12l2.2-1.8z"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/></svg>',
    "bank": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 10l9-6 9 6"/><path d="M5 10v8M9.5 10v8M14.5 10v8M19 10v8"/><path d="M3 21h18"/></svg>',
    "chart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg>',
    "world": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a14 14 0 0 1 0 18a14 14 0 0 1 0-18"/></svg>',
    "doc": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/><path d="M8 13h8M8 17h5"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3zM9.5 9.5h3.8v1.6h.06c.53-1 1.83-2.06 3.77-2.06 4.03 0 4.77 2.65 4.77 6.1V21h-4v-5.1c0-1.22-.02-2.78-1.7-2.78-1.7 0-1.96 1.33-1.96 2.7V21h-4z"/></svg>',
}
CHEV = '<svg class="chev" viewBox="0 0 10 10" aria-hidden="true"><path d="M1 3l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'

NAV = [
    ("Home", "index.html", "home"),
    ("Our Offerings", "offerings.html", "offerings"),
    ("Resources", "resources.html", "resources"),
    ("Support", "support.html", "support"),
]
OFFER_SUB = [
    ("In-Store Payments", "in-store-payments.html", "POS Terminals, Soft POS, Sound Box"),
    ("Online Payments", "online-payments.html", "Payment Gateway, Recurring Payments, Payment Links"),
    ("Cross-Border Payments", "cross-border-payments.html", "International card acceptance and settlements"),
    ("Value Added Services", "value-added-services.html", "Merchant hub, onboarding, DCC, UPI, Transit, Embedded"),
]


def header(active):
    items = []
    for label, href, key in NAV:
        cur = ' aria-current="page"' if key == active else ""
        if key == "offerings":
            sub = "".join(f'<li><a href="{h}">{l}<span>{d}</span></a></li>' for l, h, d in OFFER_SUB)
            items.append(
                f'<li class="has-sub" data-open="false"><button class="nav-link" type="button" aria-expanded="false" aria-controls="sub-offerings">{label} {CHEV}</button>'
                f'<ul class="submenu" id="sub-offerings"><li><a href="offerings.html">All Offerings<span>Payment solutions for every business</span></a></li>{sub}</ul></li>'
            )
        else:
            items.append(f'<li><a class="nav-link" href="{href}"{cur}>{label}</a></li>')
    return f'''<a class="skip-link" href="#main">Skip to main content</a>
<header class="site-header">
  <div class="container header-inner">
    <a class="logo" href="index.html" aria-label="TPSL home"><img src="assets/img/tpsl-logo.svg" alt="TPSL" width="124" height="60"></a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="primary-nav" aria-label="Open menu">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </button>
    <nav class="nav" id="primary-nav" aria-label="Primary">
      <ul>{"".join(items)}</ul>
      <a class="btn btn-primary header-cta" href="contact.html"{' aria-current="page"' if active == "contact" else ""}>Contact Us</a>
    </nav>
  </div>
</header>'''


def footer():
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="assets/img/tpsl-logo.svg" alt="TPSL" width="124" height="60">
        <p class="tag">Powering Payments. Enabling Possibilities.</p>
        <p class="footer-phone">Tel: <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>
      </div>
      <div>
        <h4>Quick Links</h4>
        <ul><li><a href="index.html">Home</a></li><li><a href="offerings.html">Our Offerings</a></li><li><a href="resources.html">Resources</a></li><li><a href="support.html">Support</a></li><li><a href="contact.html">Contact Us</a></li></ul>
      </div>
      <div>
        <h4>Our Solutions</h4>
        <ul><li><a href="in-store-payments.html">In-Store Payments</a></li><li><a href="online-payments.html">Online Payments</a></li><li><a href="cross-border-payments.html">Cross-Border Payments</a></li><li><a href="value-added-services.html">Value Added Services</a></li></ul>
      </div>
      <div>
        <h4>Legal &amp; Policies</h4>
        <ul><li><a href="privacy-policy.html">Privacy Policy</a></li><li><a href="terms-and-conditions.html">Terms &amp; Conditions</a></li><li><a href="disclaimer.html">Disclaimer</a></li><li><a href="support.html#grievance">Grievance Redressal</a></li></ul>
      </div>
      <div>
        <h4>Connect With Us</h4>
        <ul><li><a href="contact.html">Contact Us</a></li></ul>
        <div class="social"><a href="{LINKEDIN}" rel="noopener noreferrer" target="_blank" aria-label="TPSL on LinkedIn (opens in a new tab)">{ICON["linkedin"]}</a></div>
      </div>
    </div>
    <div class="footer-entities">{"".join(f'''<address class="entity-card"><strong>{e["name"].upper()}</strong><span class="formerly">(Formerly known as "{e["formerly"]}")</span>{ADDRESS_HTML}<span class="ids">CIN: {e["cin"]}<br>GST No. {e["gst"]}</span></address>''' for e in ENTITIES)}</div>
    <div class="footer-bottom">
      <p>© {YEAR} TPSL. All Rights Reserved.</p>
      <p class="safety">TPSL will never ask for your card PIN, CVV, OTP or passwords. Report suspected fraud on <a href="tel:1930">1930</a> or <a href="https://cybercrime.gov.in/" rel="noopener noreferrer" target="_blank">cybercrime.gov.in</a>.</p>
    </div>
  </div>
</footer>
<div class="cookie-banner" role="region" aria-label="Cookie notice">
  <p>This website uses only essential browser storage needed for it to work and to remember your display preferences. We do not use advertising or tracking cookies. Read our <a href="privacy-policy.html#cookies">Privacy Policy</a>.</p>
  <button class="btn btn-primary" type="button" data-cookie-ack>OK, got it</button>
</div>
<button class="a11y-btn" type="button" aria-label="Accessibility options" aria-expanded="false" aria-controls="a11y-panel">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="4.5" r="1.8" fill="currentColor"/><path d="M5 8.5l7 1.5 7-1.5M12 10v5M9 21l3-6 3 6"/></svg>
</button>
<div class="a11y-panel" id="a11y-panel" role="dialog" aria-label="Accessibility options">
  <h4>Accessibility</h4>
  <button type="button" data-a11y="large" aria-pressed="false">Larger text</button>
  <button type="button" data-a11y="contrast" aria-pressed="false">Higher contrast</button>
  <button type="button" data-a11y="links" aria-pressed="false">Underline links</button>
  <button type="button" data-a11y="reset">Reset</button>
</div>
<script src="assets/js/main.js" defer></script>'''


PHONE_DISPLAY = "022 7198 0000"
PHONE_TEL = "+912271980000"
ADDRESS_HTML = "Raiaskaran Tech Park, Tower 1, 2nd Floor, Phase 2,<br>Sakinaka, M.V. Road, Andheri East,<br>Mumbai – 400072"
ENTITIES = [
    {"name": "TPSL India Private Limited", "formerly": "Worldline India Private Limited",
     "cin": "U72200MH1997PTC242097", "gst": "27AABCE2403J1Z0"},
    {"name": "TPSL ePayments India Private Limited", "formerly": "Worldline ePayments India Private Limited",
     "cin": "U74200MH2005PTC192623", "gst": "27AABCE4591N1Z6"},
]

LINKEDIN = "https://www.linkedin.com/"  # TODO: replace with TPSL's LinkedIn company page URL


def page(filename, title, desc, active, body, noindex=False):
    canonical = f"{SITE}/" if filename == "index.html" else f"{SITE}/{filename}"
    ld = ""
    if filename == "index.html":
        ld = '<script type="application/ld+json">' + json.dumps({
            "@context": "https://schema.org", "@type": "Organization", "name": "TPSL", "url": SITE + "/",
            "logo": SITE + "/assets/img/tpsl-logo.svg", "slogan": "Powering Payments. Enabling Possibilities.", "telephone": PHONE_TEL,
            "address": {"@type": "PostalAddress", "streetAddress": "Raiaskaran Tech Park, Tower 1, 2nd Floor, Phase 2, Sakinaka, M.V. Road, Andheri East",
                        "addressLocality": "Mumbai", "postalCode": "400072", "addressRegion": "Maharashtra", "addressCountry": "IN"},
        }) + "</script>"
    full_title = title if filename == "index.html" else f"{title} | TPSL"
    html = f'''<!doctype html>
<html lang="en-IN" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full_title}</title>
<meta name="description" content="{desc}">
{'<meta name="robots" content="noindex">' if noindex else ''}
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="TPSL">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="preload" href="assets/fonts/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/sora-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/style.css">
{ld}
</head>
<body>
{header(active)}
<main id="main">
{body}
</main>
{footer()}
</body>
</html>
'''
    html = "\n".join(l for l in html.split("\n") if l.strip() != "")
    open(os.path.join(OUT, filename), "w", encoding="utf-8").write(html)


def page_hero(crumbs, eyebrow, h1, lead):
    cr = '<li><a href="index.html">Home</a></li>' + "".join(
        (f'<li><a href="{h}">{l}</a></li>' if h else f'<li aria-current="page">{l}</li>') for l, h in crumbs)
    return f'''<section class="page-hero">
  <div class="container">
    <nav class="breadcrumb" aria-label="Breadcrumb"><ol>{cr}</ol></nav>
    <span class="eyebrow">{eyebrow}</span>
    <h1>{h1}</h1>
    <p class="lead">{lead}</p>
  </div>
</section>'''


def cta_band(title="Let's Simplify Payments Together", text="Looking for the right payment solution for your business? Connect with our team to explore how TPSL can support your payment needs.", btn="Talk to Our Team"):
    return f'''<section class="section-sm"><div class="container">
  <div class="cta-band reveal"><div><h2>{title}</h2><p>{text}</p></div><a class="btn btn-light" href="contact.html">{btn}</a></div>
</div></section>'''


ENQUIRY_TYPES = ["In-Store Payments (POS, Soft POS, Sound Box)", "Online Payments (Gateway, Recurring, Payment Links)",
                 "Cross-Border Payments", "Value Added Services", "Partnership", "Existing Merchant Support", "Other"]


def enquiry_form(fid, preselect=""):
    opts = "".join(f'<option{" selected" if o == preselect else ""}>{o}</option>' for o in ENQUIRY_TYPES)
    return f'''<form class="enquiry-form form-wrap" id="{fid}" action="enquiry.php" method="post" novalidate>
  <div class="form-grid">
    <div class="field"><label for="{fid}-name">Full Name <span class="req" aria-hidden="true">*</span></label><input id="{fid}-name" name="full_name" type="text" autocomplete="name" maxlength="100" required><p class="error">Please enter your full name.</p></div>
    <div class="field"><label for="{fid}-company">Company Name <span class="req" aria-hidden="true">*</span></label><input id="{fid}-company" name="company" type="text" autocomplete="organization" maxlength="150" required><p class="error">Please enter your company name.</p></div>
    <div class="field"><label for="{fid}-email">Business Email <span class="req" aria-hidden="true">*</span></label><input id="{fid}-email" name="email" type="email" autocomplete="email" maxlength="150" required><p class="error">Please enter a valid business email.</p></div>
    <div class="field"><label for="{fid}-phone">Contact Number <span class="req" aria-hidden="true">*</span></label><input id="{fid}-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" maxlength="16" required><p class="error">Please enter a valid contact number.</p></div>
    <div class="field full"><label for="{fid}-type">Nature of Enquiry <span class="req" aria-hidden="true">*</span></label><select id="{fid}-type" name="enquiry_type" required><option value="">Select an option</option>{opts}</select><p class="error">Please choose the nature of your enquiry.</p></div>
    <div class="field full"><label for="{fid}-msg">Message <span class="req" aria-hidden="true">*</span></label><textarea id="{fid}-msg" name="message" maxlength="2000" required></textarea><p class="error">Please tell us a little about your requirement.</p></div>
    <div class="hp-field" aria-hidden="true"><label for="{fid}-website">Leave this field empty</label><input id="{fid}-website" name="website" type="text" tabindex="-1" autocomplete="off"></div>
    <div class="full"><label class="consent"><input type="checkbox" name="consent" value="yes" required> <span>I consent to TPSL using the details above to respond to my enquiry, as described in the <a href="privacy-policy.html">Privacy Policy</a>. <span class="req" aria-hidden="true">*</span></span></label></div>
  </div>
  <div class="form-status" role="status" aria-live="polite"></div>
  <p><button class="btn btn-primary" type="submit">Submit Enquiry</button></p>
  <p class="form-note">Please do not share card numbers, PIN, CVV, OTP, passwords or bank account credentials in this form.</p>
</form>'''


# =========================================================================== HOME
home = f'''
<section class="hero">
  <svg class="hero-shapes" viewBox="0 0 640 640" aria-hidden="true"><rect x="220" y="40" width="380" height="380" rx="70" fill="#FFD38A" opacity=".55" transform="rotate(24 410 230)"/><rect x="120" y="260" width="360" height="300" rx="60" fill="#FDEEE4" transform="rotate(-12 300 410)"/></svg>
  <div class="container hero-grid">
    <div>
      <span class="eyebrow">Omnichannel payments technology</span>
      <h1>Powering Payments. <span>Enabling Possibilities.</span></h1>
      <p class="lead">Simplifying payments for businesses with secure, seamless and innovative omnichannel payment solutions.</p>
      <div class="hero-actions"><a class="btn btn-primary" href="offerings.html">Explore Our Solutions</a><a class="btn btn-outline" href="contact.html">Contact Us</a></div>
      <div class="hero-stats"><div><strong>26+</strong><span>Years of experience</span></div><div><strong>30+</strong><span>Partner banks</span></div><div><strong>100+</strong><span>Payment modes</span></div></div>
    </div>
    <div class="hero-art"><img src="assets/img/hero-payments.svg" alt="" width="560" height="500"></div>
  </div>
</section>

<section class="section alt" id="about">
  <div class="container split">
    <div class="reveal"><img src="assets/img/about-network.svg" alt="" width="520" height="420"></div>
    <div class="reveal">
      <span class="eyebrow">About TPSL</span>
      <h2>Your Trusted Payments Technology Partner</h2>
      <p>With over 26 years of experience, TPSL is a leading omnichannel payments technology company enabling seamless payment experiences for businesses across India.</p>
      <p>A preferred technology partner to over 30 leading public and private sector banks, TPSL serves businesses across industries, including NBFCs, insurance, e-commerce, retail, hospitality, startups and more.</p>
      <p>Our comprehensive suite of in-store and online payment solutions helps businesses accept payments efficiently, enhance customer experiences and grow with confidence.</p>
      <ul class="pills"><li>NBFCs</li><li>Insurance</li><li>E-commerce</li><li>Retail</li><li>Hospitality</li><li>Startups</li></ul>
      <a class="btn btn-primary" href="offerings.html">Know More</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head center reveal">
      <span class="eyebrow">Our Offerings</span>
      <h2>Payment Solutions for Every Business</h2>
      <p class="lead">From in-store payments to digital transactions, TPSL offers a comprehensive suite of payment solutions designed to simplify payment acceptance, improve operational efficiency and support business growth.</p>
    </div>
    <div class="cards four">
      <article class="card reveal"><div class="icon">{ICON["store"]}</div><h3>In-Store Payments</h3><p>Accept payments seamlessly across physical business locations with our range of POS terminals, Soft POS and Sound Box solutions.</p><a class="btn-link" href="in-store-payments.html">Explore In-Store Solutions</a></article>
      <article class="card reveal"><div class="icon">{ICON["globe"]}</div><h3>Online Payments</h3><p>Enable convenient digital payment acceptance with our Payment Gateway, Recurring Payments and Payment Links solutions.</p><a class="btn-link" href="online-payments.html">Explore Online Solutions</a></article>
      <article class="card reveal"><div class="icon">{ICON["world"]}</div><h3>Cross-Border Payments</h3><p>Accept payments from international customers using international credit cards, with settlement into designated bank accounts.</p><a class="btn-link" href="cross-border-payments.html">Explore Cross-Border Payments</a></article>
      <article class="card reveal"><div class="icon">{ICON["spark"]}</div><h3>Value Added Services</h3><p>Go beyond payment acceptance with solutions for merchant management, digital onboarding, Dynamic Currency Conversion, UPI payments, Transit and Embedded payments.</p><a class="btn-link" href="value-added-services.html">Explore Value Added Services</a></article>
    </div>
  </div>
</section>

<section class="section alt" id="contact">
  <div class="container contact-grid">
    <div class="reveal">
      <span class="eyebrow">Contact Us</span>
      <h2>Let's Simplify Payments Together</h2>
      <p class="lead">Looking for the right payment solution for your business? Connect with our team to explore how TPSL can support your payment needs.</p>
      <ul class="check-list"><li>Guidance on the right mix of in-store and online solutions</li><li>Integration support for APIs, SDKs and plugins</li><li>Help with onboarding and activation</li></ul>
    </div>
    <div class="reveal">{enquiry_form("home-form")}</div>
  </div>
</section>
'''
page("index.html", "TPSL | Powering Payments. Enabling Possibilities.",
     "TPSL is an omnichannel payments technology company with 26+ years of experience, offering POS, Soft POS, Sound Box, Payment Gateway, Recurring Payments, Payment Links and value added services.",
     "home", home)

# =========================================================================== OFFERINGS overview
offer = page_hero([("Our Offerings", None)], "Our Offerings", "Payment Solutions for Every Business",
                  "From in-store payments to digital transactions, TPSL offers a comprehensive suite of payment solutions designed to simplify payment acceptance, improve operational efficiency and support business growth.")
groups = [
    ("In-Store Payments", "in-store-payments.html", "store", "Smarter Payments for Every Store", "pos-smart.svg",
     [("POS Terminals", "pos"), ("Soft POS", "softpos"), ("Sound Box", "soundbox")]),
    ("Online Payments", "online-payments.html", "globe", "Seamless Digital Payments for Your Business", "checkout-web.svg",
     [("Payment Gateway", "gateway"), ("Recurring Payments", "recurring"), ("Payment Links", "links")]),
    ("Cross-Border Payments", "cross-border-payments.html", "world", "Enabling Seamless Payments Across Borders", "cross-border.svg",
     [("International Payment Acceptance", "features"), ("Simplified Settlements", "features"), ("Business Benefits", "benefits")]),
    ("Value Added Services", "value-added-services.html", "spark", "Beyond Payments. Enabling More.", "merchant-hub.svg",
     [("One Merchant Hub", "hub"), ("Digital &amp; Omnichannel Onboarding", "onboarding"), ("Dynamic Currency Conversion", "dcc"),
      ("End-to-End UPI Solution", "upi"), ("Transit Solutions", "transit"), ("Embedded Payments", "embedded")]),
]
blurbs = {
    "In-Store Payments": "Enable seamless payment acceptance across physical business locations with TPSL's range of in-store payment solutions.",
    "Online Payments": "Simplify online payment acceptance with flexible solutions designed to support businesses across digital channels.",
    "Cross-Border Payments": "Expand your business globally. Accept payments from international customers through a secure and reliable payment infrastructure.",
    "Value Added Services": "Enhance business efficiency and customer experience with TPSL's range of value added services designed to simplify payment operations and support evolving business needs.",
}
for i, (name, href, ic, tag, art, items) in enumerate(groups):
    links = "".join(f'<li><a href="{href}#{a}">{l}</a></li>' for l, a in items)
    offer += f'''<section class="section{' alt' if i % 2 else ''}"><div class="container split{' reverse' if i % 2 else ''}">
  <div class="reveal"><span class="eyebrow">{name}</span><h2>{tag}</h2><p class="lead">{blurbs[name]}</p>
  <ul class="check-list">{links}</ul><a class="btn btn-primary" href="{href}">Explore {name}</a></div>
  <div class="reveal art-frame"><img src="assets/img/{art}" alt=""></div>
</div></section>'''
offer += cta_band()
page("offerings.html", "Our Offerings", "TPSL payment solutions: in-store payments, online payments, cross-border payments and value added services for businesses of every size.", "offerings", offer)

# =========================================================================== IN-STORE
def product(id_, eyebrow, h2, tagline, paras, art, extra="", alt="", reverse=False, enquiry=""):
    ps = "".join(f"<p>{p}</p>" for p in paras)
    q = f"?enquiry={enquiry}" if enquiry else ""
    return f'''<section class="product-block" id="{id_}"><div class="container">
  <div class="split{' reverse' if reverse else ''}">
    <div class="reveal"><span class="eyebrow">{eyebrow}</span><h2>{h2}</h2>{f'<p class="sub-head">{tagline}</p>' if tagline else ''}{ps}{extra}<a class="btn btn-primary" href="contact.html{q}">Contact Us</a></div>
    <div class="reveal art-frame">{art}</div>
  </div>
</div></section>'''


def carousel(label, devices):
    cards = "".join(f'<article class="device-card"><div class="device-art"><img src="assets/img/{f}" alt="{a}" loading="lazy" width="300" height="300"></div><h4>{t}</h4><p>{d}</p></article>' for f, a, t, d in devices)
    return f'''<div class="carousel" role="region" aria-label="{label}">
  <div class="carousel-track" tabindex="0">{cards}</div>
  <div class="carousel-controls"><button class="carousel-btn" type="button" data-dir="prev" aria-label="Previous">&#8592;</button><button class="carousel-btn" type="button" data-dir="next" aria-label="Next">&#8594;</button></div>
</div>'''


instore = page_hero([("Our Offerings", "offerings.html"), ("In-Store Payments", None)], "In-Store Payment Solutions", "Smarter Payments for Every Store",
                    "Enable seamless payment acceptance across physical business locations with TPSL's range of in-store payment solutions.")
instore += '<nav class="subnav" aria-label="On this page"><div class="container"><ul><li><a href="#pos">POS Terminals</a></li><li><a href="#softpos">Soft POS</a></li><li><a href="#soundbox">Sound Box</a></li></ul></div></nav>'
# POS – full-width carousel layout
instore += f'''<section class="product-block" id="pos"><div class="container">
  <div class="section-head reveal"><span class="eyebrow">POS Terminals</span><h2>Reliable Payments at Every Counter</h2>
  <p class="lead">Accept digital payments conveniently with POS terminals designed for businesses of all sizes. Deliver smooth checkout experiences and simplify everyday transactions.</p></div>
  {carousel("POS terminal range", [
      ("pos-smart.svg", "Android smart POS terminal", "Android Smart POS", "Touchscreen terminal with built-in printer for cards, UPI and QR."),
      ("pos-countertop.svg", "Countertop POS terminal", "Countertop POS", "Robust keypad terminal for high-volume billing counters."),
      ("pos-mini.svg", "Compact handheld POS", "Compact Handheld POS", "Portable terminal with dynamic QR display for on-the-go checkout."),
      ("pos-mpos.svg", "Card reader paired with smartphone", "mPOS Card Reader", "Lightweight card reader that pairs with a smartphone."),
  ])}
  <p><a class="btn btn-primary" href="contact.html?enquiry=pos">Contact Us</a></p>
</div></section>'''
instore += product("softpos", "Soft POS", "Turn Your Android Smartphone into a Payment Terminal", "",
                   ["Accept contactless payments using a compatible NFC-enabled smartphone without the need for a traditional POS terminal. A convenient payment acceptance solution for businesses on the move."],
                   '<img src="assets/img/softpos.svg" alt="Contactless card tapped on an Android smartphone">',
                   extra='<ul class="check-list"><li>Tap to pay with contactless cards and devices</li><li>No additional hardware required</li><li>Ideal for delivery, field sales and pop-up stores</li></ul>', reverse=True, enquiry="softpos")
instore += f'''<section class="product-block" id="soundbox"><div class="container">
  <div class="section-head reveal"><span class="eyebrow">Sound Box</span><h2>Instant Payment Alerts. Greater Convenience.</h2>
  <p class="lead">Get instant audio notifications for successful payments, helping merchants confirm transactions and manage busy checkout environments with ease.</p></div>
  {carousel("Sound box range", [
      ("soundbox-allinone.svg", "All-in-one sound box with QR and card tap", "All-in-One Sound Box", "QR, tap-to-pay and voice alerts in a single counter device."),
      ("soundbox-display.svg", "Sound box with amount display", "Display Sound Box", "Shows the paid amount on screen alongside the voice alert."),
      ("soundbox-classic.svg", "Sound box with QR standee", "Classic Sound Box", "Reliable voice confirmation with a static QR standee."),
      ("soundbox-pocket.svg", "Portable battery sound box", "Portable Sound Box", "Compact, long-battery device for small and mobile merchants."),
  ])}
  <p><a class="btn btn-primary" href="contact.html?enquiry=soundbox">Contact Us</a></p>
</div></section>'''
instore += cta_band()
page("in-store-payments.html", "In-Store Payments", "POS terminals, Soft POS and Sound Box solutions from TPSL for seamless in-store payment acceptance.", "offerings", instore)

# =========================================================================== ONLINE
online = page_hero([("Our Offerings", "offerings.html"), ("Online Payments", None)], "Online Payment Solutions", "Seamless Digital Payments for Your Business",
                   "Simplify online payment acceptance with flexible solutions designed to support businesses across digital channels.")
online += '<nav class="subnav" aria-label="On this page"><div class="container"><ul><li><a href="#gateway">Payment Gateway</a></li><li><a href="#recurring">Recurring Payments</a></li><li><a href="#links">Payment Links</a></li></ul></div></nav>'
online += f'''<section class="product-block" id="gateway"><div class="container">
  <div class="split">
    <div class="reveal"><span class="eyebrow">Payment Gateway</span><h2>One Gateway. Multiple Payment Options.</h2>
      <p class="tagline">Seamless Payments. Smarter Transactions. Faster Growth.</p>
      <p>Enable customers to make secure online payments through multiple payment methods with a seamless checkout experience across websites and applications.</p>
      <a class="btn btn-primary" href="contact.html?enquiry=gateway">Contact Us</a></div>
    <div class="reveal art-frame"><img src="assets/img/checkout-web.svg" alt="Online checkout showing UPI, cards, net banking, EMI and wallets, with a payment success screen on mobile"></div>
  </div>
  <div class="stat-strip reveal" style-hook="">
    <div><strong>100+ Payment Modes</strong><span>Cards, UPI, Net Banking, EMI &amp; Wallets</span></div>
    <div><strong>Quick Integration</strong><span>APIs, SDKs, JS &amp; 20+ Plugins</span></div>
    <div><strong>Higher Success Rates</strong><span>Intelligent routing &amp; strong bank connectivity</span></div>
    <div><strong>Powerful Controls</strong><span>Refunds, reconciliation, fraud management &amp; real-time monitoring</span></div>
  </div>
</div></section>'''.replace(' style-hook=""', '')


def feature_list(items):
    return '<ul class="check-list">' + "".join(f"<li><strong>{a}</strong> – {b}</li>" for a, b in items) + "</ul>"


online += product("recurring", "Recurring Payments", "Simplify Repeat Payments. Automate Collections.", "",
                  ["Streamline subscription fees, instalments and recurring collections with intelligent payment automation. Enable businesses to manage repeat transactions effortlessly through secure, reliable and seamless payment solutions."],
                  '<img src="assets/img/recurring.svg" alt="Calendar of scheduled automatic collections">',
                  extra="<h3>Key Features</h3>" + feature_list([
                      ("Multiple Recurring Modes", "Accept recurring payments through Cards, UPI, eNACH, NACH and Direct Debit."),
                      ("End-to-End Automation", "Automate mandate setup, scheduled collections and the entire payment lifecycle."),
                      ("Secure &amp; Compliant", "Enable OTP verification, eSign and authentication-based payment authorization."),
                      ("Complete Visibility", "Manage recurring transactions with centralized controls, seamless reconciliation and detailed reporting.")]),
                  reverse=True, enquiry="recurring")
online += product("links", "Payment Links", "Collect Payments. Anytime, Anywhere.", "",
                  ["Generate and share secure payment links with customers to collect payments effortlessly—without requiring a website or mobile application. Simplify the payment process and make it easier for customers to pay from anywhere, on any device."],
                  '<img src="assets/img/payment-links.svg" alt="Payment link shared to a customer by SMS and email">',
                  extra="<h3>Key Features</h3>" + feature_list([
                      ("Send &amp; Collect Easily", "Create and share payment links instantly through SMS and Email for quick and convenient collections."),
                      ("Customizable Experience", "Personalize payment messages, set link validity and attach invoices for a seamless customer experience."),
                      ("Multiple Payment Modes", "Accept payments through Credit &amp; Debit Cards, UPI and other digital payment options."),
                      ("Track &amp; Manage", "Monitor transactions, process refunds and access detailed reports through a centralized dashboard.")]),
                  enquiry="links")
online += cta_band()
page("online-payments.html", "Online Payments", "TPSL Payment Gateway, Recurring Payments and Payment Links for secure digital payment acceptance.", "offerings", online)

# =========================================================================== CROSS-BORDER
cb = page_hero([("Our Offerings", "offerings.html"), ("Cross-Border Payments", None)], "Cross-Border Payments", "Enabling Seamless Payments Across Borders",
               "Expand your business globally with TPSL's Cross-Border Payment Solutions. Accept payments from international customers through a secure and reliable payment infrastructure, simplifying overseas collections and supporting business growth.")
cb += '''<section class="product-block" id="features"><div class="container">
  <div class="split">
    <div class="reveal"><span class="eyebrow">Key Features</span><h2>International Payments, Simplified</h2>
      <ul class="check-list">
        <li><strong>International Payment Acceptance</strong> – Accept payments from overseas customers using international credit cards.</li>
        <li><strong>Simplified Settlements</strong> – Enable settlement of international collections into designated bank accounts through supported arrangements.</li>
        <li><strong>Secure Transactions</strong> – Facilitate cross-border payments through a secure payment infrastructure with appropriate risk and compliance controls.</li>
        <li><strong>Easy Integration</strong> – Integrate international payment acceptance into your existing online payment ecosystem.</li>
        <li><strong>Transaction Visibility</strong> – Access payment information and reports for better tracking and reconciliation.</li>
      </ul>
      <a class="btn btn-primary" href="contact.html?enquiry=crossborder">Explore Cross-Border Payment Solutions</a></div>
    <div class="reveal art-frame"><img src="assets/img/cross-border.svg" alt="International card payment travelling across a globe and settling into a bank account" width="520" height="380"></div>
  </div>
</div></section>
<section class="section alt" id="benefits"><div class="container">
  <div class="section-head reveal"><span class="eyebrow">Business Benefits</span><h2>Grow Beyond Borders</h2></div>
  <div class="cards four">
    <article class="card reveal"><div class="icon">''' + ICON["world"] + '''</div><h3>Global Reach</h3><p>Expand your reach to international customers.</p></article>
    <article class="card reveal"><div class="icon">''' + ICON["bank"] + '''</div><h3>Simpler Collections</h3><p>Simplify overseas payment collections.</p></article>
    <article class="card reveal"><div class="icon">''' + ICON["globe"] + '''</div><h3>Customer Convenience</h3><p>Improve payment convenience for global customers.</p></article>
    <article class="card reveal"><div class="icon">''' + ICON["chart"] + '''</div><h3>Greater Visibility</h3><p>Manage cross-border transactions with greater visibility.</p></article>
  </div>
</div></section>'''
cb += cta_band("Ready to Accept Payments from Around the World?", "Talk to our team about adding international payment acceptance to your business.", "Explore Cross-Border Payment Solutions").replace('href="contact.html"', 'href="contact.html?enquiry=crossborder"')
page("cross-border-payments.html", "Cross-Border Payments", "Accept payments from international customers with TPSL's Cross-Border Payment Solutions: international card acceptance, simplified settlements and transaction visibility.", "offerings", cb)

# =========================================================================== VAS
vas = page_hero([("Our Offerings", "offerings.html"), ("Value Added Services", None)], "Value Added Services", "Beyond Payments. Enabling More.",
                "Enhance business efficiency and customer experience with TPSL's range of value added services designed to simplify payment operations and support evolving business needs.")
vas += '<nav class="subnav" aria-label="On this page"><div class="container"><ul>' + "".join(
    f'<li><a href="#{a}">{l}</a></li>' for l, a in next(g for g in groups if g[0] == "Value Added Services")[5]) + "</ul></div></nav>"
vas += product("hub", "One Merchant Hub", "One Platform. Simplified Merchant Management.", "",
               ["Manage all your payment channels through one unified platform. Gain complete transaction visibility, streamline operations and make smarter business decisions with centralized merchant management."],
               '<img src="assets/img/merchant-hub.svg" alt="Unified merchant dashboard with transaction metrics and charts">',
               extra='''<div class="feature-grid"><div class="feature"><strong>Manage All Payment Channels</strong><ul class="check-list"><li>POS Transactions</li><li>QR Collections</li><li>Online Payments</li><li>Payment Links</li><li>SoftPOS Transactions</li></ul></div>
<div class="feature"><strong>Powerful Business Insights &amp; Controls</strong><ul class="check-list"><li>Real-Time Visibility</li><li>Unified Reporting</li><li>Analytics &amp; Insights</li><li>Business Management Tools</li><li>Simplified Operations</li></ul></div></div>
<p class="tagline">One Hub. Every Payment Channel. Complete Control.</p>''', enquiry="hub")
vas += product("onboarding", "Digital &amp; Omnichannel Onboarding", "Faster Onboarding. Seamless Activation.", "",
               ["Accelerate merchant onboarding with a digital-first solution that simplifies verification, minimizes manual effort and enables faster business activation through seamless self-service and assisted journeys."],
               '<img src="assets/img/onboarding.svg" alt="Merchant sign-up steps: digital KYC, bank account check, e-Sign and go live">',
               extra="<h3>Key Features</h3>" + feature_list([
                   ("Digital KYC", "Quick and secure identity verification."), ("Account Validation", "Seamless bank account verification."),
                   ("e-Sign", "Hassle-free digital document signing."), ("Assisted &amp; Self-Onboarding", "Flexible onboarding journeys tailored to merchant needs.")]) +
               '<p class="tagline">Simplify Onboarding. Accelerate Activation.</p>', reverse=True, enquiry="onboarding")
vas += product("dcc", "Dynamic Currency Conversion (DCC)", "Pay in Your Currency. Enjoy Greater Transparency.", "",
               ["Enable international cardholders to pay in their home currency at the point of sale with real-time currency conversion, greater transparency and a seamless payment experience."],
               '<img src="assets/img/dcc.svg" alt="POS terminal offering a choice between home currency and Indian rupees">',
               extra='<h3>Key Benefits</h3><ul class="check-list"><li>Additional Fee-Based Revenue Opportunity</li><li>Real-Time Currency Conversion</li><li>Transparent Currency Display</li><li>Improved Foreign Card Conversion</li><li>Enhanced Cardholder Experience &amp; Trust</li><li>Growing Adoption Across Premium Merchants</li></ul><p class="tagline">More Transparency. Better Experiences. New Revenue Opportunities.</p>',
               enquiry="dcc")
vas += product("upi", "End-to-End UPI Solution", "Simplifying UPI Payments for Businesses.", "",
               ["Enable seamless UPI acceptance with a unified solution offering flexible payment modes, real-time transaction visibility and efficient payment management across merchant channels."],
               '<img src="assets/img/upi.svg" alt="QR standee and smartphone completing a UPI payment">',
               extra="<h3>Key Features</h3>" + feature_list([
                   ("Static &amp; Dynamic QR", "Accept payments through physical and digital QR codes across POS, SoftPOS and SuperApp."),
                   ("Unified Transaction View", "Track POS, QR and online payment transactions through the Worldline SuperApp."),
                   ("Multi-Terminal Capabilities", "Enable transaction notifications and charge-slip printing across terminals."),
                   ("Voice Notifications", "Receive instant payment alerts through POS terminals.")]) +
               '<p class="tagline">One UPI Solution. Seamless Acceptance. Complete Visibility.</p>', reverse=True, enquiry="upi")
vas += product("transit", "Transit Solutions", "Making Every Journey Seamless.", "",
               ["Enable seamless digital fare collection with an integrated transit solution designed to enhance passenger convenience, simplify operations and streamline transit payments."],
               '<img src="assets/img/transit.svg" alt="Bus with a contactless fare validator">',
               extra='<h3>Key Capabilities</h3><ul class="check-list cols"><li>NCMC-certified Switch &amp; POS Terminals for Retail and Transit</li><li>Live Deployment with DTC</li><li>Pass &amp; Card Issuance</li><li>Integrated Automated Fare Collection System (AFCS)</li><li>Automated Reconciliation</li><li>API-Based Onboarding</li><li>Real-Time Transaction Monitoring</li></ul><p class="tagline">Seamless Payments. Smarter Transit. Connected Journeys.</p>',
               enquiry="transit")
vas += product("embedded", "Embedded Payments", "Payments Integrated into Your Business.", "",
               ["Embed seamless digital payment capabilities into business platforms and public services, simplifying collections and enhancing citizen convenience across multiple touchpoints."],
               '<img src="assets/img/embedded.svg" alt="Payment layer connecting e-Challan, parking, donations, property tax, municipal fees and NCMC transit">',
               extra='<h3>Key Use Cases</h3><ul class="pills"><li>Traffic Police e-Challan Collections</li><li>Digital Parking Payments</li><li>Temple Donations</li><li>Property Tax Collections</li><li>Municipal Fines &amp; Fee Collections</li><li>Transit Bus Payments – NCMC</li></ul><h3>Key Features</h3>' + feature_list([
                   ("Multiple Payment Modes", "UPI, Cards, QR and other digital payment options."), ("Seamless Integration", "API-based integration with existing platforms and systems."),
                   ("Real-Time Tracking", "Instant payment confirmation and transaction monitoring."), ("Automated Reconciliation", "Simplified settlement and collection reporting."),
                   ("Centralized Dashboard", "Unified visibility and management of transactions."), ("Secure Payments", "Authentication-enabled transactions and fraud controls.")]) +
               '<p class="tagline">Integrated Payments. Simplified Collections. Smarter Public Services.</p>', reverse=True, enquiry="embedded")
vas += cta_band()
page("value-added-services.html", "Value Added Services", "One Merchant Hub, digital onboarding, Dynamic Currency Conversion, UPI, Transit and Embedded payment solutions from TPSL.", "offerings", vas)

# =========================================================================== SUPPORT
def level(n, title, lines):
    return f'<div class="level"><span class="lvl">Level {n}</span><h4>{title}</h4>{"".join(f"<p>{l}</p>" for l in lines)}</div>'


sup = page_hero([("Support", None)], "Customer Support and Grievance Redressal", "We're Here to Help",
                "TPSL is committed to providing timely assistance and addressing customer concerns through a structured grievance redressal process. For support or complaints, please contact the respective customer service teams below.")
sup += f'''<section class="section" id="grievance"><div class="container">
  <div class="entity reveal">
    <h3>TPSL ePayments India Private Limited</h3>
    <div class="levels">
      {level(1, "Customer Service Desk", ['Email: <a href="mailto:grievance@mail.tpsl-india.co.in">grievance@mail.tpsl-india.co.in</a>', 'Phone: <a href="tel:+912267664481">022-67664481</a>'])}
      {level(2, "Escalation Desk", ['If your grievance is not resolved within 3 days, please contact:', '<a href="mailto:escalations@mail.tpsl-india.co.in">escalations@mail.tpsl-india.co.in</a>'])}
      {level(3, "Nodal Officer", ['If your grievance remains unresolved within 7 days, please contact:', '<a href="mailto:nodalofficer@mail.tpsl-india.co.in">nodalofficer@mail.tpsl-india.co.in</a>'])}
    </div>
  </div>
  <div class="entity reveal">
    <h3>TPSL India Private Limited</h3>
    <div class="levels two">
      {level(1, "Customer Service Desk", ['Email: <a href="mailto:customer_support@mail.tpsl-india.co.in">customer_support@mail.tpsl-india.co.in</a>', 'Phone: <a href="tel:18602332332">1860 233 2332</a>'])}
      {level(2, "Escalation Desk", ['Contact Person: Satish Mhamunkar', 'Email: <a href="mailto:satish.mhamunkar@tpsl.in">satish.mhamunkar@tpsl.in</a>'])}
    </div>
  </div>
</div></section>

<section class="section alt" id="mnrl"><div class="container">
  <div class="section-head reveal"><span class="eyebrow">RBI MNRL and Customer Complaint Compliance Rules</span><h2>Stay Informed. Stay Protected.</h2>
  <p class="lead">TPSL is committed to promoting customer awareness and compliance with applicable regulatory guidelines related to commercial communications and customer complaint registration.</p></div>
  <div class="split">
    <div class="reveal"><h3>Managing Commercial Communications</h3><p>Customers can block all commercial communications or selectively manage their communication preferences through:</p>
      <ul class="check-list"><li>Their Telecom Service Provider's app or website</li><li>TRAI DND App</li><li>Calling or sending an SMS to <a href="tel:1909">1909</a></li></ul></div>
    <div class="reveal"><div class="notice"><strong>Important Information</strong><p>TPSL ePayments India Private Limited and TPSL India Private Limited will use the designated 1600XXX and 1400XXX numbering series for service and promotional calls, as applicable.</p></div></div>
  </div>
</div></section>

<section class="section" id="complaint"><div class="container">
  <div class="section-head reveal"><span class="eyebrow">How to Register a Complaint</span><h2>Report spam, fraud or cybercrime</h2></div>
  <div class="steps">
    <div class="step reveal"><h4>Receiving Spam Despite DND Registration</h4><p>Register a complaint through your Telecom Service Provider's app or website, the TRAI DND App, or by calling or sending an SMS to <a href="tel:1909">1909</a>.</p></div>
    <div class="step reveal"><h4>Reporting Suspected Fraudulent Communications</h4><p>Report suspected fraudulent communications received within the last 30 days through the Department of Telecommunications' Chakshu platform.<br>Chakshu Platform: <a href="https://sancharsaathi.gov.in/sfc/" rel="noopener noreferrer" target="_blank">https://sancharsaathi.gov.in/sfc/</a></p></div>
    <div class="step reveal"><h4>Reporting Financial Fraud or Cybercrime</h4><p>If you have experienced financial fraud or cybercrime, immediately contact the national cybercrime helpline at <a href="tel:1930">1930</a> or register a complaint through the National Cyber Crime Reporting Portal.<br>Cyber Crime Portal: <a href="https://cybercrime.gov.in/" rel="noopener noreferrer" target="_blank">https://cybercrime.gov.in/</a></p></div>
  </div>
</div></section>'''
page("support.html", "Support & Grievance Redressal", "TPSL customer support, grievance redressal escalation matrix, nodal officer contacts and how to report spam, fraud or cybercrime.", "support", sup)

# =========================================================================== RESOURCES
def doc_row(title, meta, href, pending=False):
    btn = ('<span class="btn btn-outline" aria-disabled="true">Coming soon</span>' if pending
           else f'<a class="btn btn-outline" href="{href}">View</a>')
    return f'<li><div class="doc-title">{ICON["doc"]}<div><strong>{title}</strong><div class="doc-meta">{meta}</div></div></div>{btn}</li>'


res = page_hero([("Resources", None)], "Resources", "Resources &amp; Information",
                "Access important information, documents and updates related to TPSL's payment solutions and services.")
res += f'''<section class="section"><div class="container">
  <div class="doc-group reveal"><h2>Policies and Regulatory Information</h2>
    <ul class="doc-list">
      {doc_row("Privacy Policy", "Web page · Updated " + UPDATED, "privacy-policy.html")}
      {doc_row("Terms &amp; Conditions", "Web page", "terms-and-conditions.html")}
      {doc_row("Disclaimer", "Web page", "disclaimer.html")}
      {doc_row("Grievance Redressal Mechanism", "Web page · Escalation matrix and nodal officer", "support.html#grievance")}
      {doc_row("RBI MNRL and Customer Complaint Compliance Rules", "Web page", "support.html#mnrl")}
      <!-- Add policy PDFs supplied by TPSL here, e.g.:
      {doc_row("Grievance Redressal Policy", "PDF", "assets/docs/grievance-redressal-policy.pdf")} -->
    </ul>
  </div>
  <div class="doc-group reveal"><h2>Annual Returns and Updates</h2>
    <!-- Upload each PDF to assets/docs/ and replace the pending rows with doc_row(title, meta, path). -->
    <ul class="doc-list">
      {doc_row("Annual Return – TPSL India Private Limited", "PDF · Financial year to be confirmed", "", pending=True)}
      {doc_row("Annual Return – TPSL ePayments India Private Limited", "PDF · Financial year to be confirmed", "", pending=True)}
    </ul>
  </div>
</div></section>'''
res += cta_band("Can't find what you're looking for?", "Write to us and our team will help you with the information you need.", "Contact Us")
page("resources.html", "Resources", "TPSL policies, regulatory information, annual returns and updates.", "resources", res)

# =========================================================================== CONTACT
con = page_hero([("Contact Us", None)], "Let's Connect", "Your Business. Our Payment Solutions.",
                "Whether you're looking for payment solutions, exploring a partnership or seeking assistance, we're here to help. Connect with TPSL to discover how our payment technology can support your business.")
con += f'''<section class="section"><div class="container contact-grid">
  <div>
    <div class="info-card"><h3>TPSL India Private Limited</h3><p>{ADDRESS_HTML}</p><p>CIN: {ENTITIES[0]["cin"]}<br>GST No. {ENTITIES[0]["gst"]}</p><p>Tel: <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p><p>Customer support: <a href="tel:18602332332">1860 233 2332</a></p><p><a href="mailto:customer_support@mail.tpsl-india.co.in">customer_support@mail.tpsl-india.co.in</a></p></div>
    <div class="info-card"><h3>TPSL ePayments India Private Limited</h3><p>{ADDRESS_HTML}</p><p>CIN: {ENTITIES[1]["cin"]}<br>GST No. {ENTITIES[1]["gst"]}</p><p>Tel: <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p><p>Customer service: <a href="tel:+912267664481">022-67664481</a></p><p><a href="mailto:grievance@mail.tpsl-india.co.in">grievance@mail.tpsl-india.co.in</a></p></div>
    <div class="info-card"><h3>Corporate enquiries</h3><p>Tel: <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p></div>
    <p class="muted">For complaints, please follow the <a href="support.html#grievance">grievance redressal process</a>.</p>
  </div>
  <div>{enquiry_form("contact-form")}</div>
</div></section>'''
page("contact.html", "Contact Us", "Contact TPSL for payment solutions, partnerships or assistance.", "contact", con)

# =========================================================================== LEGAL
def legal(filename, title, desc, intro, sections, review_note=True):
    toc = "".join(f'<li><a href="#{sid}">{h}</a></li>' for sid, h, _ in sections)
    body = "".join(f'<h2 id="{sid}">{h}</h2>{content}' for sid, h, content in sections)
    note = "<!-- DRAFT: to be reviewed and approved by TPSL Legal/Compliance before go-live. -->" if review_note else ""
    html = page_hero([(title, None)], "Legal &amp; Policies", title, intro) + f'''{note}
<section class="section"><div class="container legal">
  <p class="updated">Last updated: {UPDATED}</p>
  <nav class="toc" aria-label="Contents"><strong>Contents</strong><ol>{toc}</ol></nav>
  {body}
</div></section>'''
    page(filename, title, desc, "", html)


GRO = f'''<p><strong>Grievance Officer / Data Protection contact</strong><br>
Name: {ph("Name")}<br>Designation: {ph("Designation")}<br>
Email: {ph("privacy@tpsl.in or designated mailbox")}<br>
Address: {ADDRESS_HTML.replace("<br>", " ")}<br>Tel: <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>'''

privacy_sections = [
    ("scope", "Scope of this Policy", f'''<p>This Privacy Policy explains how TPSL India Private Limited and TPSL ePayments India Private Limited (together, "TPSL", "we", "us" or "our") collect, use, share and protect information when you visit <a href="{SITE}/">{SITE.replace("https://", "")}</a> (the "Website") or contact us through it.</p>
<p>This policy covers the Website only. Payment transactions processed through TPSL's products are governed by the terms and privacy notices that apply to those services and by the merchant or bank through which you transact.</p>
<p>By using the Website you acknowledge this policy. Where we rely on your consent (for example, when you submit an enquiry), we ask for it clearly and you may withdraw it at any time.</p>'''),
    ("collect", "1. Information We Collect", '''<h3>Information you provide directly</h3>
<p>When you submit an enquiry through the contact form we collect your full name, company name, business email address, contact number, the nature of your enquiry and your message. When you write to our support or grievance mailboxes we receive the details you choose to include.</p>
<p>Please do not send card numbers, PIN, CVV, OTP, passwords or bank account credentials through the Website or by email. TPSL will never ask you for them.</p>
<h3>Analytics information</h3>
<p>The Website does not currently use third-party analytics or advertising tools. If we introduce analytics in future, it will be used only to measure traffic and usage trends in aggregated form so that individual users cannot be identified, and this policy will be updated before it is enabled.</p>
<h3 id="cookies">Cookies and similar technologies</h3>
<p>The Website does not set advertising or tracking cookies. It uses your browser's local storage only to remember that you have seen the cookie notice and any accessibility preferences you choose (larger text, higher contrast, underlined links). This information stays on your device and is not sent to us. You can clear it at any time through your browser settings.</p>
<h3>Log file information</h3>
<p>Like most websites, our web servers automatically record certain information when you visit, such as your IP address, browser type, referring page, pages viewed, date and time of the request. These logs are used for security, troubleshooting and to keep the Website available.</p>
<h3>Device identifiers</h3>
<p>The Website does not collect advertising IDs or other persistent device identifiers.</p>'''),
    ("use", "2. How We Use Your Information", '''<p>We use the information described above to:</p>
<ul><li>respond to your enquiry and connect you with the right team;</li>
<li>handle support requests and grievances and keep a record of how they were resolved;</li>
<li>operate, secure and improve the Website, including detecting and preventing fraud, abuse and security incidents;</li>
<li>diagnose and fix technical problems; and</li>
<li>comply with applicable laws, regulations and directions of regulatory authorities, including the Reserve Bank of India.</li></ul>
<p>We do not use your information for automated decision-making, and we do not send you promotional communications unless you have asked us to.</p>'''),
    ("sharing", "3. Sharing of Your Information", '''<p>We will not rent or sell your information to third parties.</p>
<p>We may share your information with:</p>
<ul><li><strong>Group entities and service providers</strong> that help us operate the Website and respond to enquiries (for example, hosting, email and IT support providers). They may access your information only to perform these tasks on our behalf and are bound by obligations of confidentiality and security consistent with this policy.</li>
<li><strong>Regulators, courts and law enforcement</strong> where we believe in good faith that disclosure is required by law, regulation or legal process, or is necessary to detect, prevent or respond to fraud, illegal activity, security issues, or to protect the rights, property or safety of TPSL, our customers or the public.</li></ul>'''),
    ("store", "4. How We Store Your Information", '''<h3>Storage and processing</h3>
<p>Information collected through the Website is stored and processed on servers located in India. We use reasonable security practices and procedures, including encryption of data in transit (HTTPS/TLS), access controls and security monitoring, to protect your information. However, no method of transmission over the internet or electronic storage is completely secure, and we cannot guarantee absolute security.</p>
<h3>How long we keep your information</h3>
<p>We keep enquiry information only for as long as needed to respond to you and for the purposes described in this policy, after which it is deleted or anonymised, unless a longer period is required by law or regulation. Server logs are retained for a limited period for security and audit purposes. Information may also remain in backups for a reasonable period before it is overwritten.</p>'''),
    ("rights", "5. Your Rights and Choices", '''<p>Subject to applicable law, including the Digital Personal Data Protection Act, 2023, you may:</p>
<ul><li>request a summary of the personal data we hold about you;</li>
<li>ask us to correct, complete or update it;</li>
<li>ask us to erase it where it is no longer needed;</li>
<li>withdraw consent you have given (this does not affect processing already carried out); and</li>
<li>raise a grievance about how your data has been handled.</li></ul>
<p>To exercise these rights, contact us using the details below. We may need to verify your identity before acting on a request.</p>'''),
    ("children", "6. Children", '<p>The Website is intended for businesses and is not directed at children. We do not knowingly collect personal data from anyone under 18 years of age.</p>'),
    ("links", "7. Links to Other Websites", '<p>The Website contains links to government and third-party websites (for example, the National Cyber Crime Reporting Portal and Sanchar Saathi). We are not responsible for the content or privacy practices of those websites, and we encourage you to read their privacy policies.</p>'),
    ("changes", "8. Changes to this Policy", '<p>We may update this policy from time to time. The "Last updated" date at the top of this page shows when it was last revised. Material changes will be highlighted on the Website.</p>'),
    ("contact", "9. How to Contact Us", f'''<p>If you have questions about this policy or wish to raise a privacy concern, please contact:</p>{GRO}
<p>For complaints about TPSL's services, please follow the <a href="support.html#grievance">grievance redressal process</a>.</p>'''),
]
legal("privacy-policy.html", "Privacy Policy", "How TPSL collects, uses, shares and protects information on its website.",
      "How TPSL collects, uses, shares and protects information when you use this website.", privacy_sections)

terms_sections = [
    ("acceptance", "1. Acceptance of Terms", '<p>These Terms &amp; Conditions govern your use of this website (the "Website"), operated by TPSL India Private Limited and TPSL ePayments India Private Limited ("TPSL"). By accessing or using the Website you agree to these terms. If you do not agree, please do not use the Website.</p>'),
    ("info", "2. Information on the Website", '<p>The Website provides general information about TPSL and its products and services. Product features, availability and commercial terms may vary and are subject to separate agreements, eligibility criteria and applicable regulatory requirements. Nothing on the Website constitutes an offer to provide any service.</p>'),
    ("use", "3. Acceptable Use", '<p>You agree not to: use the Website for any unlawful purpose; attempt to gain unauthorised access to any part of the Website or its systems; introduce malware or carry out any activity that could damage, overload or impair the Website; scrape or harvest information by automated means; or submit false or misleading information through the enquiry form.</p>'),
    ("ip", "4. Intellectual Property", '<p>All content on the Website, including text, graphics, logos and design, is owned by or licensed to TPSL and is protected by applicable intellectual property laws. You may view and print pages for personal, non-commercial reference only. No other use is permitted without TPSL\'s prior written consent.</p>'),
    ("third", "5. Third-Party Links", '<p>Links to third-party websites are provided for convenience. TPSL does not control and is not responsible for the content, availability or practices of those websites.</p>'),
    ("privacy", "6. Privacy", '<p>Your use of the Website is also governed by our <a href="privacy-policy.html">Privacy Policy</a>.</p>'),
    ("liability", "7. Limitation of Liability", '<p>To the fullest extent permitted by law, TPSL shall not be liable for any indirect, incidental, special or consequential loss arising from your use of, or inability to use, the Website or reliance on its content.</p>'),
    ("law", "8. Governing Law and Jurisdiction", f'<p>These terms are governed by the laws of India. Courts at Mumbai shall have exclusive jurisdiction over any dispute arising from them.</p>'),
    ("changes", "9. Changes", '<p>TPSL may revise these terms at any time by updating this page. Continued use of the Website after changes are posted means you accept the revised terms.</p>'),
    ("contact", "10. Contact", '<p>Questions about these terms may be sent through our <a href="contact.html">Contact Us</a> page.</p>'),
]
legal("terms-and-conditions.html", "Terms &amp; Conditions", "Terms and conditions for using the TPSL website.",
      "The terms that apply when you access and use this website.", terms_sections)

disc_sections = [
    ("general", "1. General Information Only", '<p>The information on this website is provided by TPSL for general informational purposes only. While we take reasonable care to keep it accurate and up to date, we make no representations or warranties of any kind, express or implied, about its completeness, accuracy, reliability or suitability for any purpose.</p>'),
    ("products", "2. Products and Services", '<p>Descriptions of products and services, including features, illustrations and device images, are indicative and may differ from the final product. Availability of any product or service is subject to TPSL\'s internal policies, partner bank requirements, applicable laws and regulatory approvals, and to the execution of separate agreements.</p>'),
    ("fraud", "3. Beware of Fraud", '<p>TPSL will never ask you for your card number, PIN, CVV, OTP, passwords or bank account credentials by phone, SMS, email or social media. Do not share these details with anyone claiming to represent TPSL. If you suspect fraud, call the national cybercrime helpline <a href="tel:1930">1930</a> or report it at <a href="https://cybercrime.gov.in/" rel="noopener noreferrer" target="_blank">cybercrime.gov.in</a>.</p>'),
    ("marks", "4. Trademarks", '<p>Names of card networks, payment systems and other third parties mentioned on this website belong to their respective owners and are used for identification only.</p>'),
    ("availability", "5. Website Availability", '<p>We aim to keep the website available at all times but are not responsible if it is temporarily unavailable due to technical issues or maintenance.</p>'),
]
legal("disclaimer.html", "Disclaimer", "Disclaimer for the TPSL website.", "Important information about the content of this website.", disc_sections)

# =========================================================================== utility pages
page("thank-you.html", "Thank You", "Your enquiry has been received.", "", page_hero([("Thank You", None)], "Enquiry received", "Thank you for contacting TPSL",
     "Your enquiry has been received and our team will get in touch with you shortly.") + '<section class="section-sm"><div class="container"><a class="btn btn-primary" href="index.html">Back to Home</a></div></section>', noindex=True)
page("404.html", "Page Not Found", "The page you are looking for could not be found.", "", page_hero([("Page not found", None)], "Error 404", "We couldn't find that page",
     "The page may have moved or no longer exists.") + '<section class="section-sm"><div class="container"><a class="btn btn-primary" href="index.html">Go to Home</a> <a class="btn btn-outline" href="contact.html">Contact Us</a></div></section>', noindex=True)

# =========================================================================== sitemap / robots
pages = ["", "offerings.html", "in-store-payments.html", "online-payments.html", "cross-border-payments.html", "value-added-services.html", "resources.html",
         "support.html", "contact.html", "privacy-policy.html", "terms-and-conditions.html", "disclaimer.html"]
today = datetime.date.today().isoformat()
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
    f"  <url><loc>{SITE}/{p}</loc><lastmod>{today}</lastmod></url>\n" for p in pages) + "</urlset>\n"
open(os.path.join(OUT, "sitemap.xml"), "w").write(sm)
open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nDisallow: /enquiry.php\nDisallow: /thank-you.html\n\nSitemap: {SITE}/sitemap.xml\n")
print("built", len(pages) + 2, "pages")
