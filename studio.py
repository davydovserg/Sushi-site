# Фото Sushi&Mall на белом → студийный фон как у Roll&Wok (градиент + лёгкое отражение)
# Вырезка: BiRefNet + заливка дыр + отрезание исходного отражения (поиск линии зеркала)
# Запуск: python studio.py [id1,id2]  → orig_st/<id>.jpg (photos.py берёт их, если нет фото Roll&Wok)
import sys, os, glob
import numpy as np
from rembg import remove, new_session
from PIL import Image, ImageDraw, ImageChops, ImageFilter
os.makedirs('orig_st', exist_ok=True)
W, H = 1500, 1160
ref = Image.open(sorted(glob.glob('orig_rw/*.jpg'))[0]).convert('RGB').resize((W, H))
top, bot = ref.getpixel((20, 20)), ref.getpixel((20, H - 20))

def bg():
    g = Image.new('RGB', (W, H)); d = ImageDraw.Draw(g)
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

def cut_mirror(im, a):
    """Отражение снизу: по полосам ширины ищем линию, ниже которой картинка — зеркало верха; режем маску по этой линии."""
    g = np.asarray(im.convert('L'), dtype=np.float32)
    m = np.asarray(a, dtype=np.float32) > 100
    H_, W_ = m.shape
    xs = np.where(m.any(0))[0]
    if len(xs) < 40: return a
    step, half = 16, 20
    pts = []
    for cx in range(xs[0] + half, xs[-1] - half, step):
        col = m[:, cx - half:cx + half].any(1)
        ys = np.where(col)[0]
        if len(ys) < 60: continue
        y0, y1 = ys[0], ys[-1]; h = y1 - y0
        best, by = 0, None
        for y in range(int(y0 + h * .35), int(y1 - h * .05), 2):
            k = min(int(h * .2), y1 - y, y - y0)
            if k < 12: continue
            A = g[y - k:y, cx - half:cx + half][::-1]; B = g[y:y + k, cx - half:cx + half]
            A = A - A.mean(); B = B - B.mean()
            c = (A * B).sum() / (np.sqrt((A * A).sum() * (B * B).sum()) + 1e-6)
            if c > best: best, by = c, y
        if by is not None and best > 0.6: pts.append((cx, by))
    if len(pts) < max(4, (xs[-1] - xs[0]) // step // 3): return a
    px = np.array([p[0] for p in pts]); py = np.array([p[1] for p in pts], dtype=np.float32)
    # сглаживание медианой
    py = np.array([np.median(py[max(0, i - 2):i + 3]) for i in range(len(py))])
    line = np.interp(np.arange(W_), px, py)
    arr = np.asarray(a).astype(np.float32)
    yy = np.arange(H_)[:, None]
    fade = np.clip((line[None, :] - yy) / 4.0, 0, 1)
    return Image.fromarray((arr * fade).astype(np.uint8))

# Ручная линия отреза отражения: id -> [(x%, y%), ...] — всё ниже ломаной убирается
MIRROR = {'253088238': [(0,.672),(.533,.672),(.538,.508),(.665,.508),(.67,.413),(.782,.413),(.787,.352),(1,.352)], '253088394': [(0,.672),(.533,.672),(.538,.508),(.665,.508),(.67,.413),(.782,.413),(.787,.352),(1,.352)]}
def cut_line(a, pts):
    w, h = a.size
    arr = np.asarray(a).astype(np.float32)
    line = np.interp(np.arange(w), [p[0] * w for p in pts], [p[1] * h for p in pts])
    fade = np.clip((line[None, :] - np.arange(h)[:, None]) / 3.0, 0, 1)
    return Image.fromarray((arr * fade).astype(np.uint8))

s = new_session('birefnet-general-lite')
have_rw = {os.path.basename(f)[:-4] for f in glob.glob('orig_rw/*.jpg')}
ids = sys.argv[1].split(',') if len(sys.argv) > 1 else [os.path.basename(f)[:-4] for f in glob.glob('orig/*.jpg')]
for i in ids:
    if i in have_rw: continue
    im = Image.open(f'orig/{i}.jpg').convert('RGB')
    a = remove(im, session=s, only_mask=True).convert('L')
    a = fill_holes(a)
    if i in MIRROR:
        a = cut_line(a, MIRROR[i])
        a = a.filter(ImageFilter.MinFilter(31)).filter(ImageFilter.MaxFilter(31)).filter(ImageFilter.GaussianBlur(1.2))  # скруглить углы, убрать полоски
    obj = im.copy(); obj.putalpha(a)
    bb = a.point(lambda v: 255 if v > 30 else 0).getbbox()
    if not bb: continue
    obj = obj.crop(bb)
    k = min(W * 0.86 / obj.width, H * 0.68 / obj.height)
    obj = obj.resize((int(obj.width * k), int(obj.height * k)), Image.LANCZOS)
    x, y = (W - obj.width) // 2, int(H * 0.78) - obj.height
    out = bg()
    # отражение от низа каждого столбца (как на зеркальном столе)
    A = np.asarray(obj).astype(np.float32); hh, ww = A.shape[:2]
    al = A[:, :, 3] > 40
    yb = np.where(al.any(0), hh - 1 - np.argmax(al[::-1], 0), -1)
    L = int(hh * .45); R = np.zeros((hh + L, ww, 4), np.float32)
    cols = np.arange(ww)
    for j in range(L):
        src = yb - j; ok = (yb >= 0) & (src >= 0)
        c = cols[ok]; R[yb[ok] + 1 + j, c] = A[src[ok], c]
        R[yb[ok] + 1 + j, c, 3] *= max(0.0, 1 - j / L) ** 1.6 * 0.24
    R[:, :, 3] *= 1  # keep
    refl = Image.fromarray(R.clip(0, 255).astype(np.uint8), 'RGBA')
    out.paste(refl, (x, y), refl)
    out.paste(obj, (x, y), obj)
    out.save(f'orig_st/{i}.jpg', quality=92)
print('done')
