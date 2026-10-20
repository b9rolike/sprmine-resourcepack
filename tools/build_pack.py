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
OUTPUT = ROOT / "dist/sprmine-unified-v1.5.0-clans-1.21.11.zip"
BG, PANEL, EDGE, VIOLET, WHITE = "#15131C", "#252130", "#51415F", "#B39ADE", "#F4F0F8"

def emit_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def save(image, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=False)

# Original 5x7 Cyrillic captions. No copied vanilla font or global font override.
PIXELS = {
 "а":[14,17,17,31,17,17,17],"б":[31,16,16,30,17,17,30],
 "в":[30,17,17,30,17,17,30],"г":[31,16,16,16,16,16,16],
 "д":[14,10,10,10,17,31,17],"е":[31,16,16,30,16,16,31],
 "з":[30,1,1,14,1,1,30],"и":[17,19,21,21,25,17,17],
 "й":[10,4,17,19,21,25,17],"к":[17,18,20,24,20,18,17],
 "л":[7,9,9,9,9,17,17],"м":[17,27,21,21,17,17,17],
 "н":[17,17,17,31,17,17,17],"о":[14,17,17,17,17,17,14],
 "п":[31,17,17,17,17,17,17],"р":[30,17,17,30,16,16,16],
 "с":[15,16,16,16,16,16,15],"т":[31,4,4,4,4,4,4],
 "ь":[16,16,16,30,17,17,30],"ы":[17,17,17,29,19,19,29],
 "я":[15,17,17,15,5,9,17],"щ":[21,21,21,21,21,31,1],
}

def caption(draw, text, center, y):
    x=center-(len(text)*6-1)//2
    for letter in text:
        for row,bits in enumerate(PIXELS[letter]):
            for column in range(5):
                if bits & (1 << (4-column)):draw.point((x+column,y+row),fill=WHITE)
        x+=6

