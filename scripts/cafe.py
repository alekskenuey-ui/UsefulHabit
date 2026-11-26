import math, subprocess, wave, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
OFFER = sys.argv[1]
W, H, FPS = 1080, 1920, 30
F = "/usr/share/fonts/opentype/inter/"
FOREST = (22, 66, 37); EMERALD = (16, 185, 129); WHITE = (255, 255, 255); AMBER = (255, 196, 61)
SRC = '/home/claude/olia3'; D = '/home/claude/v2/cafe'; A = '/home/claude/usefulhabit/assets/'
TMP = f'{D}/{OFFER}'; subprocess.run(['mkdir', '-p', TMP]); TEMPO = 1.12
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
def prep(k):
    out = f'{TMP}/{k}.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{D}/vo/{k}.mp3', '-af',
        f'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse,rubberband=tempo={TEMPO}:pitchq=quality',
        '-ar', '48000', '-ac', '1', out], check=True)
    return out, dur(out)

# сегменти: (тип, src0, src1, vo)
SEG = [('clip', 0.0, 1.95, 'm1'), ('clip', 2.0, 3.95, 'o1'), ('comp', 0, 0, 'o2'), ('ben', 0, 0, 'o3'),
       ('clip', 4.0, 5.79, 'm2'), ('offer', 5.88, 9.9, OFFER), ('end', 9.9, 9.9, 'cta')]
VOF = [prep(s[3]) for s in SEG]
ST, VO_AT, t = [], [], 0.0
for i, s in enumerate(SEG):
    ST.append(t); pre = 0.15 if i == 0 else (0.35 if s[0] == 'end' else 0.08); VO_AT.append(t + pre)
    t += pre + VOF[i][1] + (0.9 if s[0] == 'end' else 0.22)
TOTAL = round(t, 2); ST.append(TOTAL)
print(OFFER, 'TOTAL', TOTAL, flush=True)

_cache = {}
def clipframe(src):
    n = min(max(int(round(src * 24)) + 1, 1), 240)
    if n not in _cache:
        if len(_cache) > 6: _cache.clear()
        _cache[n] = Image.open(f'{SRC}/fr/{n:04d}.jpg').convert('RGB')
    return _cache[n]
def zoomed(img, z, cx=.5, cy=.5):
    if z <= 1.0001: return img
    cw, ch = W / z, H / z; x0 = min(max(cx * W - cw / 2, 0), W - cw); y0 = min(max(cy * H - ch / 2, 0), H - ch)
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))

def bubble(name, lines, tail_x, y=250, size=56):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = font('Inter-ExtraBold.otf', size); fn = font('Inter-Bold.otf', 32)
    ws = [tw(d, l, f)[0] for l in lines]; bw = max(max(ws), tw(d, name, fn)[0]) + 96
    lh = size * 1.2; bh = 40 + 42 + lh * len(lines) + 26
    x0 = min(max(tail_x - bw / 2, 50), W - 50 - bw)
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x0, y + 10, x0 + bw, y + bh + 10), radius=44, fill=(0, 0, 0, 60))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d.rounded_rectangle((x0, y, x0 + bw, y + bh), radius=44, fill=(255, 255, 255, 250))
    tx = min(max(tail_x, x0 + 70), x0 + bw - 70)
    d.polygon([(tx - 30, y + bh - 2), (tx + 30, y + bh - 2), (tx + 8, y + bh + 46)], fill=(255, 255, 255, 250))
    d.text((x0 + 48, y + 34 - tw(d, name, fn)[2]), name, font=fn, fill=EMERALD)
    for i, l in enumerate(lines):
        d.text((x0 + 48, y + 34 + 46 + i * lh - tw(d, l, f)[2]), l, font=f, fill=FOREST)
    return img
BUB = {0: bubble('Міла', ['Знову якась', 'сувора дієта?'], 760, y=200),
       1: bubble('Оля', ['Ні, без жорстких дієт!', 'Це — Skineform'], 620, y=200),
       4: bubble('Міла', ['Склад нормальний!', 'А де замовити?'], 330, y=200)}
MOVES = {0: (1.0, 1.08, .5, .55), 1: (1.0, 1.07, .6, .5), 4: (1.0, 1.08, .4, .5), 5: (1.04, 1.0, .5, .5)}

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
            p = back((t - 0.1 - k * step) / 0.3); k += 1; ww_ = tw(d, wd + ' ', f)[0]
            if p > 0:
                layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(layer).text((x, yy - tw(d, l, f)[2] + 30 * (1 - p)), wd, font=f, fill=fg + (int(255 * min(p, 1)),))
                img.alpha_composite(layer)
            x += ww_
    return img

