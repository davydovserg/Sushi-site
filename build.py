# Сборка: прозрачные фото + data.js из menu.json
import json, re, os, glob
from PIL import Image, ImageDraw, ImageFilter, ImageChops
os.makedirs('cut', exist_ok=True)
def cut(src, dst):
    im = Image.open(src).convert('RGB')
    w, h = im.size
    r, g, b = im.split()
    mn = ImageChops.darker(ImageChops.darker(r, g), b)
    if max(im.getpixel((2, 2))) < 40:
        mx = ImageChops.lighter(ImageChops.lighter(r, g), b)
        binm = mx.point(lambda v: 255 if v < 30 else 0)
    else:
        binm = mn.point(lambda v: 255 if v > 236 else 0)
    # рамка в 1px, чтобы заливка обошла всё по краю
    pad = Image.new('L', (w+2, h+2), 255); pad.paste(binm, (1, 1))
    ImageDraw.floodfill(pad, (0, 0), 128)
    bg = pad.crop((1, 1, w+1, h+1)).point(lambda v: 255 if v == 128 else 0)
    alpha = ImageChops.invert(bg).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    im.putalpha(alpha)
    bbox = alpha.point(lambda v: 255 if v > 20 else 0).getbbox()
    if bbox: im = im.crop(bbox)
    im.save(dst, 'WEBP', quality=86, method=5)
menu = json.load(open('menu.json', encoding='utf-8'))
for c in menu:
    for it in c['items']:
        if it['img']:
            dst = 'cut/%s.webp' % it['id']
            pass  # фото вырезаются нейросетью: python cutout.py img cut isnet-general-use
            it['img'] = dst
        d = it['d']
        w = ''
        m = re.search(r'Вес:?\s*(.*)$', d)
        if m: w, d = m.group(1), d[:m.start()]
        else:
            m = re.search(r'(\d+\s*шт\w*\s*-?\s*)?\d+\s*(г|мл|л)\.?\s*$', d)
            if m: w, d = m.group(0), d[:m.start()]
        d = re.sub(r'\s*,\s*,', ',', d).strip(' .,-')
        d = re.sub(r'\s*,\s*', ', ', d)
        w = re.sub(r'^\s*-\s*', '', w).replace('штук -', 'шт ·').replace('штуки -', 'шт ·').strip(' .')
        it['d'] = (d + '.') if d else ''
        it['w'] = w
        it['t'] = it['t'].replace('«', '').replace('»', '').strip()
open('data.js', 'w', encoding='utf-8').write('window.MENU=' + json.dumps(menu, ensure_ascii=False) + ';')
print('ok', sum(len(c['items']) for c in menu))

# фото целиком, без вырезки
import runpy; runpy.run_path('photos.py')
