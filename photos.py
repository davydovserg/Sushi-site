# Фото блюд целиком, без вырезки фона: orig_rw/ (Roll&Wok) важнее orig/ (Sushi&Mall)
# Запуск: python photos.py  → ph/<id>.jpg, пути в data.js и extra.js
import glob, os, re
from PIL import Image
os.makedirs('ph', exist_ok=True)
src = {os.path.basename(f)[:-4]: f for f in glob.glob('orig/*.jpg')}
src.update({os.path.basename(f)[:-4]: f for f in glob.glob('orig_st/*.jpg')})
src.update({os.path.basename(f)[:-4]: f for f in glob.glob('orig_rw/*.jpg')})
for i, f in src.items():
    im = Image.open(f).convert('RGB')
    im.thumbnail((1000, 1000), Image.LANCZOS)
    im.save(f'ph/{i}.jpg', 'JPEG', quality=86, optimize=True, progressive=True)
for p in ('data.js', 'extra.js'):
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'cut/([\w-]+)\.webp', lambda m: f'ph/{m.group(1)}.jpg' if m.group(1) in src else m.group(0), s)
    open(p, 'w', encoding='utf-8').write(s)
print(len(src), 'photos')
