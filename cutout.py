# Вырезка фона у фото блюд: нейросеть rembg + заливка дыр внутри блюда (сыр, рис)
# Запуск: python cutout.py orig cut isnet-general-use [id1,id2,...]
import sys, os, glob
from rembg import remove, new_session
from PIL import Image, ImageDraw, ImageChops, ImageFilter

src, dst, model = sys.argv[1], sys.argv[2], sys.argv[3]
ids = sys.argv[4].split(',') if len(sys.argv) > 4 else None
os.makedirs(dst, exist_ok=True)
s = new_session(model)
files = [f'{src}/{i}.jpg' for i in ids] if ids else sorted(glob.glob(src + '/*.jpg'))

def fill_holes(a):
    w, h = a.size
    solid = a.point(lambda v: 255 if v > 100 else 0)
    pad = Image.new('L', (w + 2, h + 2), 0); pad.paste(solid, (1, 1))
    ImageDraw.floodfill(pad, (0, 0), 128)          # 128 = фон, связанный с краем кадра
    outside = pad.crop((1, 1, w + 1, h + 1)).point(lambda v: 255 if v == 128 else 0)
    inside = ImageChops.invert(outside).filter(ImageFilter.GaussianBlur(0.8))
    return ImageChops.lighter(a, inside)

for f in files:
    im = Image.open(f).convert('RGB')
    out = remove(im, session=s, post_process_mask=True)
    a = fill_holes(out.split()[3])
    out = im.copy(); out.putalpha(a)
    bb = a.point(lambda v: 255 if v > 30 else 0).getbbox()
    if bb: out = out.crop(bb)
    out.thumbnail((1000, 1000), Image.LANCZOS)
    rgb = out.convert('RGB').filter(ImageFilter.UnsharpMask(radius=1.4, percent=55, threshold=2))
    rgb.putalpha(out.split()[3])
    rgb.save(os.path.join(dst, os.path.basename(f)[:-4] + '.webp'), 'WEBP', quality=86, method=6)
print('done', len(files))
