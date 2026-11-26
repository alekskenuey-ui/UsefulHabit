import json, subprocess, urllib.request, os, sys
KEY = open('/home/claude/.secrets/el').read().strip()
dur = lambda f: float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
OFF_FREE = '[excited, warm] А зараз акція: дві упаковки в подарунок при замовленні курсу! Оплата — при отриманні.'
OFF_LOW  = '[excited, warm] А зараз акційна ціна — від тридцяти семи гривень за упаковку при замовленні курсу! Оплата — при отриманні.'
CTA = '[friendly, confident] Залишайте заявку — консультант передзвонить і все розповість. Безкоштовно.'
SETS = {
 'halyna': ('pFZP5JQG7iQjIQuC4Bku', [
   ('l1', '[warm, slightly tired] Перекуси на бігу, пізні вечері, а попереду ще й свята…'),
   ('l2', '[honest] Я стежу за вагою, але жорсткі дієти — точно не моє.'),
   ('l3', '[warm] Тому додала Скінеформ: гарцинія, артишок, ацерола й трави.'),
   ('l4', '[calm, pleased] Тепер це моя підтримка до харчування й руху — і легкість після їжі.'),
   ('free', OFF_FREE), ('low', OFF_LOW),
   ('l6', '[happy] Почуваюся легше — і тримаю свій ритм без жорстких дієт.'),
   ('cta', CTA)]),
 'olia': ('cgSgspJ2msm6clMCkdW9', [
   ('l1', '[energetic] Стежу за вагою, але жорсткі дієти — не моє. Тому в мене три прості звички.'),
   ('l2', '[cheerful] Перша: склянка води зранку.'),
   ('l3', '[warm] Друга: нормальний сніданок — і капсула Скінеформу.'),
   ('l4', '[playful] Третя: більше кроків. Сходи замість ліфта!'),
   ('l5', '[satisfied] Галочка за галочкою — без жорстких правил.'),
   ('l6', '[warm] Гарцинія, артишок, ацерола й трави — для легкості після їжі та підтримки, коли важко тримати режим.'),
   ('free', OFF_FREE), ('low', OFF_LOW),
   ('cta', CTA)]),
 'oksana': ('cgSgspJ2msm6clMCkdW9', [
   ('l1', '[playful] Що в моїй сумці, коли весь день у роз\'їздах?'),
   ('l2', '[honest] Перекуси на бігу, вечеря о дев\'ятій… Я стежу за вагою, але жорсткі дієти — не про мій ритм.'),
   ('l3', '[smiling] Тому завжди з собою — Скінеформ.'),
   ('l4', '[warm] Гарцинія, артишок, ацерола й трави — десять рослинних компонентів.'),
   ('l5', '[calm, pleased] Для легкості після їжі та підтримки, коли важко тримати режим.'),
   ('free', OFF_FREE), ('low', OFF_LOW),
   ('cta', CTA)]),
}
who = sys.argv[1:] or list(SETS)
for p in who:
    voice, L = SETS[p]
    for i, (k, t) in enumerate(L):
        body = {'text': t, 'model_id': 'eleven_v4', 'language_code': 'uk', 'voice_settings': {'stability': 0.45, 'similarity_boost': 0.8, 'speed': 1.18}}
        req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128', data=json.dumps(body).encode(), headers={'xi-api-key': KEY, 'Content-Type': 'application/json'})
        f = f'/home/claude/v2/{p}/vo/{k}.mp3'
        open(f, 'wb').write(urllib.request.urlopen(req, timeout=120).read())
        print(p, k, round(dur(f), 2), flush=True)
