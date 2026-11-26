import json, subprocess, urllib.request
KEY = open('/home/claude/.secrets/el').read().strip()
OLIA, MILA = 'cgSgspJ2msm6clMCkdW9', 'FGY2WhTYpPnrIDTdsKH5'
dur = lambda f: float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
L = [
 ('m1', MILA, '[curious, playful] Що це в тебе? Знову якась сувора дієта?'),
 ('o1', OLIA, '[smiling, confident] Ні, без жорстких дієт! Це Скінеформ — рослинна підтримка, коли стежу за вагою.'),
 ('o2', OLIA, '[warm, informative] Всередині гарцинія, артишок, ацерола й трави — десять рослинних компонентів.'),
 ('o3', OLIA, '[warm] Для легкості після їжі — і щоб легше тримати режим, навіть коли свята й перекуси.'),
 ('m2', MILA, '[impressed] О, склад справді нормальний! А де такий замовити?'),
 ('free', OLIA, '[excited, warm] Зараз акція: дві упаковки в подарунок при замовленні курсу! І оплата — при отриманні.'),
 ('low', OLIA, '[excited, warm] Зараз акційна ціна — від тридцяти семи гривень за упаковку при замовленні курсу! І оплата — при отриманні.'),
 ('cta', OLIA, '[motivating, friendly] Почни з малого — і тримай свій ритм без жорстких дієт! Залишайте заявку: консультант передзвонить і все розповість. Безкоштовно.'),
]
for k, v, t in L:
    body = {'text': t, 'model_id': 'eleven_v4', 'language_code': 'uk', 'voice_settings': {'stability': 0.45, 'similarity_boost': 0.8, 'speed': 1.15}}
    req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{v}?output_format=mp3_44100_128', data=json.dumps(body).encode(), headers={'xi-api-key': KEY, 'Content-Type': 'application/json'})
    open(f'cafe/vo/{k}.mp3', 'wb').write(urllib.request.urlopen(req, timeout=120).read())
    print(k, round(dur(f'cafe/vo/{k}.mp3'), 2), flush=True)
