#!/usr/bin/env python3
"""把剪輯計畫 (plan.json) + 風格 (style.yaml) 輸出成成品影片。

用法:
    python render.py work/plan.json -o out/final.mp4 [--style ../style.yaml] [--preview]

plan.json 格式（時間全部用「原始影片」的秒數）：
{
  "source": "/abs/path/input.mp4",
  "clips": [                                   # 依序接起來的片段，可以重排、可以重複（例如把金句放片頭當鉤子）
    {"start": 1.2, "end": 3.4, "zoom": 1.0},
    {"start": 3.6, "end": 5.0, "zoom": 1.45},              # 特寫
    {"start": 5.2, "end": 7.0, "zoom": 1.0, "zoom_to": 1.2},  # 慢慢推近
    {"start": 7.1, "end": 9.0, "effect": "shrink"}         # 縮小畫面 + 黑底
  ],
  "captions": [{"start": 1.3, "end": 2.2, "text": "這篇請你"}],
  "emphasis": [{"start": 6.0, "end": 6.8, "text": "復發過", "sub": "（抗戰成功）"}],
  "asides":   [{"start": 2.0, "end": 3.2, "text": "（婦產科VIP本人）"}],
  "layered":  [{"start": 4.0, "end": 5.0, "text": "可以根治"}],
  "bgm": null,
  "mute_source": false                         # true = 原音靜音（沒有講話、只想配音樂時）
}
"""
import argparse
import json
import pathlib
import shutil
import subprocess
import tempfile

import yaml

HERE = pathlib.Path(__file__).resolve().parent


# ── 小工具 ───────────────────────────────────────────
def ass_color(hex_rgb, alpha=0.0):
    h = hex_rgb.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    a = int(round(max(0.0, min(1.0, alpha)) * 255))
    return f"&H{a:02X}{b}{g}{r}".upper()


def ass_time(t):
    t = max(0.0, t)
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def ass_text(text):
    return text.replace("{", "｛").replace("}", "｝").replace("\n", r"\N")


def has_audio(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a",
                          "-show_entries", "stream=index", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True)
    return bool(out.stdout.strip())


def subtract(intervals, holes):
    """從 intervals 挖掉 holes 的時間範圍（用來讓重點大字出現時暫停一般字幕）。"""
    out = []
    for it in intervals:
        pieces = [(it["start"], it["end"])]
        for h in holes:
            nxt = []
            for s, e in pieces:
                if h["end"] <= s or h["start"] >= e:
                    nxt.append((s, e))
                    continue
                if h["start"] - s > 0.15:
                    nxt.append((s, h["start"]))
                if e - h["end"] > 0.15:
                    nxt.append((h["end"], e))
            pieces = nxt
        out += [dict(it, start=s, end=e) for s, e in pieces]
    return out


# ── 時間換算：原片時間 → 成品時間 ─────────────────────
def build_timeline(clips, fps):
    t, tl = 0.0, []
    for c in clips:
        d = round((c["end"] - c["start"]) * fps) / fps
        tl.append({**c, "dur": d, "out": t})
        t += d
    return tl, t


def map_events(items, timeline):
    """把每個字卡對應到成品時間；跨剪接點的會自動合併，重複使用的片段會各出現一次。"""
    events = []
    for it in items:
        last = None
        for c in timeline:
            s = max(it["start"], c["start"])
            e = min(it["end"], c["start"] + c["dur"])
            if e - s < 0.05:
                continue
            os_, oe = c["out"] + s - c["start"], c["out"] + e - c["start"]
            if last and abs(last["out_end"] - os_) < 0.02:
                last["out_end"] = oe
            else:
                last = {**it, "out_start": os_, "out_end": oe}
                events.append(last)
    return events


