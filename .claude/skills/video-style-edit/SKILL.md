---
name: video-style-edit
description: 把直式口播 / 自拍 / 療程 / 生活影片自動剪成使用者的風格。兩組風格可混用：「溫柔質感」（襯線明體字幕、粉色大字、括號內心 OS、金色疊字、暖色柔光）與「可愛綜藝」（圓體粗字、頂部固定標題、粉色大數字、淡黃 / 灰色 OS、問號與震驚線塗鴉、emoji）。使用時機：使用者說「幫我剪影片」「照我的風格剪」「剪成口播 / Reels / 短影音」、或丟一支影片要求自動剪輯、上字幕。
---

# 影片風格自動剪輯

流程：**轉逐字稿 → 自動粗剪 → 你（Claude）做風格判斷 → 輸出影片**。
腳本都在 `scripts/`，風格參數在 `style.yaml`（顏色、字型、字幕位置、節奏都在那裡改）。

## 先選風格（plan.json 的 `"preset"`）
| preset | 字型 / 感覺 | 適合 |
|---|---|---|
| 不填（預設） | 襯線明體、暖色柔光、質感 | 美容療程、保養、療癒、品牌、知識分享 |
| `"cute"` | 源泉圓體粗、明亮、綜藝感 | 聊天、閨蜜對話、遊戲挑戰、生活搞笑、開箱 |

**所有元素在兩個 preset 都能用**，依內容靈活混搭：例如質感片也可以放一個問號塗鴉，綜藝片也能用縮小黑底。
使用者沒指定時，依影片內容自己判斷，並在摘要裡說明選了哪個、為什麼。

## 使用者已確認的偏好
- **不要畫面震動特效。**
- 合成音效聽起來太假，先不用（`sfx.enabled: false`）；要音效請使用者提供真實音效檔。
- 熱門音樂交給 IG / 抖音內建音樂庫。
- 原片已經燒進去的字幕：用放大裁切（zoom ≥ 1.25、focus_y 0）裁掉底部字幕，畫面中間有字的段落用 `video_from` 換成乾淨畫面。

## 取得影片
- 使用者會給 **Google 雲端硬碟分享連結**（手機 / 平板傳不了大檔）。下載：
  `curl -L -o work/src/video.mov "https://drive.usercontent.google.com/download?id=<檔案ID>&export=download&confirm=t"`
- 資料夾連結需請使用者給個別檔案連結，或改用 WeTransfer。
- 先抽格看畫面（`ffmpeg -vf "fps=1,scale=192:-2,tile=10x2"`），確認是不是原始素材、有沒有燒進去的字。

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

### 3-7 音效與畫面特效
- 音效在 `sfx/`（`scripts/make_sfx.py` 合成，無版權）：pop、whoosh、swoosh_up、ding、boom、sparkle、tick、bubble。
- `style.yaml` 的 `sfx.auto` 會自動配：開場 swoosh_up、重點大字 pop、內心 OS ding、疊字 sparkle、縮小黑底 boom、特寫切換 whoosh。
- 想在特定時間點多加：`"sfx": [{"at": 原片秒數, "name": "bubble", "volume": 1}]`；整支不要音效：`"sfx": false`。
- 畫面特效：**不要用畫面震動**（使用者不喜歡）；縮小黑底自動白光閃入；其他片段可手動加 `"fx": ["flash"]`。
- 搞笑 / 可愛的內容多用 bubble、pop；嚴肅轉折用 boom。不要每一刀都放音效，會很吵。

### 3-8 背景音樂
- **熱門歌曲有版權，不要自己抓。** 建議使用者上傳 IG / 抖音時用平台內建音樂庫（有授權，也能吃到熱門音樂的流量）。
- 使用者有提供免版權音樂才加：`"bgm": "music/xxx.mp3"`（說話時會自動壓低）。
- 沒有講話的影片：設 `"mute_source": true`，避免把底噪放大。

### 3-9 綜藝元素（任何 preset 都能用）
- **頂部固定標題** `title`：整支片的主題，例「他是一個滿分男」「當你姐妹顛覆你的想像」。≤ 10 字，通常 start 0 到片尾。
- **旁白樣式** `asides` 加 `"look"`：
  - `cream` 淡黃括號：情緒反應（「（笑容逐漸消失）」「（尷尬）」）
  - `gray` 灰色括號：吐槽說明（「（非靜止畫面）」「（沉默三秒）」）
  - `star` 白色星號：動作描述（「*眼睛開始發亮」「*默默拿出手機」）
  - `pink` 粉紅白邊：質感風的內心 OS
  - 都可以加 `"x"`、`"y"`（0–1）放在臉旁邊，`"tilt"` 歪斜。
- **重點大字**可以是數字或金額（「30萬」「300萬」）；`sub` 可放 emoji，例 `"(😍?)"`。
- **塗鴉** `doodles`：`{"start","end","type","x","y","scale"}`
  - `question` 大問號（疑惑）、`exclaim` 驚嘆號、`shock` 震驚放射線（放在臉旁，嚇到 / 震驚）、
    `squiggle` 扭扭線（尷尬 / 無言）、`heart` 愛心、`sparkle` 星光（眼睛發亮、心動）
- **emoji 貼圖** `emoji`：`{"start","end","emoji":"🤣","x","y","size"}`；字卡文字裡也可以直接打 emoji。
- 節制：同一時間畫面上最多 1 個塗鴉 + 1 個 emoji；不要遮住臉。

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