DISC = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(DISC); fd = font('Inter-SemiBold.otf', 30)
dt = 'Дієтична добавка. Не є лікарським засобом'; w_, h_, o_ = tw(dd, dt, fd)
dd.rounded_rectangle((W / 2 - w_ / 2 - 26, 92, W / 2 + w_ / 2 + 26, 92 + h_ + 26), radius=24, fill=(0, 0, 0, 120))
dd.text((W / 2 - w_ / 2, 105 - o_), dt, font=fd, fill=(255, 255, 255, 235))

BG = Image.blend(clipframe(4.6).filter(ImageFilter.GaussianBlur(24)), Image.new('RGB', (W, H), (236, 246, 240)), 0.45)
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
def comp_scene(tl, L):
    img = zoomed(BG, 1.0 + 0.04 * eio(tl / L)).convert('RGBA')
    img.alpha_composite(words_layer(['10 рослинних', 'компонентів'], tl, y=230, size=80))
    pos = [(W / 2 - 230, 760), (W / 2 + 230, 760), (W / 2 - 230, 1290), (W / 2 + 230, 1290)]
    step = (L * 0.7 - 0.6) / 4
    for k, c in enumerate(CIRC):
        p = back((tl - 0.6 - k * step) / 0.4)
        if p <= 0: continue
        sc = max(p, 0.01); ci = c.resize((int(c.width * sc), int(c.height * sc)), Image.BICUBIC)
        img.alpha_composite(fade(ci, min(1, p)), (int(pos[k][0] - ci.width / 2), int(pos[k][1] - ci.height / 2)))
    return img
BEN = [('icon_weight', ['Коли стежу', 'за вагою']), ('icon_tea', ['Легкість', 'після їжі']), ('icon_support', ['Легше тримати', 'режим'])]
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
def ben_scene(tl, L):
    img = zoomed(BG, 1.04 + 0.04 * eio(tl / L)).convert('RGBA')
    img.alpha_composite(words_layer(['Для чого', 'Skineform'], tl, y=230, size=80))
    for k, c in enumerate(CARDS):
        p = back((tl - 0.35 - k * 0.5) / 0.45)
        if p <= 0: continue
        img.alpha_composite(fade(c, min(1, max(p, 0))), (int(90 - 700 * (1 - p)), 640 + k * 310))
    return img

def pill(text, size, fg, bg):
    d0 = ImageDraw.Draw(Image.new('RGBA', (1, 1))); f = font('Inter-ExtraBold.otf', size); w, h, o = tw(d0, text, f)
    im = Image.new('RGBA', (w + 100, h + 64), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w + 100, h + 64), radius=(h + 64) // 2, fill=bg); d.text((50, 32 - o), text, font=f, fill=fg); return im
if OFFER == 'free':
    P1 = '2 упаковки в подарунок*'; LIST = ['✓  2 упаковки в подарунок*', '✓  Оплата при отриманні', '✓  Консультація безкоштовна']; NOTE = '*при замовленні курсу; умови назве консультант'
else:
    P1 = 'Від 37 грн за упаковку*'; LIST = ['✓  Від 37 грн за упаковку*', '✓  Оплата при отриманні', '✓  Консультація безкоштовна']; NOTE = '*при замовленні курсу; повну вартість назве консультант'
PILLS = [(pill(P1, 64, FOREST, AMBER + (255,)), 230), (pill('Оплата при отриманні', 56, WHITE, FOREST + (240,)), 385), (pill('*при замовленні курсу', 34, (40, 50, 45), (255, 255, 255, 225)), 520)]