# ── 字幕檔 (ASS) ─────────────────────────────────────
def make_ass(plan, style, timeline):
    W, H = style["output"]["width"], style["output"]["height"]
    f = style["fonts"]
    sub, emp, asd, lay = style["subtitle"], style["emphasis"], style["aside"], style["layered"]

    def sty(name, font, size, bold, primary, outline_c, outline, spacing, back="#000000", shadow=0):
        return (f"Style: {name},{font},{size},{primary},{primary},{outline_c},{ass_color(back, 0.6)},"
                f"{-1 if bold else 0},0,0,0,100,100,{spacing},0,1,{outline},{shadow},5,0,0,0,1")

    styles = [
        sty("Sub", f["serif"], sub["size"], sub["bold"], ass_color(sub["color"]),
            ass_color(sub["shadow_color"], 1 - sub["shadow_alpha"]), 3, sub["letter_spacing"]),
        sty("Emph", f["emphasis"], emp["size"], emp["bold"], ass_color(emp["color"]),
            ass_color(emp["shadow_color"], 1 - emp["shadow_alpha"]), 4, emp["letter_spacing"]),
        sty("EmphSub", f["serif"], emp["sub_size"], True, ass_color(emp["sub_color"]),
            ass_color(emp["shadow_color"], 1 - emp["shadow_alpha"]), 3, sub["letter_spacing"]),
        sty("Aside", f["serif"], asd["size"], asd["bold"], ass_color(asd["color"]),
            ass_color(asd["outline_color"]), asd["outline"], 2),
        sty("Layer", f["emphasis"], lay["size"], lay["bold"], ass_color(lay["color"], lay["alpha"]),
            ass_color(lay["color"], 1.0), 0, lay["letter_spacing"]),
    ]

    lines = []

    def ev(layer, e, style_name, tags, text):
        lines.append(f"Dialogue: {layer},{ass_time(e['out_start'])},{ass_time(e['out_end'])},"
                     f"{style_name},,0,0,0,,{{{tags}}}{ass_text(text)}")

    cx = W // 2
    captions = subtract(plan.get("captions", []), plan.get("emphasis", []))
    for e in map_events(plan.get("layered", []), timeline):
        ev(0, e, "Layer", rf"\an5\pos({cx},{int(lay['y'] * H)})\blur{lay['blur']}\fad(120,120)", e["text"])
    for e in map_events(captions, timeline):
        ev(2, e, "Sub", rf"\an5\pos({cx},{int(sub['y'] * H)})\blur{sub['blur']}", e["text"])
    for e in map_events(plan.get("emphasis", []), timeline):
        p = int(emp["pop"] * 100)
        y = int(emp["y"] * H)
        ev(3, e, "Emph", rf"\an5\pos({cx},{y})\blur{emp['blur']}\fad(60,150)"
                         rf"\fscx{p}\fscy{p}\t(0,180,\fscx100\fscy100)", e["text"])
        if e.get("sub"):
            ev(3, e, "EmphSub", rf"\an5\pos({cx},{y + emp['sub_gap']})\blur{sub['blur']}\fad(150,150)", e["sub"])
    for e in map_events(plan.get("asides", []), timeline):
        ev(4, e, "Aside", rf"\an5\pos({int(asd['x'] * W)},{int(asd['y'] * H)})\frz{asd['tilt']}"
                          rf"\fad(80,80)", e["text"])

    return "\n".join([
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}",
        "WrapStyle: 2", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
        "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        *styles, "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        *lines, "",
    ])


# ── 自動特效與音效 ───────────────────────────────────
def clip_at(timeline, t):
    """回傳原片時間 t 第一次出現在成品中的 (clip, 成品時間)。"""
    for c in timeline:
        if c["start"] <= t < c["start"] + c["dur"]:
            return c, c["out"] + t - c["start"]
    return None, None


def apply_auto_fx(plan, style, timeline):
    auto = style.get("effects", {})
    for c in timeline:
        c.setdefault("fx", list(c.get("fx", [])))
        if c.get("effect") == "shrink" and auto.get("flash_on_shrink") and "flash" not in c["fx"]:
            c["fx"].append("flash")
    if auto.get("shake_on_emphasis"):
        for e in plan.get("emphasis", []):
            for c in timeline:
                if c["start"] <= e["start"] < c["start"] + c["dur"]:
                    c.setdefault("_shake_at", []).append(e["start"] - c["start"])


