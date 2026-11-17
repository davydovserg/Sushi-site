# Фото Sushi&Mall на белом → студийный фон как у Roll&Wok (градиент + отражение)
# Запуск: python studio.py [id1,id2]  → orig_st/<id>.jpg (photos.py берёт их, если нет фото Roll&Wok)
import sys, os, glob
from rembg import remove, new_session
from PIL import Image, ImageDraw, ImageChops, ImageFilter
os.makedirs('orig_st', exist_ok=True)
W, H = 1500, 1160
ref = Image.open(sorted(glob.glob('orig_rw/*.jpg'))[0]).convert('RGB').resize((W, H))
top, bot = ref.getpixel((20, 20)), ref.getpixel((20, H - 20))

def bg():
    g = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(g)
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return g

def fill_holes(a):
    w, h = a.size
    solid = a.point(lambda v: 255 if v > 100 else 0)
    pad = Image.new('L', (w + 2, h + 2), 0); pad.paste(solid, (1, 1))
    ImageDraw.floodfill(pad, (0, 0), 128)
    outside = pad.crop((1, 1, w + 1, h + 1)).point(lambda v: 255 if v == 128 else 0)
    return ImageChops.lighter(a, ImageChops.invert(outside).filter(ImageFilter.GaussianBlur(0.8)))

s = new_session('isnet-general-use')
have_rw = {os.path.basename(f)[:-4] for f in glob.glob('orig_rw/*.jpg')}
ids = sys.argv[1].split(',') if len(sys.argv) > 1 else [os.path.basename(f)[:-4] for f in glob.glob('orig/*.jpg')]
for i in ids:
    if i in have_rw: continue
    im = Image.open(f'orig/{i}.jpg').convert('RGB')
    a = fill_holes(remove(im, session=s, post_process_mask=True, only_mask=True).convert('L'))
    obj = im.copy(); obj.putalpha(a)
    bb = a.point(lambda v: 255 if v > 30 else 0).getbbox()
    if not bb: continue
    obj = obj.crop(bb)
    k = min(W * 0.86 / obj.width, H * 0.68 / obj.height)
    obj = obj.resize((int(obj.width * k), int(obj.height * k)), Image.LANCZOS)
    x, y = (W - obj.width) // 2, int(H * 0.78) - obj.height
    out = bg()
    # отражение: перевёрнутое, слабое, гаснет книзу
    refl = obj.transpose(Image.FLIP_TOP_BOTTOM)
    fade = Image.linear_gradient('L').resize(refl.size).point(lambda v: int((255 - v) * 0.28))
    ra = ImageChops.multiply(refl.split()[3], fade)
    refl.putalpha(ra)
    out.paste(refl, (x, y + obj.height - 2), refl)
    # мягкая тень под блюдом
    sh = Image.new('L', (W, H), 0)
    ImageDraw.Draw(sh).ellipse([x + obj.width * .1, y + obj.height - 18, x + obj.width * .9, y + obj.height + 22], fill=120)
    out.paste(Image.new('RGB', (W, H), (20, 16, 20)), (0, 0), sh.filter(ImageFilter.GaussianBlur(18)))
    out.paste(obj, (x, y), obj)
    out.save(f'orig_st/{i}.jpg', quality=92)
print('done')