LOGO = Image.open('/home/claude/usefulhabit/logo.png').convert('RGBA'); LOGO = LOGO.resize((170, int(LOGO.height * 170 / LOGO.width)), Image.LANCZOS)
PANEL = Image.new('RGBA', (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(PANEL)
py0 = 470; ph = 790
shp = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(shp).rounded_rectangle((80, py0 + 14, W - 80, py0 + ph + 14), radius=52, fill=(0, 0, 0, 70))
PANEL.alpha_composite(shp.filter(ImageFilter.GaussianBlur(24)))
pd.rounded_rectangle((70, py0, W - 70, py0 + ph), radius=52, fill=(255, 255, 255, 248))
y = py0 + 60; f1 = font('Inter-ExtraBold.otf', 62)
for l in ['Свій ритм —', 'без жорстких дієт']:
    w, h, o = tw(pd, l, f1); pd.text((W / 2 - w / 2, y - o), l, font=f1, fill=FOREST); y += 78
y += 26; f2 = font('Inter-Bold.otf', 44)
for l in LIST:
    w, h, o = tw(pd, l, f2); pd.text((W / 2 - w / 2, y - o), l, font=f2, fill=(30, 110, 70)); y += 66
y += 26; bf = font('Inter-ExtraBold.otf', 58); bt = 'Залишити заявку ↓'; bw, bh, bo = tw(pd, bt, bf)
BTN = (W / 2 - bw / 2 - 72, y, W / 2 + bw / 2 + 72, y + bh + 68)
pd.rounded_rectangle(BTN, radius=(bh + 68) / 2, fill=EMERALD); pd.text((W / 2 - bw / 2, y + 34 - bo), bt, font=bf, fill=WHITE); y += bh + 68 + 36
f3 = font('Inter-Medium.otf', 29)
for l in [NOTE, 'Дієтична добавка. Не є лікарським засобом.']:
    w, h, o = tw(pd, l, f3); pd.text((W / 2 - w / 2, y - o), l, font=f3, fill=(70, 90, 80)); y += 40

def seg_img(i, t):
    kind, s0, s1, _ = SEG[i]; tl = t - ST[i]; L = ST[i + 1] - ST[i]
    if kind == 'comp': return comp_scene(tl, L)
    if kind == 'ben': return ben_scene(tl, L)
    if kind == 'end':
        bg = clipframe(9.9); b = eo(tl / 0.5)
        img = Image.blend(bg, bg.filter(ImageFilter.GaussianBlur(22)), b)
        img = Image.blend(img, Image.new('RGB', (W, H), (236, 246, 240)), 0.3 * b).convert('RGBA')
        img.alpha_composite(fade(LOGO, b), (W - LOGO.width - 60, 60))
        p = eo((tl - 0.2) / 0.45)
        if p > 0: img.alpha_composite(fade(PANEL, p), (0, int(70 * (1 - p))))
        if tl > 1.2:
            pu = (math.sin((tl - 1.2) * 4) + 1) / 2; g = 6 + 10 * pu
            ring = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(ring).rounded_rectangle((BTN[0] - g, BTN[1] - g, BTN[2] + g, BTN[3] + g), radius=(BTN[3] - BTN[1]) / 2 + g, outline=EMERALD + (int(120 * (1 - pu)),), width=6)
            img.alpha_composite(ring)
        return img
    rate = min(1.0, (s1 - s0) / L)
    img = clipframe(min(s0 + tl * rate, s1 - 0.02))
    z0, z1, cx, cy = MOVES.get(i, (1, 1.05, .5, .5))
    img = zoomed(img, z0 + (z1 - z0) * eio(tl / L), cx, cy).convert('RGBA')
    if i in BUB:
        a = eo((tl - 0.1) / 0.28); img.alpha_composite(fade(BUB[i], a), (0, int(30 * (1 - a))))
    if kind == 'offer':
        for k, (pl, yy) in enumerate(PILLS):
            a = back((tl - 0.3 - k * 0.55) / 0.4)
            if a > 0:
                pi = pl.resize((max(1, int(pl.width * a)), max(1, int(pl.height * a))), Image.BICUBIC)
                img.alpha_composite(fade(pi, min(1, a)), (int(W / 2 - pi.width / 2), int(yy + pl.height / 2 - pi.height / 2)))
    return img

XF = 0.22
def frame(t):
    i = max(k for k in range(len(SEG)) if t >= ST[k])
    img = seg_img(i, t)
    if i > 0 and t < ST[i] + XF and SEG[i][0] != 'end':
        img = Image.blend(seg_img(i - 1, t).convert('RGB'), img.convert('RGB'), eo((t - ST[i]) / XF)).convert('RGBA')
    if SEG[i][0] != 'end': img.alpha_composite(DISC)
    return img.convert('RGB')

if len(sys.argv) > 2:
    for tt in map(float, sys.argv[2].split(',')): frame(min(tt, TOTAL - 0.05)).save(f'{TMP}/f_{tt}.jpg', quality=80)
    sys.exit()

SR = 48000
def rw(p):
    with wave.open(p) as w: return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
N = int(TOTAL * SR); voice = np.zeros(N, np.float32)
for i, (p, _) in enumerate(VOF):
    a = rw(p); s0 = int(VO_AT[i] * SR); voice[s0:s0 + len(a)] += a[:N - s0]
tt = np.arange(N) / SR; music = np.zeros(N, np.float32)
prog = [(261.6, 329.6, 392), (196, 246.9, 293.7), (220, 261.6, 329.6), (174.6, 220, 261.6)]
bar = 2.0; t0 = 0; k = 0
while t0 < TOTAL:
    m = (tt >= t0) & (tt < min(t0 + bar + 0.5, TOTAL)); sg = tt[m] - t0; Lb = min(bar + 0.5, TOTAL - t0)
    env = np.minimum(1, sg / 0.6) * np.minimum(1, (Lb - sg) / 0.6)
    for f in prog[k % 4]: music[m] += (np.sin(2 * np.pi * f * sg) + 0.3 * np.sin(4 * np.pi * f * sg)) * env
    t0 += bar; k += 1
for j in range(int(TOTAL / 0.5)):
    s0 = int(j * 0.5 * SR); n = int(0.25 * SR); pt = np.arange(n) / SR; f = prog[(j // 4) % 4][j % 3] * 2
    music[s0:s0 + n] += (np.sin(2 * np.pi * f * pt) * np.exp(-pt * 14) * 0.5)[:N - s0]
music *= 0.11 / (np.abs(music).max() + 1e-9)
sfx = np.zeros(N, np.float32); rng = np.random.default_rng(5)
nz = rng.standard_normal(int(0.4 * SR)).astype(np.float32); env = np.sin(np.linspace(0, np.pi, len(nz))) ** 2
wh = (np.convolve(nz, np.ones(30) / 30, 'same') - np.convolve(nz, np.ones(300) / 300, 'same')) * env * 0.3
for s0 in ST[1:-1]:
    i0 = int((s0 - 0.2) * SR); sfx[i0:i0 + len(wh)] += wh[:N - i0]
pt = np.arange(int(0.12 * SR)) / SR; pop = np.sin(2 * np.pi * (900 + 2500 * pt) * pt) * np.exp(-pt * 40) * 0.28
def addpop(ts, g=1.0):
    j = int(ts * SR); sfx[j:j + len(pop)] += (pop * g)[:N - j]
L2 = ST[3] - ST[2]; step = (L2 * 0.7 - 0.6) / 4
for k in range(4): addpop(ST[2] + 0.6 + k * step)
for k in range(3): addpop(ST[3] + 0.35 + k * 0.5)
for k in range(3): addpop(ST[5] + 0.3 + k * 0.55)
for i in BUB: addpop(ST[i] + 0.08, 0.8)
ct = np.arange(int(0.6 * SR)) / SR
clink = sum(np.sin(2 * np.pi * f * ct) * np.exp(-ct * d) for f, d in [(2350, 18), (3720, 24), (5100, 30)]) * 0.12
L5 = ST[6] - ST[5]; rate5 = min(1, (9.9 - 5.88) / L5); j = int((ST[5] + (7.3 - 5.88) / rate5) * SR); sfx[j:j + len(clink)] += clink[:N - j]
ct = np.arange(int(1.2 * SR)) / SR; chime = (np.sin(2 * np.pi * 1046.5 * ct) + 0.5 * np.sin(2 * np.pi * 1568 * ct)) * np.exp(-ct * 3.5) * 0.1
j = int((ST[6] + 0.25) * SR); sfx[j:j + len(chime)] += chime[:N - j]
def ww(p, x):
    with wave.open(p, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
ww(f'{TMP}/voice.wav', voice); ww(f'{TMP}/music.wav', music); ww(f'{TMP}/sfx.wav', sfx)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', f'{TMP}/video_only.mp4'], stdin=subprocess.PIPE)
nf = int(TOTAL * FPS)
for n in range(nf): enc.stdin.write(frame(n / FPS).tobytes())
enc.stdin.close(); enc.wait()
OUT = f'/home/claude/v2/skineform_cafe_{"2pack" if OFFER == "free" else "37uah"}_9x16.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{TMP}/video_only.mp4', '-i', f'{TMP}/voice.wav', '-i', f'{TMP}/music.wav', '-i', f'{TMP}/sfx.wav',
    '-filter_complex', f'[1:a]asplit=2[vk][vm];[2:a][vk]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=400[mb];[mb][vm][3:a]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5,afade=t=out:st={TOTAL-0.6}:d=0.6[a]',
    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-t', str(TOTAL), OUT], check=True)
print('done', OUT, TOTAL)
