#!/usr/bin/env python3
"""合成一組短影音常用音效（全部由程式產生，無版權問題）。

用法:  python make_sfx.py [-o ../sfx]
產生: pop / whoosh / ding / boom / sparkle / swoosh_up / tick / bubble
"""
import argparse
import pathlib
import wave

import numpy as np

SR = 48000
HERE = pathlib.Path(__file__).resolve().parent


def t(d):
    return np.arange(int(SR * d)) / SR


def env(x, attack=0.005, decay=0.2):
    n = len(x)
    a = np.minimum(1, np.arange(n) / max(1, SR * attack))
    d = np.exp(-np.arange(n) / (SR * decay))
    return x * a * d


def sweep(f0, f1, d):
    f = np.geomspace(f0, f1, len(t(d)))
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def bandnoise(d, lo, hi, lo2=None, hi2=None):
    """帶通雜訊，頻帶可隨時間移動（做咻聲用）。"""
    n = int(SR * d)
    out = np.zeros(n)
    rng = np.random.default_rng(7)
    block = 1024
    lo2, hi2 = lo2 or lo, hi2 or hi
    for i in range(0, n, block):
        k = i / n
        l, h = lo + (lo2 - lo) * k, hi + (hi2 - hi) * k
        spec = np.fft.rfft(rng.standard_normal(block * 2))
        fr = np.fft.rfftfreq(block * 2, 1 / SR)
        spec[(fr < l) | (fr > h)] = 0
        out[i:i + block] = np.fft.irfft(spec)[:min(block, n - i)]
    return out / (np.abs(out).max() + 1e-9)


def sounds():
    s = {}
    # 啵：重點大字跳出
    s["pop"] = env(sweep(900, 260, 0.12), 0.002, 0.04) + 0.3 * env(bandnoise(0.12, 2000, 6000), 0.001, 0.01)
    # 咻：鏡頭切換 / 轉場
    d = 0.45
    w = bandnoise(d, 300, 1500, 1500, 6000)
    s["whoosh"] = w * np.sin(np.pi * np.linspace(0, 1, len(w))) ** 2
    # 上揚咻：開場
    w = bandnoise(0.6, 200, 800, 2500, 9000)
    s["swoosh_up"] = w * np.linspace(0, 1, len(w)) ** 2 * np.exp(-np.maximum(0, np.linspace(-3, 1, len(w))) * 6)
    # 叮：內心 OS / 小提示
    x = t(1.2)
    s["ding"] = env(sum(a * np.sin(2 * np.pi * 1320 * m * x) for m, a in [(1, 1), (2.76, .4), (5.4, .2)]), 0.002, 0.35)
    # 咚：縮小黑底、嚴肅轉折
    x = t(0.9)
    s["boom"] = env(sweep(110, 38, 0.9), 0.003, 0.3) + 0.25 * env(bandnoise(0.9, 40, 300), 0.002, 0.08)
    # 閃亮：金色疊字
    x = t(1.0)
    sp = np.zeros_like(x)
    for i, f in enumerate([2093, 2637, 3136, 4186, 3520]):
        st = int(i * 0.07 * SR)
        seg = env(np.sin(2 * np.pi * f * t(1.0 - i * 0.07)), 0.002, 0.18)
        sp[st:st + len(seg)] += seg[:len(sp) - st] * 0.5
    s["sparkle"] = sp
    # 滴答：字卡一個一個跳
    s["tick"] = env(bandnoise(0.05, 2500, 7000), 0.0005, 0.008)
    # 泡泡：可愛 / 搞笑
    s["bubble"] = env(sweep(300, 1400, 0.15), 0.003, 0.06)
    return s


def write(path, x, peak=0.85):
    x = x / (np.abs(x).max() + 1e-9) * peak
    fade = int(0.005 * SR)
    x[-fade:] *= np.linspace(1, 0, fade)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((x * 32767).astype("<i2").tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default=str(HERE.parent / "sfx"))
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, x in sounds().items():
        write(out / f"{name}.wav", x)
        print("✓", out / f"{name}.wav")


if __name__ == "__main__":
    main()
