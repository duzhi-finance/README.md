"""進階畫面元素：風格預設 (preset)、頂部標題、旁白樣式、手繪塗鴉、emoji 貼圖。

render.py 會呼叫這裡的函式；所有元素都可以在任何 preset 裡混用。
"""
import math
import pathlib
import re
import subprocess

import yaml

HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent
FONT_DIR = SKILL / "fonts"
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF☀-➿⭐❤️‍]+")


# ── 風格預設 ─────────────────────────────────────────
def deep_merge(a, b):
    out = dict(a)
    for k, v in (b or {}).items():
        out[k] = deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def apply_preset(style, name):
    if not name:
        return style
    p = SKILL / "presets" / f"{name}.yaml"
    if not p.exists():
        raise SystemExit(f"找不到風格預設：{p}")
    return deep_merge(style, yaml.safe_load(open(p, encoding="utf-8")))


# ── 字型檔查找（給 emoji 圖片用）─────────────────────
_font_cache = {}


def font_file(family):
    if family in _font_cache:
        return _font_cache[family]
    for f in sorted(FONT_DIR.glob("*.[ot]t[fc]")):
        fams = subprocess.run(["fc-scan", "--format", "%{family}", str(f)],
                              capture_output=True, text=True).stdout.split(",")
        if family in [x.strip() for x in fams]:
            _font_cache[family] = str(f)
            return str(f)
    path = subprocess.run(["fc-match", "-f", "%{file}", family], capture_output=True, text=True).stdout
    _font_cache[family] = path
    return path


def emoji_font_file():
    return subprocess.run(["fc-match", "-f", "%{file}", "Noto Color Emoji"],
                          capture_output=True, text=True).stdout


# ── 帶 emoji 的文字 → 透明 PNG ─────────────────────────
def render_text_png(text, family, size, fill, glow, glow_alpha, path, spacing=0, stroke=0, stroke_color=None):
    from PIL import Image, ImageDraw, ImageFilter, ImageFont

    font = ImageFont.truetype(font_file(family), size)
    efont = ImageFont.truetype(emoji_font_file(), 109)
    runs, pos = [], 0
    for m in EMOJI_RE.finditer(text):
        if m.start() > pos:
            runs.append(("t", text[pos:m.start()]))
        runs.append(("e", m.group()))
        pos = m.end()
    if pos < len(text):
        runs.append(("t", text[pos:]))

    pieces, width = [], 0
    for kind, s in runs:
        if kind == "t":
            for ch in s:
                w = font.getlength(ch) + spacing
                pieces.append(("t", ch, width))
                width += w
        else:
            s = s.replace("️", "")
            for ch in s:
                if ch == "‍":
                    continue
                im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
                ImageDraw.Draw(im).text((10, 10), ch, font=efont, embedded_color=True)
                bb = im.getbbox()
                if not bb:
                    continue
                im = im.crop(bb)
                sc = size * 1.0 / im.height
                im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
                pieces.append(("e", im, width + size * 0.05))
                width += im.width + size * 0.1 + spacing

    pad = int(size * 0.5)
    W, H = int(width) + pad * 2, int(size * 1.5) + pad * 2
    base_y = pad + int(size * 0.1)
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(txt)
    for kind, obj, x in pieces:
        if kind == "t":
            d.text((pad + x, base_y), obj, font=font, fill=fill,
                   stroke_width=stroke, stroke_fill=stroke_color or fill)
        else:
            txt.alpha_composite(obj, (int(pad + x), int(base_y + size * 0.18)))
    # 柔和光暈陰影
    a = txt.getchannel("A").filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(size * 0.08))
    a = a.point(lambda v: int(v * glow_alpha))
    shadow = Image.new("RGBA", (W, H), glow)
    shadow.putalpha(a)
    out = Image.alpha_composite(shadow, txt)
    out = out.crop(out.getbbox())
    out.save(path)
    return out.size


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def extract_emoji_overlays(plan, style, tmp):
    """把含 emoji 的字卡抽出來改成圖片貼圖（libass 不支援彩色 emoji）。"""
    W, H = style["output"]["width"], style["output"]["height"]
    f, sub, emp = style["fonts"], style["subtitle"], style["emphasis"]
    overlays, k = [], 0

    def make(text, family, size, color, glow, glow_alpha, x, y, start, end, spacing=0, pop=False):
        nonlocal k
        p = tmp / f"emo_{k}.png"
        k += 1
        w, h = render_text_png(text, family, size, hex_rgb(color) + (255,), hex_rgb(glow) + (255,),
                               glow_alpha, p, spacing=spacing)
        overlays.append({"file": str(p), "w": w, "h": h, "cx": x * W, "cy": y * H,
                         "start": start, "end": end, "pop": pop})

    for key in ("captions", "emphasis", "asides", "title"):
        keep = []
        for e in plan.get(key, []):
            text = e.get("text", "")
            if key == "emphasis" and e.get("sub") and EMOJI_RE.search(e["sub"]):
                sy = e.get("y", emp["y"]) + emp["sub_gap"] / H
                make(e["sub"], f.get("emphasis_sub", f["serif"]), emp["sub_size"], emp["sub_color"],
                     emp["shadow_color"], emp["shadow_alpha"], e.get("x", 0.5), sy, e["start"], e["end"])
                e = {**e, "sub": None}
            if not EMOJI_RE.search(text):
                keep.append(e)
                continue
            if key == "captions":
                make(text, f["serif"], sub["size"], sub["color"], sub["shadow_color"], sub["shadow_alpha"],
                     e.get("x", 0.5), e.get("y", sub["y"]), e["start"], e["end"])
            elif key == "emphasis":
                make(text, f["emphasis"], emp["size"], emp["color"], emp["shadow_color"], emp["shadow_alpha"],
                     e.get("x", 0.5), e.get("y", emp["y"]), e["start"], e["end"], pop=True)
            elif key == "asides":
                look = aside_look(style, e)
                make(text, look.get("font", f["serif"]), look["size"], look["color"],
                     look.get("glow_color", "#000000"), look.get("glow_alpha", 0.4),
                     e.get("x", look["x"]), e.get("y", look["y"]), e["start"], e["end"])
            else:
                t = style["title"]
                make(text, t["font"], t["size"], t["color"], t["shadow_color"], t["shadow_alpha"],
                     e.get("x", 0.5), e.get("y", t["y"]), e["start"], e["end"])
        plan[key] = keep
    for e in plan.get("emoji", []):  # 單獨的 emoji 貼圖
        make(e["emoji"], f["serif"], int(e.get("size", 120)), "#FFFFFF", "#000000", e.get("glow", 0.25),
             e.get("x", 0.7), e.get("y", 0.4), e["start"], e["end"], pop=True)
    return overlays


