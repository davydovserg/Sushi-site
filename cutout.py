import sys, os, glob
from rembg import remove, new_session
from PIL import Image
src, dst, model = sys.argv[1], sys.argv[2], sys.argv[3]
ids = sys.argv[4].split(',') if len(sys.argv) > 4 else None
os.makedirs(dst, exist_ok=True)
s = new_session(model)
files = [f'{src}/{i}.jpg' for i in ids] if ids else sorted(glob.glob(src + '/*.jpg'))
for f in files:
    im = Image.open(f).convert('RGB')
    out = remove(im, session=s, post_process_mask=True)
    a = out.split()[3]
    bb = a.point(lambda v: 255 if v > 30 else 0).getbbox()
    if bb: out = out.crop(bb)
    out.save(os.path.join(dst, os.path.basename(f)[:-4] + '.webp'), 'WEBP', quality=88, method=5)
print('done', len(files))
