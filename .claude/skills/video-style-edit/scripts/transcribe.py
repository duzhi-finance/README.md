#!/usr/bin/env python3
"""把影片轉成帶「逐字時間戳記」的繁體中文逐字稿。

用法:
    python transcribe.py input.mp4 -o work/transcript.json [--model medium]

輸出 JSON:
    {"source": "...", "duration": 63.2,
     "words": [{"start": 0.31, "end": 0.52, "text": "這"}, ...],
     "segments": [{"start": ..., "end": ..., "text": "..."}]}
"""
import argparse
import json
import pathlib
import subprocess


def to_traditional(text):
    try:
        import opencc  # opencc-python-reimplemented
        return opencc.OpenCC("s2twp").convert(text)
    except ImportError:
        return text


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("-o", "--out", default="work/transcript.json")
    ap.add_argument("--model", default="medium",
                    help="tiny / base / small / medium / large-v3（越大越準越慢）")
    ap.add_argument("--device", default="auto")
    args = ap.parse_args()

    from faster_whisper import WhisperModel

    model = WhisperModel(args.model, device=args.device, compute_type="auto")
    segments, _info = model.transcribe(
        args.video,
        language="zh",
        word_timestamps=True,
        vad_filter=True,
        initial_prompt="以下是繁體中文的口語分享，請加上標點符號。",
    )

    words, segs = [], []
    for seg in segments:
        segs.append({"start": round(seg.start, 3), "end": round(seg.end, 3),
                     "text": to_traditional(seg.text.strip())})
        for w in seg.words or []:
            t = to_traditional(w.word.strip())
            if t:
                words.append({"start": round(w.start, 3), "end": round(w.end, 3), "text": t})

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "source": str(pathlib.Path(args.video).resolve()),
        "duration": probe_duration(args.video),
        "words": words,
        "segments": segs,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✓ 逐字稿：{out}（{len(segs)} 句、{len(words)} 個詞）")


if __name__ == "__main__":
    main()