def aside_look(style, e):
    asd = style["aside"]
    look = dict(asd)
    name = e.get("look") or asd.get("default_look")
    look.update(style.get("aside_looks", {}).get(name, {}))
    return look


# ── 額外的 ASS 樣式與事件 ─────────────────────────────
def extra_styles(style, sty, ass_color):
    out = []
    t = style["title"]
    out.append(sty("Title", t["font"], t["size"], True, ass_color(t["color"]),
                   ass_color(t["outline_color"], 1 - t["outline_alpha"]), t["outline"], t["letter_spacing"],
                   back=t["shadow_color"], back_alpha=1 - t["shadow_alpha"], shadow=t["shadow"]))
    for name, lk in style.get("aside_looks", {}).items():
        lk = aside_look(style, {"look": name})
        out.append(sty(f"Aside_{name}", lk.get("font", style["fonts"]["serif"]), lk["size"], True,
                       ass_color(lk["color"]), ass_color(lk["outline_color"], 1 - lk.get("outline_alpha", 1)),
                       lk["outline"], lk.get("letter_spacing", 2)))
    d = style["doodle"]
    out.append(sty("Doodle", d["font"], 100, True, ass_color(d["color"]),
                   ass_color(d["shadow_color"], 1 - d["shadow_alpha"]), 4, 0))
    return out


