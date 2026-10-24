"""Brand-aware social post generator (Brand Kit uyumlu).
Offline mod: hazır kütüphane metni. AI mod: OPENAI_API_KEY varsa OpenAI ile metin.
Görseller Pillow ile çizilir. Resmî logo varsa logos/<marka>.png kullanılır, yoksa yer tutucu çizilir.
Resmî font varsa fonts/<dosya> kullanılır, yoksa DejaVu'ya düşer.
"""
import json, os, argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def load_environment():
    if load_dotenv is not None:
        load_dotenv()
        return

    env_path = Path(__file__).resolve().parent / '.env'
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"\'')
        os.environ.setdefault(key, value)


load_environment()

BASE = Path(__file__).resolve().parent
BRANDS = json.loads((BASE / 'brand_configs.json').read_text(encoding='utf-8'))
DEJAVU = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
DEJAVU_R = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'

def tr_upper(s):
    """Türkçe büyük harf: i→İ, ı→I (Python .upper() bunu yanlış yapar)."""
    return s.replace('i', 'İ').replace('ı', 'I').upper()

def font(name, size, regular=False):
    for p in (BASE / 'fonts' / name if name else None, DEJAVU_R if regular else DEJAVU):
        try:
            return ImageFont.truetype(str(p), size)
        except Exception:
            continue
    return ImageFont.load_default()

def wrap(draw, txt, f, maxw):
    lines, line = [], ''
    for w in txt.split():
        t = (line + ' ' + w).strip()
        if draw.textbbox((0, 0), t, font=f)[2] > maxw and line:
            lines.append(line); line = w
        else:
            line = t
    return lines + ([line] if line else [])

def ai_copy(brand, topic):
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "AI mode requires the 'openai' package. Install it with: pip install openai"
        ) from exc
    b = BRANDS[brand]
    lang = 'Turkish' if b['lang'] == 'tr' else 'English'
    prompt = f"""Generate social post text for {b['name']} on topic {topic}.
Tone: {b['tone']}. Audience: {b['audience']}.
No invented statistics, dates, prizes, offers, diagnoses or unverifiable facts. No guarantees.
Return a JSON object with exactly: title (max 7 words), subtitle (max 16 words), category (max 3 words), caption (40-65 words). Write in {lang}."""
    r = OpenAI().responses.create(model=os.getenv('OPENAI_MODEL', 'gpt-4.1-mini'), input=prompt)
    raw = r.output_text.strip().removeprefix('```json').removesuffix('```').strip()
    return json.loads(raw)

def draw_logo(img, d, brand, c, box):
    """Resmî logo dosyası varsa yapıştırır; yoksa net işaretli yer tutucu."""
    p = BASE / 'logos' / f'{brand}.png'
    x0, y0, x1, y1 = box
    if p.exists():
        lg = Image.open(p).convert('RGBA'); lg.thumbnail((x1 - x0, y1 - y0))
        img.paste(lg, (x1 - lg.width if x0 > 500 else x0, y0), lg)
    else:
        d.rounded_rectangle(box, radius=14, outline=c['fg'], width=3)
        f = font(MONO, 20)
        d.text(((x0 + x1) / 2, (y0 + y1) / 2), 'LOGO', font=f, fill=c['fg'], anchor='mm')

def draw_title(d, title, c, x, y, maxw, f_big, step):
    f = f_big
    lines = wrap(d, title, f, maxw)
    if len(lines) > 5:
        f = f_big.font_variant(size=64); lines = wrap(d, title, f, maxw); step = 80
    words_total = len(title.split()); seen = 0
    for ln in lines[:6]:
        cx = x
        for w in ln.split():
            seen += 1
            col = c['accent'] if (c['highlight_last_word'] and seen == words_total) else c['fg']
            d.text((cx, y), w, font=f, fill=col)
            cx += d.textlength(w + ' ', font=f)
        y += step
    return y

