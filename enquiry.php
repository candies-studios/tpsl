<?php
/**
 * TPSL website — enquiry form handler.
 *
 * Requirements: PHP 8.1+ with a working mail transport (sendmail/postfix relay
 * or an SMTP relay configured in php.ini). Nothing is stored on disk except a
 * short-lived rate-limit counter (hashed IP) in the system temp directory.
 *
 * CONFIGURE the three constants below before go-live.
 */

declare(strict_types=1);

const RECIPIENTS    = ['sales@tpsl.in'];            // TODO: mailbox(es) that should receive enquiries
const FROM_ADDRESS  = 'no-reply@tpsl.in';           // TODO: must be a sender allowed by tpsl.in SPF/DKIM
const ALLOWED_HOSTS = ['www.tpsl.in', 'tpsl.in'];   // hosts allowed to post the form
const MAX_PER_HOUR  = 5;                             // submissions per IP per hour

header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');

$wantsJson = (isset($_SERVER['HTTP_ACCEPT']) && str_contains($_SERVER['HTTP_ACCEPT'], 'application/json'));

function respond(bool $ok, string $message, int $code = 200): never
{
    global $wantsJson;
    http_response_code($code);
    if ($wantsJson) {
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(['ok' => $ok, 'message' => $message]);
    } elseif ($ok) {
        header('Location: /thank-you.html', true, 303);
    } else {
        header('Content-Type: text/plain; charset=utf-8');
        echo $message;
    }
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST');
    respond(false, 'Method not allowed.', 405);
}

/* Same-origin check (blocks cross-site form posting). */
$origin = $_SERVER['HTTP_ORIGIN'] ?? ($_SERVER['HTTP_REFERER'] ?? '');
$originHost = $origin ? parse_url($origin, PHP_URL_HOST) : null;
if ($originHost !== null && !in_array(strtolower((string)$originHost), ALLOWED_HOSTS, true)) {
    respond(false, 'Invalid request origin.', 403);
}

/* Honeypot: real users never fill this hidden field. Pretend success for bots. */
if (!empty($_POST['website'])) {
    respond(true, 'Thank you.');
}

/* Rate limit per IP (hashed; no raw IP is written to disk). */
$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$bucket = sys_get_temp_dir() . '/tpsl_rl_' . hash('sha256', $ip . date('YmdH'));
$count = is_file($bucket) ? (int)file_get_contents($bucket) : 0;
if ($count >= MAX_PER_HOUR) {
    respond(false, 'Too many submissions. Please try again later.', 429);
}
@file_put_contents($bucket, (string)($count + 1), LOCK_EX);

/* Validate input. */
function field(string $key, int $max): string
{
    $v = trim((string)($_POST[$key] ?? ''));
    $v = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $v) ?? '';
    return mb_substr($v, 0, $max);
}
function oneLine(string $v): string
{
    return trim(preg_replace('/[\r\n]+/', ' ', $v) ?? '');
}

$name    = oneLine(field('full_name', 100));
$company = oneLine(field('company', 150));
$email   = oneLine(field('email', 150));
$phone   = oneLine(field('phone', 16));
$type    = oneLine(field('enquiry_type', 80));
$message = field('message', 2000);
$consent = ($_POST['consent'] ?? '') === 'yes';

$allowedTypes = [
    'In-Store Payments (POS, Soft POS, Sound Box)',
    'Online Payments (Gateway, Recurring, Payment Links)',
    'Cross-Border Payments', 'Value Added Services', 'Partnership', 'Existing Merchant Support', 'Other',
];

$errors = [];
if ($name === '')                                         $errors[] = 'name';
if ($company === '')                                      $errors[] = 'company';
if (!filter_var($email, FILTER_VALIDATE_EMAIL))           $errors[] = 'email';
if (!preg_match('/^\+?[0-9][0-9\s-]{7,15}$/', $phone))    $errors[] = 'phone';
if (!in_array($type, $allowedTypes, true))                $errors[] = 'enquiry type';
if ($message === '')                                      $errors[] = 'message';
if (!$consent)                                            $errors[] = 'consent';

if ($errors) {
    respond(false, 'Please check the following: ' . implode(', ', $errors) . '.', 422);
}

/* Reject messages that look like they contain card numbers (PCI hygiene). */
if (preg_match('/\b(?:\d[ -]?){13,19}\b/', $message)) {
    respond(false, 'For your security, please do not include card or account numbers in your message.', 422);
}

$body = "New website enquiry\n"
      . "-------------------\n"
      . "Name:         {$name}\n"
      . "Company:      {$company}\n"
      . "Email:        {$email}\n"
      . "Phone:        {$phone}\n"
      . "Enquiry type: {$type}\n"
      . "Submitted:    " . gmdate('Y-m-d H:i:s') . " UTC\n\n"
      . "Message:\n{$message}\n";

$headers = [
    'From: TPSL Website <' . FROM_ADDRESS . '>',
    'Reply-To: ' . $email,
    'Content-Type: text/plain; charset=UTF-8',
    'X-Mailer: TPSL-Website',
];

$subject = '=?UTF-8?B?' . base64_encode('Website enquiry: ' . $type . ' – ' . $company) . '?=';
$sent = mail(implode(',', RECIPIENTS), $subject, $body, implode("\r\n", $headers), '-f' . FROM_ADDRESS);

if (!$sent) {
    error_log('TPSL enquiry: mail() failed');
    respond(false, 'We could not submit your enquiry right now. Please try again or write to us directly.', 500);
}

respond(true, 'Thank you. Your enquiry has been received.');
