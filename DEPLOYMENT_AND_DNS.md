# TPSL Website — Hosting, DNS & Go-Live Requirements

Prepared for: TPSL IT / Infrastructure team (tpsl.in, managed on Cloudflare)
Website type: static HTML/CSS/JS site + one small PHP form handler (`enquiry.php`)

TPSL will keep control of the Cloudflare account, so this pack is written so that **no delegated access is needed**. TPSL creates the DNS records below, and we never need a Cloudflare API token.

Values in `<ANGLE_BRACKETS>` are filled in once the server is provisioned.

---

## 1. Hosting platform / server details

| Item | Recommendation |
|---|---|
| Hosting model | Cloud VM (IaaS), **dedicated** to this website (not shared hosting) |
| Region | **India** (e.g. AWS ap-south-1 Mumbai / Azure Central India / GCP asia-south1, or TPSL's own India data centre). This keeps all website data, including form submissions and server logs, in India. |
| Size | 2 vCPU, 4 GB RAM, 40 GB SSD (the site is static, so this has plenty of headroom) |
| OS | Ubuntu Server 24.04 LTS (64-bit), auto security updates enabled |
| Web server | nginx 1.24+ (config provided: `server-config/nginx-tpsl.conf`) |
| Runtime | PHP 8.3-FPM, used **only** by `enquiry.php`. No database and no CMS. |
| Mail | SMTP relay or mailbox for the enquiry form (e.g. TPSL's Microsoft 365 / Google Workspace relay, or Amazon SES Mumbai) |
| Server name | `<SERVER_HOSTNAME>` |
| Provider / account owner | `<CLOUD_PROVIDER>` — owned by `<TPSL / vendor>` |

> If TPSL prefers to host on its own on-premises infrastructure, the same spec and config apply. We would need SSH/VPN access to the VM, or TPSL's team can deploy using the steps in section 7.

## 2. Public IP address(es) of the web server

| Type | Value |
|---|---|
| IPv4 (static / Elastic IP) | `<PUBLIC_IPV4>` |
| IPv6 (optional) | `<PUBLIC_IPV6>` (only if enabled) |

These will be shared as soon as the VM is provisioned. The IP is static, so it won't change on reboot.

## 3. DNS entries required (to be created by TPSL in Cloudflare)

### 3.1 Website publishing

| Type | Name | Content | Proxy status | TTL |
|---|---|---|---|---|
| A | `tpsl.in` (@) | `<PUBLIC_IPV4>` | Proxied (orange cloud), see 3.3 | Auto |
| A | `www` | `<PUBLIC_IPV4>` | Proxied | Auto |
| AAAA | `@` and `www` | `<PUBLIC_IPV6>` | Proxied | Auto (only if IPv6 is used) |

`www.tpsl.in` is the primary address. `tpsl.in` permanently redirects (301) to `https://www.tpsl.in`. The redirect is handled on the server, so no Cloudflare page rule is required.

**Before switching:** please check whether any existing `@` / `www` records point to the current website or another service. We will agree a cut-over time with you and lower the TTL beforehand if the records are not proxied.

### 3.2 SSL certificate

Choose **one** of the options below. Option A is recommended.

**Option A — Cloudflare proxy + Cloudflare Origin Certificate (recommended)**
1. TPSL generates an Origin Certificate in Cloudflare (SSL/TLS → Origin Server) for `tpsl.in` and `*.tpsl.in`, 15-year validity, RSA 2048 or ECDSA.
2. TPSL shares the certificate (`.pem`) and private key through a secure channel, such as a password-protected archive with the password sent separately, or by placing them directly on the server.
3. In Cloudflare, TPSL sets:
   - SSL/TLS encryption mode: **Full (strict)**
   - Always Use HTTPS: **On**
   - Minimum TLS Version: **1.2**
   - TLS 1.3: **On**
   - HSTS: can be enabled after go-live is verified (the server also sends HSTS)

Visitors then see Cloudflare's edge certificate, which Cloudflare manages and renews automatically. The origin certificate encrypts traffic between Cloudflare and our server.

**Option B — TPSL's own commercial / wildcard certificate**
TPSL provides `fullchain` (certificate + intermediate) and the private key for `www.tpsl.in` and `tpsl.in`, or a `*.tpsl.in` wildcard. Cloudflare can still proxy in Full (strict) mode. If the CA requires DNS validation, we will send TPSL the exact TXT/CNAME validation record to add.

**Option C — Let's Encrypt on the server (no DNS change needed for validation)**
The server obtains and auto-renews the certificate using HTTP-01 validation on `/.well-known/acme-challenge/`. This works with the records in 3.1 as they are and needs no DNS access.

**CAA record (recommended for all options).** Restrict which CAs can issue certificates for tpsl.in. Keep any CAA records already in use and add only what is missing:

| Type | Name | Content |
|---|---|---|
| CAA | `@` | `0 issue "<ca-domain>"` (for example `digicert.com`, `sectigo.com` or `letsencrypt.org`, depending on the option chosen). With Option A, Cloudflare's edge CAs must also be allowed. Cloudflare adds these automatically when Universal SSL is on. |
| CAA | `@` | `0 iodef "mailto:<security mailbox>"` |

### 3.3 Records for the enquiry form email

The contact form sends mail from `no-reply@tpsl.in` to TPSL's sales mailbox. To stop these emails landing in spam:

| Type | Name | Content | Notes |
|---|---|---|---|
| TXT (SPF) | `@` | Add `include:<relay SPF domain>` or `ip4:<PUBLIC_IPV4>` to the **existing** SPF record | A domain must have only **one** SPF record, so merge this into the current one rather than adding a second |
| TXT / CNAME (DKIM) | `<selector>._domainkey` | Supplied by the chosen mail relay | Only if a relay such as SES or M365 is used |

If TPSL would rather the form send through its existing Microsoft 365 / Google Workspace tenant, we just need SMTP relay details and no SPF change is required.

### 3.4 Records we do NOT need
- No NS delegation, sub-zone or Cloudflare account access
- No MX changes. TPSL's existing email is not touched.

## 4. Web hosting environment

| Item | Detail |
|---|---|
| Environment | Public cloud IaaS (dedicated VM), India region. Can also run on TPSL on-premises. |
| Architecture | Visitor → Cloudflare (WAF/CDN/TLS) → nginx on VM (TLS) → static files; `enquiry.php` → SMTP relay |
| Data stored | None. Form submissions are emailed, not stored. A short-lived hashed rate-limit counter is the only thing written to disk. |
| Third-party scripts | None. Fonts and images are self-hosted, and there are no analytics or trackers. |
| Inbound firewall | 443/TCP and 80/TCP (redirect + ACME only). With Option A, restrict 80/443 to **Cloudflare IP ranges only** (https://www.cloudflare.com/ips/). 22/TCP only from TPSL/vendor admin IPs or VPN. |
| Outbound | 587/TCP to the SMTP relay, 443 for OS updates |

## 5. Additional technical prerequisites for go-live

**From TPSL (content and compliance):**
1. Registered office addresses, CIN and phone numbers for TPSL India Pvt Ltd and TPSL ePayments India Pvt Ltd. These are marked as yellow `[placeholders]` on the site.
2. Grievance Officer / Data Protection contact (name, designation, email) for the Privacy Policy.
3. Legal/Compliance review and sign-off of the Privacy Policy, Terms & Conditions and Disclaimer pages. The drafts follow the structure of the RBI website privacy policy and the DPDP Act, 2023.
4. PDFs for the Resources page: annual returns and any policies to be published.
5. TPSL LinkedIn page URL, and the mailbox(es) that should receive website enquiries.
6. Optional: real product photos of terminals and sound boxes to replace the illustrations.

**Security and regulatory:**
7. VAPT / security audit of the site before go-live. We recommend a CERT-In empanelled auditor, and we will fix any findings.
8. Server logs kept for a rolling **180 days within India**, and server time synced to NTP (NIC/NPL servers or the cloud provider's NTP), in line with CERT-In Directions of 28 April 2022.
9. Cloudflare WAF managed rules on, plus a rate-limiting rule on `/enquiry.php` (e.g. 10 requests/minute per IP).
10. Daily VM snapshot or backup with 7–30 days retention.
11. Uptime monitoring on `https://www.tpsl.in`.

## 6. Go-live checklist

- [ ] VM provisioned, OS hardened, firewall rules applied
- [ ] Site deployed; nginx config tested (`nginx -t`)
- [ ] SSL installed (Option A/B/C); SSL Labs grade A or better
- [ ] DNS A/AAAA records created by TPSL; Cloudflare SSL mode set to Full (strict)
- [ ] `http://tpsl.in`, `http://www.tpsl.in` and `https://tpsl.in` all 301 to `https://www.tpsl.in`
- [ ] Security headers verified (securityheaders.com)
- [ ] Contact form delivers to the TPSL mailbox; SPF/DKIM pass
- [ ] All `[placeholders]` replaced; legal pages approved
- [ ] VAPT closed
- [ ] `sitemap.xml` submitted in Google Search Console (optional)

## 7. Deployment steps (Ubuntu 24.04)

```bash
sudo apt update && sudo apt -y upgrade
sudo apt -y install nginx php8.3-fpm unattended-upgrades
sudo mkdir -p /var/www/tpsl && sudo chown -R $USER:www-data /var/www/tpsl
# upload public_html/ to /var/www/tpsl/public_html
sudo find /var/www/tpsl -type d -exec chmod 755 {} \; && sudo find /var/www/tpsl -type f -exec chmod 644 {} \;

sudo cp server-config/tpsl-tls.conf /etc/nginx/snippets/tpsl-tls.conf
echo 'limit_req_zone $binary_remote_addr zone=tpsl_form:10m rate=10r/m;' | sudo tee /etc/nginx/conf.d/tpsl-ratelimit.conf
sudo cp server-config/nginx-tpsl.conf /etc/nginx/sites-available/tpsl.conf
sudo ln -s /etc/nginx/sites-available/tpsl.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
# place certificate files at /etc/ssl/tpsl/fullchain.pem and privkey.pem (chmod 600 on the key)
sudo nginx -t && sudo systemctl reload nginx

# PHP mail: configure sendmail_path / an SMTP relay (e.g. msmtp) in /etc/php/8.3/fpm/php.ini
# edit RECIPIENTS and FROM_ADDRESS at the top of public_html/enquiry.php
sudo ufw allow 'Nginx Full' && sudo ufw allow from <ADMIN_IP> to any port 22 && sudo ufw enable
```

For Apache hosting, use `server-config/apache-htaccess.txt` (rename it to `.htaccess` in `public_html/`).