def create(brand, index=0, topic=None, mode='offline', output=None):
    b = BRANDS[brand]; c = b['colors']; tr = b['lang'] == 'tr'
    sample = b['topics'][index % len(b['topics'])]
    if mode == 'ai':
        if not os.getenv('OPENAI_API_KEY'):
            raise RuntimeError('AI mode needs OPENAI_API_KEY')
        dd = ai_copy(brand, topic or sample[0])
        title, subtitle, category, caption = dd['title'], dd['subtitle'], dd['category'], dd['caption']
    else:
        title, subtitle, category, caption = sample
    up = tr_upper if tr else str.upper
    title, category, name = up(title), up(category), up(b['name'])
    tag_bg = c.get('tag_bg_myth', c['tag_bg']) if 'MİT' in category else c['tag_bg']

    W, H = 1080, 1350
    img = Image.new('RGB', (W, H), c['bg']); d = ImageDraw.Draw(img)
    domain = b['url'].replace('https://', '').replace('www.', '').strip('/')
    fT = font(b['font_file'], 82); fS = font(None, 35, True)

    if b['layout'] == 'frame':  # Design House Global: çizgi çerçeve, başlık sol altta, ortalı web adresi
        d.line((72, 70, W - 72, 70), fill=c['fg'], width=2)
        d.line((72, H - 110, W - 72, H - 110), fill=c['fg'], width=2)
        draw_logo(img, d, brand, c, (72, 95, 232, 255))
        d.rectangle((72, 285, 72 + d.textlength(category, font=font(MONO, 22)) + 36, 332), fill=tag_bg)
        d.text((90, 294), category, font=font(MONO, 22), fill=c['tag_fg'])
        fT = font(b['font_file'], 78)
        if ' — ' in title:  # "X — Y." kalıbı: tire sonrası satır başı
            a, bb = title.split(' — ', 1)
            lines = wrap(d, a + ' —', fT, 930) + wrap(d, bb, fT, 930)
        else:
            lines = wrap(d, title, fT, 930)
        sub = wrap(d, subtitle, fS, 930)[:2]
        block = len(lines) * 96 + 30 + len(sub) * 50
        y = H - 170 - block
        for ln in lines: d.text((72, y), ln, font=fT, fill=c['fg']); y += 96
        y += 30
        for ln in sub: d.text((72, y), ln, font=fS, fill=c['fg']); y += 50
        d.text((W / 2, H - 55), domain, font=font(MONO, 26), fill=c['fg'], anchor='mm')
    else:
        # sabit unsurlar: sağ üst logo, üst etiket, alt iletişim şeridi
        draw_logo(img, d, brand, c, (W - 72 - 300, 50, W - 72, 235))
        tw = d.textlength(category, font=font(DEJAVU, 25))
        d.rounded_rectangle((72, 76, 72 + tw + 48, 143), radius=20, fill=tag_bg)
        d.text((96, 94), category, font=font(DEJAVU, 25), fill=c['tag_fg'])
        d.text((72, 195), name, font=font(DEJAVU, 33 if len(name) < 22 else 26), fill=c['fg'])
        d.line((72, 273, W - 72, 273), fill=c['accent'] if c['accent'] != c['bg'] else c['fg'], width=5)
        y = draw_title(d, title, c, 72, 400, 930, fT, 104)
        y = max(y + 48, 900)
        if b['layout'] == 'card':  # ABA Psikoloji: yumuşak köşeli kart
            sub = wrap(d, subtitle, fS, 840)[:3]
            d.rounded_rectangle((60, y - 30, W - 60, y + len(sub) * 52 + 30), radius=28, fill='#FFFFFF')
            for ln in sub: d.text((96, y), ln, font=fS, fill=c['fg']); y += 52
        else:
            for ln in wrap(d, subtitle, fS, 900)[:3]: d.text((72, y), ln, font=fS, fill=c['fg']); y += 52
        d.rectangle((0, 1240, W, H), fill=c['strip_bg'])
        d.line((0, 1240, W, 1240), fill=c['strip_line'], width=6)
        d.text((72, 1278), domain, font=font(DEJAVU, 27), fill=c['strip_fg'])

    out = Path(output) if output else BASE / 'ornek_postlar' / f'{brand}_{index + 1}.png'
    out.parent.mkdir(parents=True, exist_ok=True); img.save(out)
    return out, {'brand': b['name'], 'title': title, 'subtitle': subtitle, 'category': category, 'caption': caption,
                 'mode': mode, 'official_logo_included': (BASE / 'logos' / f'{brand}.png').exists()}

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--brand', choices=list(BRANDS) + ['all']); p.add_argument('--index', type=int, default=0)
    p.add_argument('--topic'); p.add_argument('--mode', choices=['offline', 'ai'], default='offline'); p.add_argument('--output')
    a = p.parse_args()
    if a.brand in (None, 'all'):  # tüm markalar x 3 post
        allmeta = []
        for k in BRANDS:
            for i in range(3):
                path, m = create(k, i); allmeta.append({'path': str(path.name), **m})
        (BASE / 'ornek_postlar' / 'ornek_postlar.json').write_text(json.dumps(allmeta, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'{len(allmeta)} post üretildi')
    else:
        path, meta = create(a.brand, a.index, a.topic, a.mode, a.output)
        print(json.dumps({'path': str(path), **meta}, ensure_ascii=False, indent=2))
