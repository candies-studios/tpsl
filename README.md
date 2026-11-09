# TPSL Website

Static website for TPSL (www.tpsl.in), built from *TPSL Complete Website Content*.

## Folder structure

```
(repo root)                  ← these files are the website; upload them to the web root
  index.html                 Home
  offerings.html             Our Offerings (overview)
  in-store-payments.html     POS Terminals, Soft POS, Sound Box
  online-payments.html       Payment Gateway, Recurring Payments, Payment Links
  cross-border-payments.html International card acceptance, settlements, benefits
  value-added-services.html  Merchant Hub, Onboarding, DCC, UPI, Transit, Embedded
  resources.html             Policies & regulatory info, annual returns
  support.html               Grievance redressal matrix, MNRL rules, complaint steps
  contact.html               Contact details + enquiry form
  privacy-policy.html        Privacy Policy (RBI policy structure + DPDP Act 2023)
  terms-and-conditions.html  Terms & Conditions (draft, for legal review)
  disclaimer.html            Disclaimer (draft, for legal review)
  thank-you.html, 404.html   Utility pages
  enquiry.php                Contact form handler (the only server-side code)
  robots.txt, sitemap.xml, favicon.ico, .well-known/security.txt
  assets/css, js, fonts, img, docs
server-config/               nginx server block, TLS snippet, Apache .htaccess
build/build.py               Generator for all HTML pages (edit content here)
DEPLOYMENT_AND_DNS.md        Hosting, DNS, SSL and go-live requirements for TPSL IT
```

## Design notes
- **Logo:** the lowercase `tpsl` wordmark in Sora, with an orange "pixel" full stop (`assets/img/tpsl-logo.svg`, white version `tpsl-logo-white.svg`). The letters are vector outlines, so the logo renders the same everywhere.
- **Colours** follow the BillDesk reference: white canvas, near-black text, burnt-orange `#C14C23` buttons, orange `#F15A22` and amber `#FFB23F` accents, and a peach `#FDEEE4` footer.
- **Illustrations** are original, unbranded SVGs. Replace them with real product photos when available, keeping the same file names or updating `build.py`.

## RBI / privacy & security alignment
- The Privacy Policy follows the section structure of the RBI website privacy policy: information collected (provided directly, analytics, cookies, log files, device identifiers), how it is used, sharing (no rent/sale), storage and processing in India, retention, and contact. It adds DPDP Act 2023 rights and a Grievance Officer.
- There are no third-party trackers, analytics, fonts or CDNs. All assets are self-hosted, which makes a strict Content-Security-Policy possible.
- The enquiry form asks for explicit consent and states the purpose. It warns users not to share card/PIN/OTP, rejects card-number-like input, and has a honeypot, rate limiting and same-origin checks. Nothing is stored; enquiries are emailed.
- The cookie notice reflects actual behaviour: only essential local storage is used.
- Fraud-safety messaging appears on every page, along with the 1930 and cybercrime.gov.in references.
- Accessibility: skip link, keyboard-navigable menus, ARIA labels, visible focus, reduced-motion support, and a text size / contrast / link underline panel (GIGW / WCAG-friendly).
- Server config enforces TLS 1.2+, HSTS, CSP, X-Frame-Options, nosniff, Referrer-Policy and Permissions-Policy. Only `enquiry.php` can execute.

## Before go-live: fill in
Search the HTML for `placeholder` (yellow `[ ]` on the page) and `TODO`:
- Registered office addresses, CIN and phone numbers (footer and Contact page) for both entities
- Grievance Officer details (Privacy Policy, section 9)
- Jurisdiction city (Terms, section 8)
- LinkedIn URL (`LINKEDIN` in `build/build.py`)
- `RECIPIENTS` / `FROM_ADDRESS` in `enquiry.php`
- Annual return PDFs: upload to `assets/docs/`, then edit the Resources section in `build.py`
- Security contact in `.well-known/security.txt`

To edit content, change `build/build.py` and run `python3 build/build.py` (Python 3.8+, no packages needed). This rewrites the HTML files in `public_html/`.

## Content notes for TPSL to confirm
- The UPI section says "Worldline SuperApp" exactly as written in the content document. Please confirm this name is still correct.
- The POS and Sound Box carousels show four illustrative device types each. Please confirm the actual models offered.