def frame(rows, main=False, clanless=False, theme="generic"):
    height = 114 + rows * 18
    image = Image.new("RGBA", (176, height), BG)
    d = ImageDraw.Draw(image)
    d.rectangle((0, 0, 175, height - 1), outline=EDGE)
    d.rectangle((2, 2, 173, height - 3), outline="#30283B")
    d.line((7, 2, 168, 2), fill=VIOLET)
    d.rectangle((4, 4, 171, rows * 18 + 15), fill=PANEL)
    # Small original pennant. Keep the default Minecraft font untouched.
    d.polygon([(7, 4), (23, 4), (23, 17), (15, 23), (7, 17)], fill="#654B88", outline=VIOLET)
    d.line((15, 7, 15, 16), fill=WHITE, width=1)
    d.line((11, 11, 19, 11), fill=WHITE, width=1)
    if main:
        buttons = [(10,"поиск"),(16,"создать"),(29,"топ"),(33,"еще")] if clanless else [
            (10,"команда"),(13,"развитие"),(16,"события"),(29,"банк"),(33,"еще")]
        for slot,text in buttons:
            center=16+(slot%9)*18
            y=18+(slot//9)*18
            d.rounded_rectangle((center-25,y-3,center+25,y+28),radius=2,fill=BG,outline="#59466D")
            d.line((center-20,y-2,center+20,y-2),fill="#79648F")
            caption(d,text,center,y+18)
    if theme=="bank":
        for slot,text in ((11,"внести"),(13,"баланс"),(15,"снять")):
            center=16+(slot%9)*18
            d.rounded_rectangle((center-14,34,center+14,53),radius=2,fill=BG,outline="#79648F")
            caption(d,text,center,55)
    # Quiet motif identifies each screen, without altering click geometry.
    motif = {"bank":"bank", "development":"growth", "shop":"palette",
             "chronicle":"document", "staff":"info", "team":"team"}.get(theme,"info")
    stamp = icon(motif)
    stamp.putalpha(stamp.getchannel("A").point(lambda a: a//3))
    image.alpha_composite(stamp,(153,4))
    footer=rows*18-1
    if not main:d.line((7,footer,168,footer),fill="#3C3148")
    d.rectangle((5,rows*18+17,170,rows*18+28),fill="#AAA1B6")
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
    if kind == "hitbox":
        return im
    if kind == "team":
        d.rectangle((3,2,6,5),fill=WHITE);d.rectangle((10,3,12,5),fill=VIOLET)
        d.polygon([(1,13),(2,9),(4,7),(6,7),(8,9),(9,13)],fill=VIOLET,outline=WHITE)
        d.polygon([(10,8),(13,7),(15,10),(15,13),(11,13)],fill="#79618F",outline=VIOLET)
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
    elif kind == "confirm":
        d.line([(2,8),(6,12),(14,3)],fill=VIOLET,width=3)
        d.line([(2,7),(6,11),(14,2)],fill=WHITE,width=1)
    elif kind == "cancel":
        d.ellipse((1,1,14,14),outline="#C9839D")
        d.line((5,5,10,10),fill=WHITE,width=2);d.line((5,10,10,5),fill=WHITE,width=2)
    elif kind == "info":
        d.polygon([(3,2),(12,2),(12,9),(8,14),(3,9)],outline=WHITE,fill="#654B88")
        d.line((8,5,8,10),fill=VIOLET)
    elif kind in ("back","previous","next"):
        points=[(10,3),(5,8),(10,13)] if kind!="next" else [(5,3),(10,8),(5,13)]
        d.line(points,fill=WHITE,width=2)
        if kind=="back":d.line((6,8,14,8),fill=VIOLET,width=2)
    elif kind in ("deposit","withdraw"):
        d.ellipse((1,7,11,14),fill="#72578F",outline=WHITE)
        d.line((12,1,12,9),fill=VIOLET,width=2)
        d.line([(9,4),(12,1),(15,4)] if kind=="withdraw" else [(9,6),(12,9),(15,6)],fill=WHITE,width=1)
    elif kind=="coins":
        for x,y in ((1,7),(6,3),(8,8)):
            d.ellipse((x,y,x+6,y+5),fill="#72578F",outline=WHITE)
            d.point((x+3,y+2),fill=VIOLET)
    elif kind=="lock":
        d.arc((4,1,11,10),180,360,fill=WHITE,width=2)
        d.rectangle((2,7,13,14),fill="#72578F",outline=VIOLET)
        d.line((8,9,8,12),fill=WHITE)
    elif kind in ("document","guide"):
        d.polygon([(3,1),(10,1),(13,4),(13,14),(3,14)],fill="#30283B",outline=WHITE)
        for y in (6,9,12):d.line((5,y,10,y),fill=VIOLET)
    elif kind=="filter":
        d.polygon([(1,3),(14,3),(9,9),(9,13),(6,14),(6,9)],outline=WHITE,fill="#72578F")
    elif kind=="sort":
        for y,length in ((4,12),(8,8),(12,4)):d.line((2,y,length,y),fill=WHITE,width=2)
        d.line((13,6,13,14),fill=VIOLET);d.line([(11,12),(13,14),(15,12)],fill=VIOLET)
    elif kind=="target":
        d.ellipse((2,2,13,13),outline=WHITE,width=1);d.ellipse((5,5,10,10),outline=VIOLET)
        d.line((8,8,14,1),fill=WHITE,width=1)
    elif kind=="palette":
        d.ellipse((1,2,14,13),fill="#72578F",outline=WHITE)
        for xy in ((4,5),(8,4),(11,7),(5,10)):d.rectangle((xy[0],xy[1],xy[0]+1,xy[1]+1),fill=WHITE)
    elif kind in ("chest","shop"):
        d.rectangle((2,4,13,13),fill="#72578F",outline=WHITE)
        d.line((3,8,12,8),fill=VIOLET);d.rectangle((7,7,8,10),fill=WHITE)
        if kind=="shop":d.line((1,3,14,3),fill=VIOLET,width=2)
    elif kind=="allies":
        d.arc((1,5,10,12),30,300,fill=WHITE,width=2);d.arc((6,3,15,10),210,120,fill=VIOLET,width=2)
    elif kind=="settings":
        d.ellipse((3,3,12,12),outline=WHITE,width=2);d.ellipse((6,6,9,9),fill=VIOLET)
        for xy in ((7,0,8,3),(7,12,8,15),(0,7,3,8),(12,7,15,8)):d.rectangle(xy,fill=VIOLET)
    elif kind=="swords":
        d.line((3,2,13,13),fill=WHITE,width=2);d.line((13,2,3,13),fill=VIOLET,width=2)
        d.line((1,10,5,14),fill=WHITE);d.line((10,14,14,10),fill=VIOLET)
    else:
        raise ValueError(f"missing icon: {kind}")
    return im

for name, rows, main, clanless in [("main",5,True,False),("clanless",5,True,True),("section",3,False,False),("members",6,False,False)]:
    save(frame(rows,main,clanless, "team" if name=="members" else "generic"), SOURCE / f"assets/sprmine/textures/gui/clans/{name}.png")
providers = [{"type":"space", "advances":{"\uf800":-8,"\uf801":-169,"\uf802":24}}]
for name, height, glyph in [("main",204,"\uf810"),("clanless",204,"\uf811"),("section",168,"\uf812"),("members",222,"\uf813")]:
    providers.append({"type":"bitmap", "file":f"sprmine:gui/clans/{name}.png", "height":height,"ascent":13,"chars":[glyph]})
for theme_index,theme in enumerate(("generic","bank","development","shop","chronicle","staff")):
    for rows in range(3,7):
        name=f"{theme}_{rows}"
        save(frame(rows,theme=theme), SOURCE / f"assets/sprmine/textures/gui/clans/{name}.png")
        providers.append({"type":"bitmap","file":f"sprmine:gui/clans/{name}.png",
                          "height":114+rows*18,"ascent":13,"chars":[chr(0xf820+theme_index*4+rows-3)]})
emit_json(SOURCE / "assets/sprmine/font/clans_ui.json", {"providers":providers})
for name in ("team","growth","events","bank","more","close","info","back","previous","next",
             "deposit","withdraw","coins","lock","document","guide","filter","sort","target",
             "palette","chest","shop","allies","settings","swords","hitbox","confirm","cancel"):
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
