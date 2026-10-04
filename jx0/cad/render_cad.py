"""Render the SolidWorks assembly (jx0/cad/JX0_Robot.SLDASM) to PNG views and compose the README cover.

    python jx0/cad/render_cad.py        -> jx0/cad/images/jx0_cad_{front,back,side,legs}.png, jx0/docs/images/jx0_cover.png

The views are exported with ModelDocExtension.SaveAs3 (works even when the SolidWorks window is covered). The cover
puts the front and back views next to a still of the simulated robot (jx0/results/images/jx0_demo_walk.png).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from swlib.core import C, Session, set_view, typed  # noqa: E402

ASM = ROOT / "jx0" / "cad" / "JX0_Robot.SLDASM"
IMG = ROOT / "jx0" / "cad" / "images"
VIEWS = {"front": (1.0, -0.8, 0.45), "back": (-1.0, 0.8, 0.45), "side": (0.0, -1.0, 0.25), "legs": (0.9, -1.0, 0.1)}


def export_views():
    s = Session()
    doc = s.open_doc(ASM.resolve())
    IMG.mkdir(parents=True, exist_ok=True)
    out = {}
    for name, eye in VIEWS.items():
        set_view(s.app, doc, eye=eye)
        if name == "legs":                                      # zoom onto the legs
            typed(doc.ActiveView, "IModelView")
            doc.ViewZoomTo2(-0.09, -0.11, -0.16, 0.09, 0.11, 0.06)
        path = (IMG / f"jx0_cad_{name}.png").resolve()
        ext = typed(doc.Extension, "IModelDocExtension")
        ok = ext.SaveAs3(str(path), C.swSaveAsCurrentVersion, C.swSaveAsOptions_Silent | C.swSaveAsOptions_Copy, None, None, 0, 0)
        out[name] = path
        print(name, ok, path.relative_to(ROOT))
    return out


def compose_cover(views):
    from PIL import Image, ImageChops

    def crop(im):
        bg = Image.new(im.mode, im.size, im.getpixel((2, 2)))
        box = ImageChops.difference(im, bg).getbbox()
        return im.crop(box) if box else im
    front, back = (crop(Image.open(views[k]).convert("RGB")) for k in ("front", "back"))
    sim_path = ROOT / "jx0" / "results" / "images" / "jx0_demo_walk.png"
    H = 640
    tiles = [front, back]
    if sim_path.exists():
        sim = Image.open(sim_path).convert("RGB")
        w, h = sim.size
        tiles.append(sim.crop((int(w * 0.30), 0, int(w * 0.78), h)))
    tiles = [t.resize((int(t.width * H / t.height), H)) for t in tiles]
    bg = (196, 202, 214)
    cover = Image.new("RGB", (sum(t.width for t in tiles) + 20 * (len(tiles) - 1), H), bg)
    x = 0
    for t in tiles:
        cover.paste(t, (x, 0))
        x += t.width + 20
    out = ROOT / "jx0" / "docs" / "images" / "jx0_cover.png"
    cover.save(out)
    print("cover", out.relative_to(ROOT), cover.size)


if __name__ == "__main__":
    v = export_views() if "--cover-only" not in sys.argv else {k: IMG / f"jx0_cad_{k}.png" for k in VIEWS}
    compose_cover(v)