def collect_sfx(plan, style, timeline):
    cfg = style.get("sfx", {})
    if not cfg.get("enabled") or plan.get("sfx") is False:
        return []
    folder = (HERE.parent / cfg.get("folder", "sfx")).resolve()
    base = cfg.get("volume", 0.5)
    auto = cfg.get("auto", {}) if plan.get("auto_sfx", True) else {}
    ev = []

    def add(at, name, vol=1.0):
        f = folder / f"{name}.wav"
        if name and f.exists() and at is not None:
            ev.append({"at": max(0.0, at), "file": str(f), "volume": base * vol})

    if auto.get("intro"):
        add(0.0, auto["intro"], 0.7)
    for key in ("emphasis", "asides", "layered"):
        name = auto.get(key)
        for e in plan.get(key, []) if name else []:
            for c in timeline:
                if c["start"] <= e["start"] < c["start"] + c["dur"]:
                    add(c["out"] + e["start"] - c["start"], name)
    for prev, c in zip(timeline, timeline[1:]):
        if c.get("effect") == "shrink" and auto.get("shrink"):
            add(c["out"], auto["shrink"])
        elif auto.get("zoom_cut") and abs(float(c.get("zoom", 1)) - float(prev.get("zoom", 1))) >= 0.25:
            add(c["out"] - 0.12, auto["zoom_cut"], cfg.get("zoom_cut_volume", 0.4))
    for e in plan.get("sfx") or []:  # 手動指定：{"at": 原片秒數, "name": "pop", "volume": 1}
        _, at = clip_at(timeline, e["at"])
        add(at, e["name"], e.get("volume", 1.0))
    return ev


