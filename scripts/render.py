import math, subprocess, wave, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
PERSON, OFFER = sys.argv[1], sys.argv[2]          # halyna|oksana , free|low
W, H, FPS = 1080, 1920, 30
F = "/usr/share/fonts/opentype/inter/"
FOREST = (22, 66, 37); EMERALD = (16, 185, 129); WHITE = (255, 255, 255); AMBER = (255, 196, 61)
SRC = f'/home/claude/{PERSON}'; D = f'/home/claude/v2/{PERSON}'; A = '/home/claude/usefulhabit/assets/'
TMP = f'{D}/{OFFER}'; subprocess.run(['mkdir', '-p', TMP])
TEMPO = 1.18 if PERSON == 'olia' else 1.1
def font(n, s): return ImageFont.truetype(F + n, s)
def tw(d, t, f): b = d.textbbox((0, 0), t, font=f); return b[2] - b[0], b[3] - b[1], b[1]
def eo(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def eio(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def back(x, s=1.7):
    x = min(max(x, 0), 1); x -= 1; return x * x * ((s + 1) * x + s) + 1
def dur(f): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
def fade(img, a):
    if a >= 1: return img
    img = img.copy(); img.putalpha(img.getchannel('A').point(lambda v: int(v * a))); return img
def cover(path):
    im = Image.open(path).convert('RGB'); sw, sh = im.size; tg = 9 / 16
    if sw / sh > tg: nw = int(sh * tg); im = im.crop(((sw - nw) // 2, 0, (sw - nw) // 2 + nw, sh))
    else: nh = int(sw / tg); im = im.crop((0, (sh - nh) // 2, sw, (sh - nh) // 2 + nh))
    return im
def blurred(im): return Image.blend(im.filter(ImageFilter.GaussianBlur(22)), Image.new('RGB', im.size, (236, 246, 240)), 0.45)

# ---------------- сценарії ----------------
if PERSON == 'halyna':
    S = [dict(t='photo', img='s1', vo='l1', cap=['Перекуси, пізні вечері,', 'а ще свята…'], mv=(1.10, 1.0, .5, .42)),
         dict(t='photo', img='s2', vo='l2', cap=['Стежу за вагою,', 'але дієти — не моє'], mv=(1.0, 1.10, .45, .5)),
         dict(t='comp', img='s2', vo='l3', title=['10 рослинних', 'компонентів']),
         dict(t='ben', img='s4', vo='l4'),
         dict(t='offer', img='s5b', vo=OFFER, mv=(1.08, 1.0, .5, .55)),
         dict(t='photo', img='s6', vo='l6', cap=['Мій ритм —', 'без жорстких дієт'], mv=(1.0, 1.12, .5, .45))]
    CUT = 'halyna_cut.png'
elif PERSON == 'olia':
    SRC = '/home/claude/olia2'
    S = [dict(t='photo', img='s1', vo='l1', chk=True, mv=(1.12, 1.0, .5, .55)),
         dict(t='photo', img='s2', vo='l2', chk=True, mv=(1.0, 1.10, .5, .5)),
         dict(t='photo', img='s3', vo='l3', chk=True, mv=(1.0, 1.10, .5, .55)),
         dict(t='photo', img='s4', vo='l4', chk=True, mv=(1.15, 1.10, .58, .7)),
         dict(t='photo', img='s5', vo='l5', chk=True, cap=['Без жорстких правил'], capy=690, mv=(1.0, 1.10, .5, .55)),
         dict(t='ben', img='s3', vo='l6'),
         dict(t='offer', img='s3', vo=OFFER, mv=(1.10, 1.0, .5, .6))]
    CUT = 'olia_cut.png'
else:
    S = [dict(t='photo', img='s1', vo='l1', cap=['Що в моїй сумці?'], mv=(1.10, 1.0, .5, .45)),
         dict(t='photo', img='s2', vo='l2', cap=['Перекуси на бігу,', 'вечеря о 21:00…'], mv=(1.0, 1.12, .5, .58)),
         dict(t='photo', img='s3', vo='l3', cap=['А це — Skineform'], mv=(1.0, 1.15, .5, .55)),
         dict(t='comp', img='s3', vo='l4', title=['Рослинний', 'комплекс']),
         dict(t='ben', img='s4', vo='l5'),
         dict(t='offer', img='s5', vo=OFFER, mv=(1.08, 1.0, .5, .45))]
    CUT = 'oksana_cut.png'
NS = len(S)
for s in S:
    im = cover(f'{SRC}/sc/{s["img"]}.jpg'); s['im'] = blurred(im) if s['t'] in ('comp', 'ben') else im
    s.setdefault('mv', (1.05, 1.05, .5, .5))

# ---------------- озвучка ----------------
def prep(k):
    out = f'{TMP}/{k}.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{D}/vo/{k}.mp3', '-af',
        f'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse,rubberband=tempo={TEMPO}:pitchq=quality',
        '-ar', '48000', '-ac', '1', out], check=True)
    return out, dur(out)
VOF = [prep(s['vo']) for s in S] + [prep('cta')]
PRE, POST = 0.12, 0.22
ST, VO_AT, t = [], [], 0.0
for i in range(NS):
    ST.append(t); VO_AT.append(t + PRE); t += PRE + VOF[i][1] + POST
END0 = t - 0.9
VO_AT.append(t + 0.1); TOTAL = round(t + 0.1 + VOF[-1][1] + 0.9, 2); ST.append(TOTAL)
print(PERSON, OFFER, 'TOTAL', TOTAL, flush=True)

def kb(img, z, cx, cy):
    sw, sh = img.size; cw, ch = sw / z, sh / z
    x0 = min(max(cx * sw - cw / 2, 0), sw - cw); y0 = min(max(cy * sh - ch / 2, 0), sh - ch)
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))

def words_layer(lines, t, y=250, size=74, bg=FOREST + (232,), fg=WHITE, step=0.11):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img); f = font('Inter-ExtraBold.otf', size)
    lh = size * 1.22; widths = [tw(d, l, f)[0] for l in lines]; bw = max(widths) + 100
    bh = lh * len(lines) + 56; a = eo(t / 0.25)
    if a <= 0: return img
    d.rounded_rectangle((W / 2 - bw / 2, y, W / 2 + bw / 2, y + bh), radius=40, fill=bg[:3] + (int(bg[3] * a),))
    k = 0
    for li, l in enumerate(lines):
        x = W / 2 - widths[li] / 2; yy = y + 28 + li * lh
        for wd in l.split(' '):
            p = back((t - 0.1 - k * step) / 0.3); k += 1
            ww = tw(d, wd + ' ', f)[0]
            if p > 0:
                layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(layer).text((x, yy - tw(d, l, f)[2] + 30 * (1 - p)), wd, font=f, fill=fg + (int(255 * min(p, 1)),))
                img.alpha_composite(layer)
            x += ww
    return img

# чекліст (Оля)
ROWS = ['Вода зранку', 'Сніданок + Skineform', 'Більше кроків']
CX0, CY0, CW = 165, 262, 750
def checklist(t):
    TICK = [ST[1] + 0.8, ST[2] + 1.6, ST[3] + 0.9]
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle((CX0, CY0, CX0 + CW, CY0 + 372), radius=36, fill=(255, 255, 255, 242))
    ft = font('Inter-ExtraBold.otf', 46); tt_ = 'Мої 3 звички'; w, h, o = tw(d, tt_, ft)
    d.text((W / 2 - w / 2, CY0 + 30 - o), tt_, font=ft, fill=FOREST)
    fr = font('Inter-Bold.otf', 44)
    for k, r in enumerate(ROWS):
        y = CY0 + 112 + k * 84; bx = CX0 + 48
        p = eo((t - TICK[k]) / 0.25); pop = 1 + 0.25 * math.sin(min(max((t - TICK[k]) / 0.35, 0), 1) * math.pi)
        if p > 0:
            s_ = 26 * pop; c = (bx + 28, y + 28)
            d.rounded_rectangle((c[0] - s_, c[1] - s_, c[0] + s_, c[1] + s_), radius=12, fill=EMERALD)
            d.line([(c[0] - 13, c[1] + 1), (c[0] - 3, c[1] + 11), (c[0] + 15, c[1] - 11)], fill=WHITE, width=7, joint='curve')
        else:
            d.rounded_rectangle((bx, y, bx + 56, y + 56), radius=12, outline=(150, 175, 160), width=4)
        w, h, o = tw(d, r, fr); d.text((bx + 84, y + 28 - h / 2 - o), r, font=fr, fill=(30, 110, 70) if p > 0 else (60, 70, 65))
    return img

# постійний дисклеймер угорі
DISC = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(DISC); fd = font('Inter-SemiBold.otf', 30)
dt = 'Дієтична добавка. Не є лікарським засобом'; w_, h_, o_ = tw(dd, dt, fd)
dd.rounded_rectangle((W / 2 - w_ / 2 - 26, 92, W / 2 + w_ / 2 + 26, 92 + h_ + 26), radius=24, fill=(0, 0, 0, 120))
dd.text((W / 2 - w_ / 2, 105 - o_), dt, font=fd, fill=(255, 255, 255, 235))

# склад — кружечки інгредієнтів
ING = [('ing_acerola_grape.webp', 'Ацерола'), ('ing_garcinia.webp', 'Гарцинія'), ('ing_artichoke.webp', 'Артишок'), ('ing_herbs.webp', 'Ромашка, м\'ята')]
def circ(p, label):
    im = Image.open(A + p).convert('RGB').resize((330, 330), Image.LANCZOS)
    m = Image.new('L', (330, 330), 0); ImageDraw.Draw(m).ellipse((0, 0, 330, 330), fill=255)
    out = Image.new('RGBA', (400, 470), (0, 0, 0, 0)); d = ImageDraw.Draw(out)
    d.ellipse((15, 15, 385, 385), fill=(167, 243, 208, 255)); out.paste(im, (35, 35), m)
    f = font('Inter-ExtraBold.otf', 40); w, h, o = tw(d, label, f)
    d.rounded_rectangle((200 - w / 2 - 26, 398, 200 + w / 2 + 26, 398 + h + 30), radius=30, fill=FOREST + (240,))
    d.text((200 - w / 2, 413 - o), label, font=f, fill=WHITE); return out
CIRC = [circ(*x) for x in ING]
COMP_T0 = 0.5
def comp_scene(s, tl, L):
    img = kb(s['im'], 1.05, .5, .5).convert('RGBA')
    img.alpha_composite(words_layer(s['title'], tl, y=230, size=80))
    pos = [(W / 2 - 230, 760), (W / 2 + 230, 760), (W / 2 - 230, 1290), (W / 2 + 230, 1290)]
    step = (L * 0.75 - COMP_T0) / 4
    for k, c in enumerate(CIRC):
        p = back((tl - COMP_T0 - k * step) / 0.4)
        if p <= 0: continue
        sc = max(p, 0.01); ci = c.resize((int(c.width * sc), int(c.height * sc)), Image.BICUBIC)
        img.alpha_composite(fade(ci, min(1, p)), (int(pos[k][0] - ci.width / 2), int(pos[k][1] - ci.height / 2)))
    return img

# переваги — картки з іконками
BEN = [('icon_weight', ['Коли стежу', 'за вагою']), ('icon_tea', ['Легкість', 'після їжі']), ('icon_support', ['Рослинна', 'підтримка'])]
def card(icon, lines):
    c = Image.new('RGBA', (900, 270), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    sh = Image.new('RGBA', c.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((14, 20, 886, 262), radius=60, fill=(0, 0, 0, 60)); c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d.rounded_rectangle((10, 8, 890, 250), radius=60, fill=(255, 255, 255, 250))
    ic = Image.open(A + icon + '.webp').convert('RGBA').resize((210, 210), Image.LANCZOS); c.alpha_composite(ic, (34, 24))
    f = font('Inter-ExtraBold.otf', 60); y = 129 - len(lines) * 37
    for l in lines:
        w, h, o = tw(d, l, f); d.text((290, y - o), l, font=f, fill=FOREST); y += 74
    return c
CARDS = [card(*b) for b in BEN]
BEN_T0, BEN_STEP = 0.45, 0.5
def ben_scene(s, tl, L):
    img = kb(s['im'], 1.05 + 0.04 * eio(tl / L), .5, .5).convert('RGBA')
    img.alpha_composite(words_layer(['Для чого', 'Skineform'], tl, y=230, size=80))
    for k, c in enumerate(CARDS):
        p = back((tl - BEN_T0 - k * BEN_STEP) / 0.45)
        if p <= 0: continue
        x = int(90 - 700 * (1 - p)); img.alpha_composite(fade(c, min(1, max(p, 0))), (x, 640 + k * 310))
    return img

# оферта — плашки
def pill(text, size, fg, bg):
    d0 = ImageDraw.Draw(Image.new('RGBA', (1, 1))); f = font('Inter-ExtraBold.otf', size); w, h, o = tw(d0, text, f)
    im = Image.new('RGBA', (w + 100, h + 64), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w + 100, h + 64), radius=(h + 64) // 2, fill=bg); d.text((50, 32 - o), text, font=f, fill=fg); return im
if OFFER == 'free':
    PILLS = [(pill('2 упаковки в подарунок*', 62, FOREST, AMBER + (255,)), 250), (pill('Оплата при отриманні', 56, WHITE, FOREST + (240,)), 400), (pill('*при замовленні курсу', 34, (40, 50, 45), (255, 255, 255, 225)), 535)]
    LIST = ['✓  2 упаковки в подарунок*', '✓  Оплата при отриманні', '✓  Консультація безкоштовна']
    NOTE = '*при замовленні курсу; умови назве консультант'
else:
    PILLS = [(pill('Від 37 грн за упаковку*', 64, FOREST, AMBER + (255,)), 250), (pill('Оплата при отриманні', 56, WHITE, FOREST + (240,)), 405), (pill('*при замовленні курсу', 34, (40, 50, 45), (255, 255, 255, 225)), 540)]
    LIST = ['✓  Від 37 грн за упаковку*', '✓  Оплата при отриманні', '✓  Консультація безкоштовна']
    NOTE = '*при замовленні курсу; повну вартість назве консультант'
PILL_T0, PILL_STEP = 0.3, 0.55

# фінальна картка
LOGO = Image.open('/home/claude/usefulhabit/logo.png').convert('RGBA'); LOGO = LOGO.resize((170, int(LOGO.height * 170 / LOGO.width)), Image.LANCZOS)
HC = Image.open(f'{SRC}/sc/{CUT}').convert('RGBA'); HC = HC.resize((int(HC.width * 700 / HC.height), 700), Image.LANCZOS)
PANEL = Image.new('RGBA', (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(PANEL)
py0 = 300; ph = 770
sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((80, py0 + 14, W - 80, py0 + ph + 14), radius=52, fill=(0, 0, 0, 70)); PANEL.alpha_composite(sh.filter(ImageFilter.GaussianBlur(24)))
pd.rounded_rectangle((70, py0, W - 70, py0 + ph), radius=52, fill=(255, 255, 255, 248))
y = py0 + 56; f1 = font('Inter-ExtraBold.otf', 62)
for l in ['Skineform —', 'рослинна підтримка']:
    w, h, o = tw(pd, l, f1); pd.text((W / 2 - w / 2, y - o), l, font=f1, fill=FOREST); y += 78
y += 24; f2 = font('Inter-Bold.otf', 44)
for l in LIST:
    w, h, o = tw(pd, l, f2); pd.text((W / 2 - w / 2, y - o), l, font=f2, fill=(30, 110, 70)); y += 66
y += 22; bf = font('Inter-ExtraBold.otf', 58); bt = 'Залишити заявку ↓'; bw, bh, bo = tw(pd, bt, bf)
BTN = (W / 2 - bw / 2 - 72, y, W / 2 + bw / 2 + 72, y + bh + 68)
pd.rounded_rectangle(BTN, radius=(bh + 68) / 2, fill=EMERALD); pd.text((W / 2 - bw / 2, y + 34 - bo), bt, font=bf, fill=WHITE); y += bh + 68 + 34
f3 = font('Inter-Medium.otf', 29)
for l in [NOTE, 'Дієтична добавка. Не є лікарським засобом.']:
    w, h, o = tw(pd, l, f3); pd.text((W / 2 - w / 2, y - o), l, font=f3, fill=(70, 90, 80)); y += 40

def scene(i, t):
    s = S[i]; L = (ST[i + 1] if i < NS - 1 else END0 + 0.9) - ST[i]; tl = t - ST[i]
    if s['t'] == 'comp': return comp_scene(s, tl, L)
    if s['t'] == 'ben': return ben_scene(s, tl, L)
    z0, z1, cx, cy = s['mv']; p = eio(tl / max(L, 0.1))
    img = kb(s['im'], z0 + (z1 - z0) * p, cx, cy).convert('RGBA')
    if s.get('chk'):
        a = eo((t - 0.15) / 0.35) if i == 0 else 1
        img.alpha_composite(fade(checklist(t), a), (0, int(30 * (1 - a))))
    if s.get('cap'): img.alpha_composite(words_layer(s['cap'], tl - (0.4 if s.get('chk') else 0.1), y=s.get('capy', 250), size=62 if s.get('chk') else 74))
    if s['t'] == 'offer':
        for k, (pl, yy) in enumerate(PILLS):
            a = back((tl - PILL_T0 - k * PILL_STEP) / 0.4)
            if a > 0:
                pi = pl.resize((max(1, int(pl.width * a)), max(1, int(pl.height * a))), Image.BICUBIC)
                img.alpha_composite(fade(pi, min(1, a)), (int(W / 2 - pi.width / 2), int(yy + pl.height / 2 - pi.height / 2)))
    return img

def endcard(t):
    tl = t - END0; base = scene(NS - 1, t); b = eo(tl / 0.5)
    img = Image.blend(base.convert('RGB'), base.convert('RGB').filter(ImageFilter.GaussianBlur(16)), b)
    img = Image.blend(img, Image.new('RGB', (W, H), (236, 246, 240)), 0.35 * b).convert('RGBA')
    img.alpha_composite(fade(LOGO, b), (W - LOGO.width - 60, 60))
    p = eo((tl - 0.15) / 0.45)
    if p > 0: img.alpha_composite(fade(PANEL, p), (0, int(80 * (1 - p))))
    hs = back((tl - 0.4) / 0.6)
    if hs > 0:
        bob = int(6 * math.sin(tl * 1.8)); yy = H - HC.height + int(500 * (1 - min(hs, 1.2))) + bob
        img.alpha_composite(HC, (W // 2 - HC.width // 2, yy))
    if tl > 1.4:
        pu = (math.sin((tl - 1.4) * 4) + 1) / 2; g = 6 + 12 * pu
        ring = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ring).rounded_rectangle((BTN[0] - g, BTN[1] - g, BTN[2] + g, BTN[3] + g), radius=(BTN[3] - BTN[1]) / 2 + g, outline=EMERALD + (int(140 * (1 - pu)),), width=6)
        img.alpha_composite(ring)
    return img

XF = 0.25
def frame(t):
    if t >= END0: return endcard(t).convert('RGB')
    i = max(k for k in range(NS) if t >= ST[k])
    img = scene(i, t)
    if i > 0 and t < ST[i] + XF:
        img = Image.blend(scene(i - 1, t).convert('RGB'), img.convert('RGB'), eo((t - ST[i]) / XF)).convert('RGBA')
    img.alpha_composite(DISC)
    return img.convert('RGB')

if len(sys.argv) > 3:   # режим превью: кадри в png
    for tt in map(float, sys.argv[3].split(',')): frame(min(tt, TOTAL - 0.05)).save(f'{TMP}/f_{tt}.jpg', quality=80)
    sys.exit()

# ---------------- аудіо ----------------
SR = 48000
def rw(p):
    with wave.open(p) as w: return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
N = int(TOTAL * SR); voice = np.zeros(N, np.float32)
for i, (p, _) in enumerate(VOF):
    a = rw(p); s0 = int(VO_AT[i] * SR); voice[s0:s0 + len(a)] += a[:N - s0]
tt = np.arange(N) / SR; music = np.zeros(N, np.float32)
prog = [(261.6, 329.6, 392), (220, 261.6, 329.6), (174.6, 220, 261.6), (196, 246.9, 293.7)]
bar = 2.0; t0 = 0; k = 0
while t0 < TOTAL:
    m = (tt >= t0) & (tt < min(t0 + bar + 0.5, TOTAL)); sg = tt[m] - t0; Lb = min(bar + 0.5, TOTAL - t0)
    env = np.minimum(1, sg / 0.6) * np.minimum(1, (Lb - sg) / 0.6)
    for f in prog[k % 4]: music[m] += (np.sin(2 * np.pi * f * sg) + 0.3 * np.sin(4 * np.pi * f * sg)) * env
    t0 += bar; k += 1
for j in range(int(TOTAL / 0.5)):
    s0 = int(j * 0.5 * SR); n = int(0.3 * SR); pt = np.arange(n) / SR; f = prog[(j // 4) % 4][j % 3] * 2
    music[s0:s0 + n] += (np.sin(2 * np.pi * f * pt) * np.exp(-pt * 12) * 0.5)[:N - s0]
music *= 0.1 / (np.abs(music).max() + 1e-9)
sfx = np.zeros(N, np.float32); rng = np.random.default_rng(3)
nz = rng.standard_normal(int(0.4 * SR)).astype(np.float32); env = np.sin(np.linspace(0, np.pi, len(nz))) ** 2
wh = (np.convolve(nz, np.ones(30) / 30, 'same') - np.convolve(nz, np.ones(300) / 300, 'same')) * env * 0.28
for s0 in ST[1:NS] + [END0]:
    i0 = int((s0 - 0.2) * SR); sfx[i0:i0 + len(wh)] += wh[:N - i0]
pt = np.arange(int(0.12 * SR)) / SR; pop = np.sin(2 * np.pi * (900 + 2500 * pt) * pt) * np.exp(-pt * 40) * 0.28
def addpop(tsec):
    j = int(tsec * SR); sfx[j:j + len(pop)] += pop[:N - j]
for i, s in enumerate(S):
    L = (ST[i + 1] if i < NS - 1 else END0 + 0.9) - ST[i]
    if s['t'] == 'comp':
        step = (L * 0.75 - COMP_T0) / 4
        for k in range(4): addpop(ST[i] + COMP_T0 + k * step)
    if s['t'] == 'ben':
        for k in range(3): addpop(ST[i] + BEN_T0 + k * BEN_STEP)
    if s['t'] == 'offer':
        for k in range(3): addpop(ST[i] + PILL_T0 + k * PILL_STEP)
if PERSON == 'olia':
    for tk in [ST[1] + 0.8, ST[2] + 1.6, ST[3] + 0.9]: addpop(tk)
ct = np.arange(int(1.2 * SR)) / SR; chime = (np.sin(2 * np.pi * 1046.5 * ct) + 0.5 * np.sin(2 * np.pi * 1568 * ct)) * np.exp(-ct * 3.5) * 0.1
j = int((END0 + 0.2) * SR); sfx[j:j + len(chime)] += chime[:N - j]
def ww(p, x):
    with wave.open(p, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
ww(f'{TMP}/voice.wav', voice); ww(f'{TMP}/music.wav', music); ww(f'{TMP}/sfx.wav', sfx)

enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', f'{TMP}/video_only.mp4'], stdin=subprocess.PIPE)
nf = int(TOTAL * FPS)
for n in range(nf):
    enc.stdin.write(frame(n / FPS).tobytes())
    if n % 300 == 0: print(PERSON, OFFER, 'frame', n, '/', nf, flush=True)
enc.stdin.close(); enc.wait()
OUT = f'/home/claude/v2/skineform_{PERSON}_{"2pack" if OFFER == "free" else "37uah"}_9x16.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{TMP}/video_only.mp4', '-i', f'{TMP}/voice.wav', '-i', f'{TMP}/music.wav', '-i', f'{TMP}/sfx.wav',
    '-filter_complex', f'[1:a]asplit=2[vk][vm];[2:a][vk]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=400[mb];[mb][vm][3:a]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5,afade=t=out:st={TOTAL-0.6}:d=0.6[a]',
    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-t', str(TOTAL), OUT], check=True)
print('done', OUT, TOTAL)
