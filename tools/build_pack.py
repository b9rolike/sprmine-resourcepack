"""Reproducible original clan UI assets layered over the unchanged rank ZIP."""
import hashlib
import io
import json
from pathlib import Path
import zipfile
from PIL import Image, ImageDraw
from pack_metadata import validate_metadata

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sprmine-ranks-v1.3-vanilla-font-1.21.11.zip"
EXPECTED = "557FB48683E85AA323F9A8E4E5D2D856FC0B61145BA51B224CEE253162A67AA3"
assert hashlib.sha256(BASE.read_bytes()).hexdigest().upper() == EXPECTED
SOURCE = ROOT / "pack-source"
OUTPUT = ROOT / "dist/sprmine-unified-v1.4.1-clans-1.21.11.zip"
BG, PANEL, EDGE, VIOLET, WHITE = "#18151F", "#272130", "#494052", "#A78BDA", "#F2EEF7"

def emit_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def save(image, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=False)

def frame(rows, main=False, clanless=False):
    height = 114 + rows * 18
    image = Image.new("RGBA", (176, height), BG)
    d = ImageDraw.Draw(image)
    d.rectangle((0, 0, 175, height - 1), outline=EDGE)
    d.line((3, 2, 172, 2), fill=VIOLET)
    d.rectangle((4, 4, 171, rows * 18 + 15), fill=PANEL)
    # Small original pennant. Keep the default Minecraft font untouched.
    d.polygon([(7, 4), (23, 4), (23, 17), (15, 23), (7, 17)], fill="#654B88", outline=VIOLET)
    d.line((15, 7, 15, 16), fill=WHITE, width=1)
    d.line((11, 11, 19, 11), fill=WHITE, width=1)
    if main:
        slots = [10, 12, 14, 16] if clanless else [9, 11, 13, 15, 17]
        for slot in slots:
            x, y = 7 + (slot % 9) * 18, 17 + (slot // 9) * 18
            d.rectangle((x, y, x + 17, y + 17), fill=BG, outline="#59476E")
    d.line((7, rows * 18 + 16, 168, rows * 18 + 16), fill=EDGE)
    # Exactly vanilla container geometry: inventory row 0 starts at rows*18+31.
    for r in range(3):
        for c in range(9):
            x, y = 7 + c * 18, rows * 18 + 30 + r * 18
            d.rectangle((x, y, x + 17, y + 17), fill="#201C27", outline=EDGE)
    for c in range(9):
        x, y = 7 + c * 18, rows * 18 + 88
        d.rectangle((x, y, x + 17, y + 17), fill="#201C27", outline=EDGE)
    return image

def icon(kind):
    im = Image.new("RGBA", (16, 16))
    d = ImageDraw.Draw(im)
    if kind == "team":
        d.rectangle((2, 2, 5, 5), fill=WHITE); d.rectangle((9, 3, 12, 6), fill=VIOLET)
        d.rectangle((0, 8, 7, 13), fill=WHITE); d.rectangle((8, 9, 15, 13), fill=VIOLET)
    elif kind == "growth":
        d.line((8, 3, 8, 13), fill=WHITE); d.line((3, 7, 12, 7), fill=VIOLET)
        for x, y in [(6,0),(0,5),(11,5),(0,11),(11,11)]: d.rectangle((x,y,x+3,y+3), fill=VIOLET)
    elif kind == "events":
        d.rectangle((1, 3, 14, 14), outline=WHITE); d.rectangle((2, 4, 13, 6), fill=VIOLET)
        for x in (4,10): d.line((x,0,x,4),fill=WHITE)
        for x,y in ((4,9),(9,9),(4,12),(9,12)): d.rectangle((x,y,x+1,y+1),fill=VIOLET)
    elif kind == "bank":
        d.rectangle((1, 4, 14, 13), fill="#654B88", outline=WHITE)
        d.line((2,8,13,8),fill=VIOLET); d.rectangle((7,7,8,10),fill=WHITE)
    elif kind == "more":
        for x in (1,6,11): d.rectangle((x,7,x+2,9),fill=VIOLET)
    elif kind == "close":
        d.line((4,4,11,11),fill=WHITE,width=2); d.line((4,11,11,4),fill=WHITE,width=2)
    elif kind == "info":
        d.polygon([(3,2),(12,2),(12,9),(8,14),(3,9)],outline=WHITE,fill="#654B88")
        d.line((8,5,8,10),fill=VIOLET)
    return im

for name, rows, main, clanless in [("main",3,True,False),("clanless",3,True,True),("section",3,False,False),("members",6,False,False)]:
    save(frame(rows,main,clanless), SOURCE / f"assets/sprmine/textures/gui/clans/{name}.png")
providers = [{"type":"space", "advances":{"\uf800":-8,"\uf801":-169,"\uf802":24}}]
for name, height, glyph in [("main",168,"\uf810"),("clanless",168,"\uf811"),("section",168,"\uf812"),("members",222,"\uf813")]:
    providers.append({"type":"bitmap", "file":f"sprmine:gui/clans/{name}.png", "height":height,"ascent":13,"chars":[glyph]})
emit_json(SOURCE / "assets/sprmine/font/clans_ui.json", {"providers":providers})
for name in ("team","growth","events","bank","more","close","info"):
    save(icon(name), SOURCE / f"assets/sprmine/textures/item/clans/{name}.png")
    emit_json(SOURCE / f"assets/sprmine/models/item/clans/{name}.json",
              {"parent":"minecraft:item/generated","textures":{"layer0":f"sprmine:item/clans/{name}"}})
    emit_json(SOURCE / f"assets/sprmine/items/clans/{name}.json",
              {"model":{"type":"minecraft:model","model":f"sprmine:item/clans/{name}"}})
with zipfile.ZipFile(BASE) as z:
    entries = {n:z.read(n) for n in z.namelist() if not n.endswith("/")}
old_entries = dict(entries)
for path in SOURCE.rglob("*"):
    if path.is_file():
        key=path.relative_to(SOURCE).as_posix()
        assert key.startswith("assets/sprmine/"), key
        assert key not in entries, f"unexpected rank resource replacement: {key}"
        entries[key]=path.read_bytes()
metadata = {"pack":{"pack_format":75,"min_format":75,"max_format":75,
                    "description":"SPRMine | ранги и меню кланов | тестовая версия"}}
validate_metadata(metadata)
entries["pack.mcmeta"] = (json.dumps(metadata,ensure_ascii=False)+"\n").encode()
assert all(entries[n] == data for n,data in old_entries.items() if n != "pack.mcmeta")
OUTPUT.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(OUTPUT,"w",zipfile.ZIP_DEFLATED) as z:
    for name,data in sorted(entries.items()):
        info=zipfile.ZipInfo(name,(2026,10,20,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(info,data)
manifest={"file":OUTPUT.name,"bytes":OUTPUT.stat().st_size,"sha1":hashlib.sha1(OUTPUT.read_bytes()).hexdigest(),"sha256":hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),"rank_assets_unchanged":True,"entries":len(entries),"pack_id":"48727862-cfde-3d2c-b25b-196edaa64345"}
emit_json(OUTPUT.parent / "manifest.json",manifest)
print(json.dumps(manifest,indent=2))