# ── 畫面濾鏡 ─────────────────────────────────────────
def video_chain(c, style):
    W, H = style["output"]["width"], style["output"]["height"]
    cam, g = style["camera"], style["grade"]
    fy = c.get("focus_y", cam["focus_y"])
    chain = [f"scale={W}:{H}:force_original_aspect_ratio=increase", f"crop={W}:{H}", "setsar=1"]

    z0 = float(c.get("zoom", 1.0))
    z1 = float(c.get("zoom_to", z0))
    if z1 != z0:  # 慢慢推近 / 拉遠
        z = f"({z0}+({z1 - z0})*min(t/{c['dur']:.3f},1))"
        chain += [f"scale=w='trunc({W}*{z}/2)*2':h='trunc({H}*{z}/2)*2':eval=frame",
                  f"crop={W}:{H}:x='(iw-{W})/2':y='(ih-{H})*{fy}'"]
    elif z0 > 1.0:
        chain += [f"scale={int(W * z0) // 2 * 2}:{int(H * z0) // 2 * 2}",
                  f"crop={W}:{H}:x=(iw-{W})/2:y=(ih-{H})*{fy}"]

    fx = c.get("fx", [])
    for st in c.get("_shake_at", []):  # 震一下：重點大字出現的瞬間
        k = f"if(gte(t,{st:.3f}),max(0,1-(t-{st:.3f})/0.35),0)"
        chain += [f"scale={W + 60}:{H + 104}",
                  f"crop={W}:{H}:x='30+26*sin((t-{st:.3f})*70)*{k}':y='52+22*cos((t-{st:.3f})*55)*{k}'"]
    if g.get("soften", 0) > 0:
        chain.append(f"smartblur=lr=2.0:ls={0.6 * g['soften']:.2f}:lt=6")
    w = g.get("warmth", 0)
    chain.append(f"eq=brightness={g['brightness']}:contrast={g['contrast']}:saturation={g['saturation']}")
    if w:
        chain.append(f"colorbalance=rs={w:.3f}:bs={-w:.3f}:rm={w * 0.8:.3f}:bm={-w * 0.8:.3f}")
    if g.get("vignette", 0) > 0:
        chain.append(f"vignette=angle={0.2 + 0.6 * g['vignette']:.3f}")

    if c.get("effect") == "shrink":
        s = cam["shrink_scale"]
        chain += [f"scale={int(W * s) // 2 * 2}:-2",
                  f"pad={W}:{H}:(ow-iw)/2:{int(H * cam['shrink_center_y'])}-ih/2:black"]
    if "flash" in fx:  # 白光閃入
        chain.append("fade=t=in:st=0:d=0.18:color=white")
    chain += [f"fps={style['output']['fps']}", "format=yuv420p", "setsar=1", "setpts=PTS-STARTPTS"]
    return ",".join(chain)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("-o", "--out", default="out/final.mp4")
    ap.add_argument("--style", default=str(HERE.parent / "style.yaml"))
    ap.add_argument("--preview", action="store_true", help="快速低畫質預覽")
    ap.add_argument("--keep-ass", action="store_true", help="另存字幕檔 .ass 方便進剪輯軟體微調")
    args = ap.parse_args()

    style = yaml.safe_load(open(args.style, encoding="utf-8"))
    plan = json.load(open(args.plan, encoding="utf-8"))
    src = str(pathlib.Path(plan["source"]).resolve())
    fps = style["output"]["fps"]
    timeline, total = build_timeline(plan["clips"], fps)
    audio_in = has_audio(src) and not plan.get("mute_source")  # 沒講話的影片：靜音，避免把底噪放大

    apply_auto_fx(plan, style, timeline)
    sfx_events = collect_sfx(plan, style, timeline)

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="vse_"))
    (tmp / "subs.ass").write_text(make_ass(plan, style, timeline), encoding="utf-8")

    cmd, fg = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-stats"], []
    for c in timeline:
        cmd += ["-ss", f"{c['start']:.3f}", "-t", f"{c['dur']:.3f}", "-i", src]
    n = len(timeline)
    concat_in = ""
    for i, c in enumerate(timeline):
        fg.append(f"[{i}:v]{video_chain(c, style)}[v{i}]")
        if audio_in:
            fo = max(0.0, c["dur"] - 0.03)
            fg.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,"
                      f"afade=t=in:d=0.02,afade=t=out:st={fo:.3f}:d=0.03,asetpts=PTS-STARTPTS[a{i}]")
        else:
            fg.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={c['dur']:.3f}[a{i}]")
        concat_in += f"[v{i}][a{i}]"
    fg.append(f"{concat_in}concat=n={n}:v=1:a=1[cv][ca]")
    fg.append("[cv]ass=subs.ass[outv]")

    au = style["audio"]
    fg.append(f"[ca]highpass=f=70,loudnorm=I={au['loudness']}:TP=-1.5:LRA=11[vraw]")
    next_in = n
    if sfx_events:
        files = sorted({e["file"] for e in sfx_events})
        labels = []
        for f in files:
            evs = [e for e in sfx_events if e["file"] == f]
            cmd += ["-i", f]
            outs = "".join(f"[s{next_in}_{j}]" for j in range(len(evs)))
            fg.append(f"[{next_in}:a]aresample=48000,aformat=channel_layouts=stereo,asplit={len(evs)}{outs}")
            for j, e in enumerate(evs):
                ms = int(e["at"] * 1000)
                fg.append(f"[s{next_in}_{j}]volume={e['volume']:.2f},adelay={ms}|{ms}[x{next_in}_{j}]")
                labels.append(f"[x{next_in}_{j}]")
            next_in += 1
        fg.append(f"[vraw]{''.join(labels)}amix=inputs={len(labels) + 1}:duration=first:normalize=0[voice]")
    else:
        fg.append("[vraw]anull[voice]")
    bgm = plan.get("bgm") or au.get("bgm")
    if bgm:
        bi = next_in
        cmd += ["-stream_loop", "-1", "-i", str(pathlib.Path(bgm).resolve())]
        fg.append(f"[{bi}:a]aresample=48000,aformat=channel_layouts=stereo,volume={au['bgm_volume']},"
                  f"atrim=duration={total:.3f},afade=t=out:st={max(0, total - 1.5):.3f}:d=1.5[bg]")
        if au.get("bgm_duck", True):
            fg.append("[voice]asplit[vo][vk]")
            fg.append("[bg][vk]sidechaincompress=threshold=0.02:ratio=8:attack=30:release=500[bgd]")
            fg.append("[vo][bgd]amix=inputs=2:duration=first:normalize=0[outa]")
        else:
            fg.append("[voice][bg]amix=inputs=2:duration=first:normalize=0[outa]")
    else:
        fg.append("[voice]anull[outa]")

    out = pathlib.Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    (tmp / "graph.txt").write_text(";\n".join(fg), encoding="utf-8")
    enc = (["-preset", "veryfast", "-crf", "28"] if args.preview else ["-preset", "medium", "-crf", "19"])
    cmd += ["-filter_complex_script", "graph.txt", "-map", "[outv]", "-map", "[outa]",
            "-c:v", "libx264", *enc, "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", str(out)]
    try:
        subprocess.run(cmd, cwd=tmp, check=True)
        if args.keep_ass:
            shutil.copy(tmp / "subs.ass", out.with_suffix(".ass"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"✓ 完成：{out}（{total:.1f} 秒，{n} 個片段）")


if __name__ == "__main__":
    main()
