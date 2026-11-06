<?php
// Server-side proxy to EnsoTraffic webmaster API (push.json). The API token stays on the server.
header('Content-Type: application/json; charset=utf-8');
$TOKEN = getenv('ENSO_TOKEN'); $FLOW = getenv('ENSO_FLOW'); $OFFER = getenv('ENSO_OFFER');
function out($ok, $msg = '') { echo json_encode(['status' => $ok ? 'ok' : 'error', 'message' => $msg], JSON_UNESCAPED_UNICODE); exit; }
$in = json_decode(file_get_contents('php://input'), true) ?: [];
if (!empty($in['website'])) out(true);                       // honeypot
if (empty($in['consent'])) out(false, 'Потрібна згода на передачу та обробку даних.');
$phone = preg_replace('/\D+/', '', $in['phone'] ?? '');
if (strlen($phone) == 10 && $phone[0] == '0') $phone = '38' . $phone;
elseif (strlen($phone) == 9) $phone = '380' . $phone;
if (strlen($phone) < 6 || strlen($phone) > 15) out(false, 'Перевірте номер телефону.');
$ip = $_SERVER['HTTP_CF_CONNECTING_IP'] ?? $_SERVER['REMOTE_ADDR'];
$d = ['flow' => $FLOW, 'offer' => $OFFER, 'ip' => $ip, 'phone' => $phone,
      'name' => mb_substr(trim($in['name'] ?? ''), 0, 120), 'ua' => $_SERVER['HTTP_USER_AGENT'] ?? '',
      'country' => 'ua', 'mobile' => empty($in['mobile']) ? 0 : 1];
foreach (['utm_source','utm_medium','utm_campaign','utm_content','utm_term'] as $k)
  if (!empty($in[$k])) $d[$k] = substr($in[$k], 0, 255);
if (!empty($in['gclid'])) $d['sub1'] = substr($in['gclid'], 0, 255);
if (!empty($in['fbclid'])) $d['sub2'] = substr($in['fbclid'], 0, 255);
$ch = curl_init('https://ensotraffic.tech/api/wm/push.json?id=' . urlencode($TOKEN));
curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_POSTFIELDS => http_build_query($d), CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15]);
$r = json_decode(curl_exec($ch), true); curl_close($ch);
// consent log (time, ip, text version) — keep as proof of consent
file_put_contents(__DIR__ . '/consent.log', json_encode(['t' => date('c'), 'ip' => $ip, 'v' => $in['consent_v'] ?? '', 'lead' => $r['id'] ?? null]) . "\n", FILE_APPEND | LOCK_EX);
if (($r['status'] ?? '') === 'ok') out(true);
$e = $r['error'] ?? 'db';
$map = ['duplicate' => 'Такий запит уже надіслано. Дякуємо!', 'phone' => 'Перевірте номер телефону.', 'nophone' => 'Перевірте номер телефону.',
        'email' => 'Перевірте email.', 'traffic' => 'Пропозиція тимчасово недоступна.', 'ban' => 'Не вдалося прийняти запит.', 'db' => 'Тимчасова помилка. Спробуйте ще раз.'];
// access, key, noflow, badflow, no-api, offer, security, data = configuration problems: log, show generic text
if (!isset($map[$e])) error_log('EnsoTraffic error: ' . json_encode($r));
out(false, $map[$e] ?? 'Не вдалося надіслати запит. Спробуйте пізніше.');
