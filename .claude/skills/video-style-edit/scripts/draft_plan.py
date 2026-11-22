#!/usr/bin/env python3
"""從逐字稿自動產生「初版剪輯計畫」：刪停頓、刪贅字、切好字幕、給預設鏡頭變化。

用法:
    python draft_plan.py work/transcript.json -o work/plan.json [--style ../style.yaml]

產生的 plan.json 之後由 Claude 依風格加上：重點大字、內心 OS、疊字、特寫 / 縮小鏡頭、片頭鉤子。
所有時間都是「原始影片」的秒數；render.py 會自動換算成剪完後的時間。
"""
import argparse
import json
import pathlib
import re

import yaml

HERE = pathlib.Path(__file__).resolve().parent
PUNCT = "，。！？、；：,.!?;:…~～「」『』\"' "
BREAK_PUNCT = "，。！？；,.!?;…"


def clean(text, strip_punct):
    return re.sub(f"[{re.escape(PUNCT)}]", "", text) if strip_punct else text.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("transcript")
    ap.add_argument("-o", "--out", default="work/plan.json")
    ap.add_argument("--style", default=str(HERE.parent / "style.yaml"))
    args = ap.parse_args()

    style = yaml.safe_load(open(args.style, encoding="utf-8"))
    tr = json.load(open(args.transcript, encoding="utf-8"))
    pace, sub, cam = style["pacing"], style["subtitle"], style["camera"]
    fillers = set(pace.get("filler_words", []))
    duration = tr["duration"]

    words = [w for w in tr["words"] if clean(w["text"], True) not in fillers]
    words = [w for w in words if clean(w["text"], True)]  # 去掉純標點

    # ── 1. 依停頓切成片段 ──
    groups = []
    for w in words:
        if groups and w["start"] - groups[-1][-1]["end"] <= pace["max_pause"]:
            groups[-1].append(w)
        else:
            groups.append([w])

    clips = []
    zoom_cycle = [1.0, cam["medium_zoom"], 1.0, cam["closeup_zoom"]]
    for i, g in enumerate(groups):
        s = max(0.0, g[0]["start"] - pace["pad"])
        e = min(duration, g[-1]["end"] + pace["pad"])
        if clips and s < clips[-1]["end"]:
            s = clips[-1]["end"]
        if e - s < 0.15:
            continue
        clips.append({"start": round(s, 3), "end": round(e, 3),
                      "zoom": zoom_cycle[i % len(zoom_cycle)],
                      "text": "".join(w["text"] for w in g)})

    # ── 2. 切字幕：遇到標點、字數到上限、或停頓就換行 ──
    captions, buf = [], []

    def flush():
        if not buf:
            return
        text = clean("".join(w["text"] for w in buf), sub.get("strip_punctuation", True))
        if text:
            captions.append({"start": buf[0]["start"], "end": buf[-1]["end"], "text": text})
        buf.clear()

    for w in words:
        if buf and (w["start"] - buf[-1]["end"] > pace["max_pause"]
                    or len(clean("".join(x["text"] for x in buf) + w["text"], True)) > sub["max_chars"]):
            flush()
        buf.append(w)
        if w["text"][-1] in BREAK_PUNCT:
            flush()
    flush()

    # 字幕之間的小空隙補起來，避免閃爍
    for a, b in zip(captions, captions[1:]):
        if 0 < b["start"] - a["end"] < 0.4:
            a["end"] = b["start"]
    for c in captions:
        c["start"], c["end"] = round(c["start"], 3), round(c["end"], 3)

    plan = {
        "source": tr["source"],
        "clips": clips,
        "captions": captions,
        "emphasis": [],   # {"start","end","text","sub"?}      粉色超大重點字
        "asides": [],     # {"start","end","text"}             （括號內心 OS）
        "layered": [],    # {"start","end","text"}             金色半透明疊字
        "bgm": None,
    }
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")

    kept = sum(c["end"] - c["start"] for c in clips)
    print(f"✓ 初版計畫：{out}")
    print(f"  原片 {duration:.1f}s → 剪後約 {kept:.1f}s（{len(clips)} 段、{len(captions)} 句字幕）")


if __name__ == "__main__":
    main()
