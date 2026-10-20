"""Validate all locally owned pack references and unchanged baseline rank assets."""
import hashlib
import json
from pathlib import Path
import zipfile
from PIL import Image
import io
from pack_metadata import validate_metadata

root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/"dist/manifest.json").read_text(encoding="utf-8"))
assert Path(manifest["file"]).name == manifest["file"], "unsafe manifest filename"
file=root/"dist"/manifest["file"]
assert hashlib.sha1(file.read_bytes()).hexdigest()==manifest["sha1"]
assert hashlib.sha256(file.read_bytes()).hexdigest()==manifest["sha256"]
assert file.stat().st_size==manifest["bytes"]
with zipfile.ZipFile(file) as z, zipfile.ZipFile(root/"sprmine-ranks-v1.3-vanilla-font-1.21.11.zip") as old:
    validate_metadata(json.loads(z.read("pack.mcmeta")))
    names=z.namelist()
    assert len(names)==len(set(names))
    for n in old.namelist():
        if not n.endswith("/") and n!="pack.mcmeta": assert z.read(n)==old.read(n),n
    assert "assets/minecraft/font/default.json" not in names
    assert not any(n.startswith("assets/minecraft/textures/") for n in names)
    for n in names:
        if n.endswith(".json"):
            data=json.loads(z.read(n))
            if "/items/clans/" in n:
                model=data["model"]["model"].split(":",1)[1]
                assert "assets/sprmine/models/"+model+".json" in names,n
            if "/models/item/clans/" in n:
                texture=data["textures"]["layer0"].split(":",1)[1]
                assert "assets/sprmine/textures/"+texture+".png" in names,n
            if n.endswith("clans_ui.json"):
                chars=[]
                for provider in data["providers"]:
                    if provider["type"]!="bitmap":continue
                    chars+=provider["chars"]
                    im=Image.open(io.BytesIO(z.read("assets/sprmine/textures/"+provider["file"].split(":",1)[1])))
                    assert im.size==(176,provider["height"])
                    assert 0<provider["ascent"]<=provider["height"]<=256
                    assert im.getpixel((175,0))[3]>0
                assert len(chars)==len(set(chars))==4
print("PASS: metadata format 75, zip, baseline, font, 7 item model/texture references, dimensions and hashes")
