---
name: video-style-edit
description: 把直式口播 / 自拍分享影片，自動剪成「溫柔質感口播」風格（襯線明體字幕、粉色超大重點字、括號內心 OS、半透明金色疊字、特寫與縮小黑底鏡頭變化、暖色柔光）。使用時機：使用者說「幫我剪影片」「照我的風格剪」「剪成口播 / Reels / 短影音」、或丟一支影片要求自動剪輯、上字幕。
---

# 溫柔質感口播 —— 自動剪輯

流程：**轉逐字稿 → 自動粗剪 → 你（Claude）做風格判斷 → 輸出影片**。
腳本都在 `scripts/`，風格參數在 `style.yaml`（顏色、字型、字幕位置、節奏都在那裡改）。

## 0. 環境準備（第一次）

```bash
pip install -r .claude/skills/video-style-edit/requirements.txt
# 另外需要 ffmpeg（含 libass）以及繁中襯線字型：
#   Linux: apt-get install fonts-noto-cjk fonts-noto-cjk-extra
#   Mac:   brew install ffmpeg ；字型可在 style.yaml 改成 "Songti TC"
```

Whisper 第一次會從 huggingface.co 下載模型。若網路被擋，請使用者在自己的電腦跑
`transcribe.py`，把 `transcript.json` 傳回來，或請他開放 huggingface.co。

## 1. 轉逐字稿

```bash
S=.claude/skills/video-style-edit/scripts
python $S/transcribe.py <影片>.mp4 -o work/transcript.json --model medium
```

## 2. 自動粗剪（刪停頓、刪贅字、切字幕）

```bash
python $S/draft_plan.py work/transcript.json -o work/plan.json
```

## 3. 風格判斷（這一步是你的工作）

讀 `work/transcript.json` 和 `work/plan.json`，依下面的規則**直接修改 plan.json**。
時間一律用**原始影片的秒數**，render 會自己換算。

### 3-1 內容整理
- **NG / 講錯重來**：同一句講了兩次，只保留最後、最順的那次（刪掉對應的 clip，或調整 start/end）。
- **錯字**：修正 Whisper 聽錯的字（尤其是品牌名、專有名詞），問使用者不確定的字。
- **片頭鉤子**：找出最有衝突感 / 最引起共鳴的一句（例如「曾經長達三年都沒根治」），
  把那個 clip **複製一份放到 clips 最前面**，前 3 秒就要抓住人。
- 總長度目標：短影音 30–60 秒。太長就刪掉重複的解釋。

### 3-2 字幕（captions）
- 白色襯線字，每行 ≤ 10 字，**依語意斷句**，不要把詞切開（「婦科 / 發炎」不可切成「婦 / 科發炎」）。
- 不放標點；只有收尾的句子可以保留「。」。

### 3-3 重點大字（emphasis）—— 這個風格的靈魂
- 每 5–8 秒最多 1 個，整支片約 4–8 個。
- 選 **2–4 個字的情緒詞或動作詞**：例「滑走」「復發過」「根治」「超痛」「三年」。
- 時間對準「說出那個詞」的瞬間，持續 0.6–1.2 秒。這段時間一般字幕會自動暫停。
- 可加 `"sub": "（抗戰成功）"` 這種幽默小註解在大字下方。

### 3-4 括號內心 OS（asides）
- 自嘲、吐槽、補充身分的小旁白，例「（婦產科VIP本人）」「（真的很煩）」「（不是業配）」。
- 整支片 2–4 個，**不要**跟重點大字同時出現。文字要自己寫，口吻俏皮、短（≤ 10 字）。

### 3-5 金色疊字（layered）
- 用在「核心承諾 / 結論」那一句，例「可以根治」「終於好了」。整支片 1–2 次。
- 和一般字幕同時出現（疊在字幕後面），時間對齊那句話。

### 3-6 鏡頭變化（clips 裡的欄位）
- `zoom`：1.0 = 原始、1.15 = 中景、1.45 = 特寫。相鄰片段要有變化，製造跳剪節奏。
- 講到**重點大字**時，那一段用特寫（1.4–1.5）。
- `"zoom_to": 1.2`：情緒鋪陳時慢慢推近。
- `"effect": "shrink"`：縮小畫面 + 黑底，用在「轉折」或「講到很嚴肅 / 很慘」的句子，整支片 1–2 次。
- 臉的位置偏高或偏低時，可加 `"focus_y": 0.35` 調整放大的中心。
- 片段可以切細：一個長 clip 可以拆成兩個（時間接續），各自給不同 zoom。

### 3-7 背景音樂
使用者有提供音樂才加：`"bgm": "music/xxx.mp3"`（說話時會自動壓低）。

## 4. 輸出

```bash
python $S/render.py work/plan.json -o out/preview.mp4 --preview   # 快速預覽
python $S/render.py work/plan.json -o out/final.mp4 --keep-ass    # 正式輸出 + 字幕檔
```

輸出後抽幾張畫面檢查（字幕有沒有被切掉、大字位置、特寫有沒有切到頭）：

```bash
for t in 1 5 10 20; do ffmpeg -y -loglevel error -ss $t -i out/final.mp4 -frames:v 1 -vf scale=540:-2 out/check_$t.png; done
```

把成品和一份簡短的剪輯摘要（刪了什麼、鉤子用哪句、重點字有哪些）交給使用者，
問他哪裡想調整；風格上的固定偏好要回寫到 `style.yaml` 或本檔案的規則裡。

## 注意
- 影片檔不要 commit 進 git（`work/`、`out/` 已列入 .gitignore）。
- 產品功效相關的字卡（例如「根治」）只照使用者原話放，不要自己誇大。