def doodle_events(plan, style, timeline, map_events, ev):
    W, H = style["output"]["width"], style["output"]["height"]
    d = style["doodle"]
    white, shadow = d["color"], d["shadow_color"]
    for e in map_events(plan.get("doodles", []), timeline):
        x, y = int(e.get("x", 0.72) * W), int(e.get("y", 0.42) * H)
        s = float(e.get("scale", 1.0))
        kind = e.get("type", "question")
        rot = e.get("rot", 0)
        pop = r"\fscx40\fscy40\t(0,160,\fscx100\fscy100)" if kind != "shock" else ""
        base = rf"\an5\pos({x},{y})\frz{rot}\fad(80,120)"
        if kind == "question":
            ev(6, e, "Doodle", base + rf"\fs{int(230 * s)}\blur3" + pop, "?")
        elif kind == "exclaim":
            ev(6, e, "Doodle", base + rf"\fs{int(230 * s)}\blur3" + pop, "!")
        elif kind == "heart":
            ev(6, e, "Doodle", base + rf"\fs{int(170 * s)}\fnNoto Sans CJK TC\1c&HB0A2F6&\blur3" + pop, "♥")
        elif kind == "sparkle":
            r = int(55 * s)
            star = (f"m 0 {-r} b {r * .12:.0f} {-r * .12:.0f} {r * .12:.0f} {-r * .12:.0f} {r} 0 "
                    f"b {r * .12:.0f} {r * .12:.0f} {r * .12:.0f} {r * .12:.0f} 0 {r} "
                    f"b {-r * .12:.0f} {r * .12:.0f} {-r * .12:.0f} {r * .12:.0f} {-r} 0 "
                    f"b {-r * .12:.0f} {-r * .12:.0f} {-r * .12:.0f} {-r * .12:.0f} 0 {-r}")
            for dx, dy, k in ((0, 0, 1.0), (int(70 * s), int(-60 * s), 0.5)):
                ev(6, e, "Doodle", rf"\an5\pos({x + dx},{y + dy})\fad(80,120)\bord2\blur2\fscx{int(100 * k)}"
                                   rf"\fscy{int(100 * k)}\t(0,400,\frz20)\p1", star)
        elif kind == "squiggle":
            s *= 1.6
            L, A = int(220 * s), int(30 * s)
            fwd = " ".join(f"b {i * L / 4 + L / 12:.0f} {-A if i % 2 == 0 else A} "
                           f"{i * L / 4 + L / 6:.0f} {-A if i % 2 == 0 else A} {(i + 1) * L / 4:.0f} 0"
                           for i in range(4))
            back = " ".join(f"b {(3 - i) * L / 4 + L / 6:.0f} {-A if (3 - i) % 2 == 0 else A} "
                            f"{(3 - i) * L / 4 + L / 12:.0f} {-A if (3 - i) % 2 == 0 else A} {(3 - i) * L / 4:.0f} 0"
                            for i in range(4))
            path = f"m 0 0 {fwd} {back}"
            ev(5, e, "Doodle", base + rf"\1a&HFF&\3c{shadow_ass(shadow)}\3a&H90&\bord{int(14 * s)}\blur6\p1", path)
            x0, x1 = x - L // 2 - 30, x + L // 2 + 30
            ev(6, e, "Doodle", base + rf"\1a&HFF&\3c{shadow_ass(white)}\3a&H00&\bord{int(9 * s)}\blur1"
                                      rf"\clip({x0},0,{x0},{H})\t(0,350,\clip({x0},0,{x1},{H}))\p1", path)
        elif kind == "shock":  # 震驚放射線
            n = int(e.get("lines", 11))
            a0, a1 = e.get("arc", [-160, 160])
            for i in range(n):
                ang = math.radians(a0 + (a1 - a0) * i / max(1, n - 1))
                r = int((95 + (i % 3) * 14) * s)
                ln = int((60 + (i * 37 % 4) * 14) * s)
                th = int(13 * s)
                px, py = x + r * math.cos(ang), y + r * math.sin(ang)
                col = shadow_ass("#FFFFFF" if i % 2 else "#8E8A86")
                ev(5, e, "Doodle", rf"\an4\pos({px:.0f},{py:.0f})\org({px:.0f},{py:.0f})"
                                   rf"\frz{-math.degrees(ang):.0f}\1c{col}\bord0\blur1.5"
                                   rf"\fad({60 + i * 15},120)\p1", f"m 0 0 l {ln} 0 l {ln} {th} l 0 {th}")


def shadow_ass(hex_):
    r, g, b = hex_rgb(hex_)
    return f"&H{b:02X}{g:02X}{r:02X}&"


def title_events(plan, style, timeline, map_events, ev):
    W, H = style["output"]["width"], style["output"]["height"]
    t = style["title"]
    for e in map_events(plan.get("title", []), timeline):
        y = int(e.get("y", t["y"]) * H)
        ev(7, e, "Title", rf"\an5\pos({int(e.get('x', 0.5) * W)},{y})\blur{t['blur']}\fad(150,150)", e["text"])


# ── emoji 貼圖疊加的 ffmpeg 濾鏡 ───────────────────────
def overlay_filters(overlays, timeline, map_events, first_input, fps, total, src_label):
    """回傳 (額外 -i 參數, 濾鏡字串列表, 最後的輸出標籤)。"""
    args, fg, label, k = [], [], src_label, first_input
    for i, o in enumerate(overlays):
        evs = map_events([o], timeline)
        if not evs:
            continue
        args += ["-loop", "1", "-framerate", str(fps), "-t", f"{total:.3f}", "-i", o["file"]]
        for j, e in enumerate(evs):
            a, b = e["out_start"], e["out_end"]
            x, y = int(o["cx"] - o["w"] / 2), int(o["cy"] - o["h"] / 2)
            fl = f"ov{i}_{j}"
            fg.append(f"[{k}:v]format=rgba,fade=t=in:st={a:.3f}:d=0.12:alpha=1,"
                      f"fade=t=out:st={max(a, b - 0.12):.3f}:d=0.12:alpha=1[{fl}]")
            nl = f"vo{i}_{j}"
            fg.append(f"[{label}][{fl}]overlay={x}:{y}:enable='between(t,{a:.3f},{b:.3f})'[{nl}]")
            label = nl
            if j + 1 < len(evs):
                args += ["-loop", "1", "-framerate", str(fps), "-t", f"{total:.3f}", "-i", o["file"]]
                k += 1
        k += 1
    return args, fg, label, k
