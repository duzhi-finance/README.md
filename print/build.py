#!/usr/bin/env python3
"""Build the A4 print version of the Guang Mei menu (print/a4.html)."""
from pathlib import Path

H = Path(__file__).parent
QR = (H / "line-qr.svg").read_text(encoding="utf-8").split("?>", 1)[1]

FZ = 1.06
BASE3 = ["薰衣草熱蒸喚醒肌膚", "韓式雙效水循環小氣泡", "手清粉刺毛孔潔淨"]

FACE = [
    dict(name="韓式雙效水循環", time="80 分鐘", was="$2,000", now="$1,800",
         effect=["深層清潔", "毛孔淨化", "補水保濕"],
         steps=BASE3 + ["安瓶精華導入", "積雪草修護凍膜", "光療・最後一道屏障鎖水修復程序"],
         desc="第一次做臉推薦從這堂開始。",
         fit="第一次做臉的人｜毛孔、粉刺困擾｜想定期清潔保濕的人"),
    dict(name="外泌體養膚", photo=["photos/exo.jpg"], badge="冬日活動", time="90 分鐘", was="$3,900", now="$2,500",
         effect=["水潤保濕", "提亮光澤", "穩定修護"],
         steps=BASE3 + ["奈米微創水光導入", "積雪草舒緩修復面膜", "光療・最後一道屏障鎖水修復程序"],
         desc="一次完成清潔＋修復＋水光感打造！",
         fit="所有膚質｜改善暗沉、蠟黃、痘痘｜幫助雷射術後修護｜敏弱肌重建肌膚屏障"),
    dict(name="24K 黃金撥筋", time="120 分鐘", was="$4,280", now="$3,800",
         effect=["緊緻拉提", "透亮光澤", "放鬆臉部線條"],
         steps=BASE3 + ["24K 緊緻安瓶微針", "24K 金箔", "黃金面霜撥筋按摩", "EMS 導入", "黃金軟膜"],
         desc="使用 24K 純金金箔能量護理，搭配黃金面霜撥筋循環，緊緻拉提，打造透亮細緻發光肌。",
         fit="乾燥、暗沉、疲憊肌｜想要抗老緊緻的人"),
    dict(name="木乃伊緊緻術", photo=["photos/mummy.jpg"], time="120 分鐘", was="$4,280", now="$3,800",
         effect=["緊緻塑顏", "毛孔細緻", "輪廓拉提"],
         steps=BASE3 + ["緊緻安瓶微針", "木乃伊緊緻包覆術", "客製化保養導入"],
         desc="輪廓上提，氣質自然提升。",
         fit="毛孔明顯者｜臉部線條鬆弛｜雙頰下垂感｜想打造小 V 臉輪廓者"),
    dict(name="藻針亮膚", photo=[("duo", "photos/zao.jpg")], badge="冬日活動", time="120 分鐘", was="$3,880", now="$2,500",
         effect=["毛孔細緻", "控油清爽", "膚觸細滑"],
         steps=BASE3 + ["矽藻針換膚", "微電 PDRN 導入", "積雪草凍膜＋照光"],
         desc="",
         fit="毛孔粗大、膚觸粗糙｜油光、粉刺困擾｜想讓肌膚細緻透亮的人"),
    dict(name="酸類亮澤課程", photo=["photos/acid.jpg"], badge="冬日活動", time="90 分鐘", was="$3,600", now="$2,500",
         effect=["粉刺清潔", "亮澤膚色", "代謝老化角質"],
         steps=BASE3 + ["液態皮秒（杏仁酸或水楊酸）", "舒緩按摩", "客製化軟膜"],
         desc="針對黑頭粉刺、痘痘，有效改善膚色暗沉，代謝老化角質。",
         fit="黑頭粉刺、痘痘肌｜膚色暗沉｜角質堆積、膚觸粗糙"),
    dict(name="淨透水光肌", badge="冬日活動", time="90 分鐘", was="$3,200", now="$2,500",
         effect=["深層淨透", "多層補水", "水光感"],
         steps=BASE3 + ["超聲波剷皮", "微針玻尿酸安瓶", "微電導入", "客製化軟膜"],
         desc="韓式肌膚管理",
         fit="缺水乾燥肌｜毛孔、粉刺困擾｜想要水潤光澤感的人"),
    dict(name="潤泥秀種鑽", photo=["photos/zuan.jpg"], time="60 分鐘", was="", now="$4,398",
         effect=["透亮光澤", "保濕滋潤", "細緻膚觸"],
         steps=["深層潔顏・洗去臉部髒污與油光", "溫和去角質・讓肌膚更好吸收保養", "舒緩凍膜・鎮靜補水",
                "潤泥種鑽粉・細緻鋪於肌膚", "種鑽專屬精華・專業手法按壓導入", "專屬修護面霜・薄敷鎖水防護"],
         desc="以潤泥種鑽粉搭配專屬精華與按壓手法，讓保養更好吸收，肌膚透出細緻光澤。",
         fit="乾燥暗沉肌｜想讓肌膚透亮有光澤｜重要場合前想加強保養的人"),
]


def Z(z, inner):
    return f'<div class="z" style="zoom:{z}">{inner}</div>'


def foot(dark=False):
    return f'''<div class="foot{' dk' if dark else ''}"><div class="fl"><b>光美</b><span>GUĀNG MĚI</span></div>
<div class="fm">台北市大安區忠孝東路四段223巷40號<br>捷運忠孝敦化站 2 號出口・全預約制<br>Instagram @guangmeitaiwan</div>
<div class="fq"><div class="qr">{QR}</div><span>LINE 預約</span></div></div>'''


def photos(c):
    if not c.get("photo"):
        return ""
    parts = []
    for ph in c["photo"]:
        if isinstance(ph, tuple) and ph[0] == "duo":
            parts.append(f'<figure class="duo"><img src="{ph[1]}" alt=""><span class="l">BEFORE</span><span class="r">AFTER</span></figure>')
        elif isinstance(ph, tuple):
            parts.append(f'''<div class="pair"><figure><img src="{ph[0]}" alt=""><figcaption>BEFORE</figcaption></figure>
<figure><img src="{ph[1]}" alt=""><figcaption>AFTER</figcaption></figure></div>''')
        else:
            parts.append(f'<img class="one" src="{ph}" alt="">')
    return f'<div class="ba">{"".join(parts)}</div>'


def course(c):
    badge = f'<span class="badge">{c["badge"]}</span>' if c.get("badge") else ""
    was = f'<s>{c["was"]}</s>' if c["was"] else ""
    steps = "".join(f"<li>{s}</li>" for s in c["steps"])
    eff = "".join(f"<i>{e}</i>" for e in c["effect"])
    desc = f'<p class="ds">{c["desc"]}</p>' if c["desc"] else ""
    return f'''<div class="course">
 <div class="ch"><h3>{c["name"]}{badge}</h3><span class="tm">{c["time"]}</span><span class="pr">{was}<b>{c["now"]}</b></span></div>
 <div class="cb">
  {photos(c)}
  <div class="info">
   <div class="lab">功效</div><div class="eff">{eff}</div>
   <div class="lab">課程內容</div><ol class="st">{steps}</ol>
   {desc}
   <p class="fit"><b>適合</b>{c["fit"]}</p>
  </div>
 </div>
</div>'''


def face_pages():
    out = []
    for i in range(0, len(FACE), 2):
        head = ('''<div class="eyebrow">Course Menu</div><h2 class="h2">課程價目表・臉部保養</h2>
<p class="lead">每一堂課都會先看看你的狀況，再一起決定怎麼做。　<s class="lg">原價</s> <span class="lg2">體驗價</span></p>'''
                if i == 0 else '<div class="eyebrow">Facial Care</div><h2 class="h2">臉部保養</h2>')
        out.append(f'''<section class="page"><div class="in">{Z(FZ, head + "".join(course(c) for c in FACE[i:i+2]))}
<p class="disc">＊對比照為實際顧客護理前後紀錄，經本人同意使用；效果因個人膚況而異。</p>
</div>{foot()}</section>''')
    return "".join(out)


CSS = r"""
@page{size:A4;margin:0}
:root{--paper:#F6F0E9;--paper2:#EFE5DA;--ink:#2B211C;--soft:#6E5B4E;--rose:#A97862;--deep:#8C5A48;--champ:#C9AE8E;--line:#E2D4C5;--dark:#1E1A17}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#ccc}
body{font-family:'Noto Serif TC',serif;color:var(--ink);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{position:relative;width:210mm;height:297mm;overflow:hidden;background:var(--paper);margin:0 auto 10mm;page-break-after:always;break-after:page}
@media print{html,body{background:none}.page{margin:0}}
.in{position:absolute;left:16mm;right:16mm;top:15mm;bottom:35mm}
.lat{font-family:'Cormorant Garamond',serif}
.eyebrow{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:15pt;color:var(--rose)}
.h2{font-size:25pt;font-weight:700;letter-spacing:3pt;margin:1mm 0 2mm}
.lead{font-size:10pt;color:var(--soft);letter-spacing:.6pt;line-height:1.8}
.lg{color:#B9A797}.lg2{color:var(--rose)}
img{display:block}
/* footer */
.foot{position:absolute;left:16mm;right:16mm;bottom:8mm;height:23mm;display:flex;align-items:center;gap:6mm;border-top:.3mm solid var(--line);padding-top:3mm}
.fl{display:flex;align-items:baseline;gap:2mm}.fl b{font-size:17pt;letter-spacing:3pt}.fl span{font-family:'Cormorant Garamond',serif;font-size:13pt;letter-spacing:2pt}
.fm{flex:1;text-align:left;font-size:10pt;color:var(--soft);line-height:1.7;letter-spacing:.4pt}
.fq{display:flex;align-items:center;gap:2mm;font-size:10pt;letter-spacing:1pt;color:var(--soft)}
.qr{width:19mm;height:19mm;background:#fff;padding:.8mm;border-radius:1mm}.qr svg{width:100%;height:100%;display:block}
.foot.dk{border-top-color:rgba(255,255,255,.35)}
.zs .in>*{zoom:1.25}.zb .in>*{zoom:1.12}
/* winter */
.winter{background:radial-gradient(120% 60% at 50% 0%,#F1DED2 0%,#F6F0E9 70%);text-align:center}
.winter .eyebrow{font-size:20pt;margin-top:8mm}
.winter h1{font-size:46pt;font-weight:900;letter-spacing:8pt;margin:3mm 0 1mm}
.winter .date{font-family:'Cormorant Garamond',serif;font-size:15pt;letter-spacing:4pt;color:var(--soft)}
.rule{display:flex;align-items:center;gap:3mm;margin:7mm 0}.rule i{flex:1;height:.3mm;background:var(--line)}.rule b{width:2mm;height:2mm;background:var(--champ);transform:rotate(45deg)}
.winter .sub{font-size:13pt;letter-spacing:2pt;color:var(--soft)}
.price{display:flex;justify-content:center;align-items:center;gap:5mm;margin:6mm 0 4mm}
.price .lab{font-size:12pt;letter-spacing:2pt;color:var(--rose);border:.35mm solid var(--rose);border-radius:10mm;padding:1.5mm 5mm}
.price .num{font-family:'Cormorant Garamond',serif;font-size:72pt;font-weight:500;color:var(--rose);line-height:1}
.price .num small{font-size:30pt;vertical-align:30pt;margin-right:1mm}
.wl{list-style:none;text-align:left;border-top:.3mm solid var(--line);margin-top:4mm}
.wl li{display:flex;align-items:center;gap:6mm;padding:4.3mm 3mm;border-bottom:.3mm solid var(--line)}
.wl .n{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:20pt;color:var(--champ);width:10mm}
.wl .t{flex:1}.wl .t b{display:block;font-size:15pt;letter-spacing:1.5pt}.wl .t span{font-size:10pt;color:var(--soft);letter-spacing:1pt}
.wl s{font-family:'Cormorant Garamond',serif;font-size:15pt;color:var(--champ)}
.cta{display:inline-block;margin-top:8mm;font-size:12pt;letter-spacing:2pt;background:var(--ink);color:var(--paper);border-radius:10mm;padding:3mm 9mm}
/* gift */
.gift .bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:30% 45%;filter:blur(2px)}
.gift .veil{position:absolute;inset:0;background:linear-gradient(180deg,rgba(248,239,231,.78),rgba(246,233,223,.5) 55%,rgba(248,239,231,.85))}
.gift .in{top:28mm}
.gift .eyebrow{font-size:22pt}
.gift h1{font-size:54pt;font-weight:700;letter-spacing:12pt;margin:3mm 0 4mm}
.gift .sub{font-size:14pt;letter-spacing:2.5pt;color:var(--soft);margin-bottom:10mm}
.glass{background:rgba(255,255,255,.5);border:.4mm solid rgba(255,255,255,.9);border-radius:6mm;box-shadow:0 3mm 8mm rgba(120,90,70,.12)}
.gstep{display:flex;gap:8mm;align-items:center;padding:8mm 9mm;border-top:.3mm solid rgba(255,255,255,.8)}.gstep:first-child{border-top:none}
.gstep .n{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:26pt;color:var(--rose);width:12mm}
.gstep b{display:block;font-size:17pt;letter-spacing:1.5pt;font-weight:600}.gstep span{font-size:11.5pt;color:var(--soft);letter-spacing:1pt}
.gift .brandline{margin-top:10mm;font-size:13pt;line-height:2;letter-spacing:1pt}.gift .brandline i{font-family:'Cormorant Garamond',serif;color:var(--rose);font-size:17pt}
.small{font-size:9pt;color:var(--soft);letter-spacing:.6pt;line-height:1.8;margin-top:6mm}
/* top3 */
.tc{display:flex;gap:6mm;background:#fff;border-radius:5mm;overflow:hidden;box-shadow:0 2mm 6mm rgba(120,90,70,.08);margin-top:6mm}
.tc img{width:44mm;height:auto;object-fit:cover;flex:none}
.tc .b{padding:5mm 6mm 5mm 0;flex:1}
.tc .rk{font-family:'Cormorant Garamond',serif;font-size:10pt;letter-spacing:3pt;color:var(--rose)}
.tc h3{font-size:15pt;letter-spacing:1.5pt;margin:.5mm 0}
.tc .p{font-family:'Cormorant Garamond',serif;font-size:20pt;font-weight:600;color:var(--rose);line-height:1.1}
.tc .tg{font-size:9pt;color:var(--soft);letter-spacing:.8pt;margin:.5mm 0 2mm}
.tc .fh{font-family:'Cormorant Garamond',serif;font-size:9pt;letter-spacing:2pt;color:var(--rose);border-top:.3mm dashed var(--line);padding-top:2mm}
.tc ol{list-style:none;counter-reset:s;columns:2;column-gap:5mm;margin-top:1mm}
.tc li{counter-increment:s;font-size:9.3pt;letter-spacing:.5pt;line-height:1.75;break-inside:avoid}
.tc li:before{content:counter(s);display:inline-flex;width:3.6mm;height:3.6mm;border-radius:50%;background:var(--champ);color:#fff;font-size:6.5pt;align-items:center;justify-content:center;margin-right:1.6mm;vertical-align:.3mm;font-family:'Cormorant Garamond',serif}
/* facial course */
.course{margin-top:6mm;padding-top:5mm;border-top:.5mm solid var(--ink)}
.course+.course{border-top:.3mm solid var(--line)}
.ch{display:flex;align-items:baseline;gap:4mm}
.ch h3{font-size:17pt;letter-spacing:1.5pt;flex:1}
.badge{display:inline-block;font-size:8pt;font-weight:400;letter-spacing:1pt;padding:.6mm 2.5mm;border-radius:5mm;background:#F1DED2;color:var(--rose);margin-left:2.5mm;vertical-align:1.2mm}
.tm{font-size:10pt;color:var(--soft);letter-spacing:1pt}
.pr s{font-family:'Cormorant Garamond',serif;font-size:12pt;color:#B9A797;margin-right:2mm}
.pr b{font-family:'Cormorant Garamond',serif;font-size:20pt;font-weight:600;color:var(--rose)}
.cb{display:flex;gap:6mm;margin-top:3.5mm;align-items:center}
.ba{display:flex;gap:2.5mm;flex:none;width:76mm;justify-content:center;align-items:center}
.ba img.one{display:block;max-width:76mm;max-height:64mm;width:auto;height:auto;border-radius:3mm}
.duo{position:relative;width:76mm;border-radius:3mm;overflow:hidden}
.duo img{display:block;width:100%}
.duo span{position:absolute;bottom:2.5mm;font-family:'Cormorant Garamond',serif;font-size:9pt;letter-spacing:2.5pt;color:#fff;background:rgba(43,33,28,.5);padding:.6mm 2.6mm;border-radius:5mm}
.duo .l{left:2.5mm}.duo .r{left:calc(50% + 2.5mm)}
.pair{display:flex;flex-direction:column;gap:2.5mm}
.pair figure{position:relative;width:27mm;height:30.75mm;border-radius:3mm;overflow:hidden}
.pair img{width:100%;height:100%;object-fit:cover;object-position:50% 35%}
.pair figcaption{position:absolute;left:0;right:0;bottom:0;text-align:center;font-family:'Cormorant Garamond',serif;font-size:8pt;letter-spacing:2pt;color:#fff;background:rgba(43,33,28,.45);padding:.5mm 0}
.ph{width:36mm;height:46mm;border:.35mm dashed var(--champ);border-radius:3mm;background:#FBF7F3;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1mm}
.ph em{font-style:normal;font-family:'Cormorant Garamond',serif;font-size:11pt;letter-spacing:2.5pt;color:var(--rose)}
.ph span{font-size:7.5pt;color:#B9A797;letter-spacing:.8pt}
.info{flex:1;min-width:0}
.lab{font-size:8.5pt;letter-spacing:2pt;color:var(--rose);margin:0 0 1.2mm}
.eff{display:flex;flex-wrap:wrap;gap:1.6mm;margin-bottom:2.6mm}
.eff i{font-style:normal;font-size:9.5pt;letter-spacing:1pt;font-weight:600;background:#F1DED2;color:var(--deep);border-radius:5mm;padding:.8mm 3mm}
.st{list-style:none;counter-reset:s}
.st li{counter-increment:s;font-size:9.3pt;line-height:1.7;letter-spacing:.4pt;display:flex;gap:1.8mm}
.st li:before{content:counter(s);flex:none;width:3.6mm;height:3.6mm;margin-top:1mm;border-radius:50%;background:#F1DED2;color:var(--rose);font-size:6.5pt;display:flex;align-items:center;justify-content:center;font-family:'Cormorant Garamond',serif}
.ds{font-size:9pt;color:var(--soft);line-height:1.7;letter-spacing:.4pt;margin-top:1.6mm}
.fit{font-size:9pt;color:var(--soft);line-height:1.7;letter-spacing:.4pt;margin-top:1.2mm}
.fit b{color:var(--rose);margin-right:2mm}
.disc{position:absolute;bottom:0;left:0;right:0;font-size:7.5pt;color:#9b8a7d;letter-spacing:.4pt}
/* scalp */
.item{padding:4mm 0;border-bottom:.3mm solid var(--line)}
.plan{margin-top:6mm;border-radius:6mm;padding:8mm 9mm;background:linear-gradient(135deg,#F5EBE3 0%,#EFDFD3 100%)}
.plan .pl{font-size:13pt;letter-spacing:3pt}
.plan .pb{font-family:'Cormorant Garamond',serif;font-size:66pt;font-weight:500;line-height:1;color:var(--deep)}
.plan .pb small{font-size:24pt;vertical-align:30pt;margin-right:1mm}
.plan .pt{font-size:13pt;letter-spacing:2pt;margin-top:1mm}
.plan hr{border:none;width:14mm;height:.5mm;background:var(--ink);margin:5mm 0 4mm}
.plan .cols{display:flex;gap:10mm}
.plan .cols>div{flex:1}
.note{font-size:9.5pt;line-height:1.9;letter-spacing:.6pt;color:var(--soft)}
/* menu list (body etc.) */
.cat{margin-top:7mm}
.cat-h{display:flex;align-items:baseline;justify-content:space-between;border-bottom:.5mm solid var(--ink);padding-bottom:2mm}
.cat-h h3{font-size:16pt;letter-spacing:3pt}.cat-h span{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:14pt;color:var(--soft)}
.it{padding:4mm 0;border-bottom:.3mm solid var(--line)}
.it .r1{display:flex;align-items:baseline;gap:3mm}.it .nm{flex:1;font-size:13pt;font-weight:600;letter-spacing:1pt}
.it .d{font-size:9.5pt;color:var(--soft);line-height:1.8;letter-spacing:.5pt;margin-top:1mm}
.it .pz{text-align:right;margin-top:.5mm}
.it .pz s{font-family:'Cormorant Garamond',serif;font-size:12pt;color:#B9A797;margin-right:2mm}
.it .pz b{font-family:'Cormorant Garamond',serif;font-size:18pt;font-weight:600;color:var(--rose)}
.it .pz em{font-style:normal;font-size:9.5pt;color:var(--soft);letter-spacing:1pt}
.nego{display:inline-block;font-size:9pt;letter-spacing:1pt;color:#fff;background:var(--rose);padding:.8mm 3mm;border-radius:5mm;margin-left:2mm;vertical-align:1mm}
/* rent */
.rent{background:radial-gradient(120% 60% at 50% 100%,#F1DED2 0%,#F6F0E9 70%)}
.rent .pic{position:relative;margin-top:5mm;border-radius:5mm;overflow:hidden;width:118mm}
.rent .pic img{width:100%}
.rent .pic span{position:absolute;left:3mm;top:3mm;font-size:8pt;background:#fffd;padding:.8mm 3mm;border-radius:5mm;letter-spacing:1pt}
.rent .row{display:flex;gap:7mm;align-items:flex-start}
.rent ul{list-style:none;margin-top:6mm;flex:1}
.rent li{font-size:11pt;letter-spacing:1pt;padding:3mm 0;display:flex;gap:3mm;align-items:center;border-bottom:.3mm solid var(--line)}
.rent li:before{content:"";width:2mm;height:2mm;border:.35mm solid var(--rose);transform:rotate(45deg);flex:none}
.rent .rp{display:flex;align-items:baseline;gap:2.5mm;margin-top:7mm}
.rent .rp b{font-family:'Cormorant Garamond',serif;font-size:32pt;font-weight:600}
"""


def html():
    winter_items = [("外泌體養膚", "保濕・提亮・穩定", "$3,900"), ("木乃伊緊緻術", "緊緻・輪廓・拉提", "$4,280"),
                    ("藻針亮膚", "毛孔・油光・清爽", "$3,880"), ("酸類亮澤課程", "粉刺・暗沉", "$3,600"),
                    ("淨透水光肌", "清潔・水潤", "$3,200")]
    wl = "".join(f'<li><span class="n">0{i+1}</span><span class="t"><b>{a}</b><span>{b}</span></span><s>{c}</s></li>'
                 for i, (a, b, c) in enumerate(winter_items))
    tops = [
        ("../img/top1.jpg", "TOP 01", "外泌體養髮課程", "$3,500", "頭皮清潔・按摩・髮根蓬鬆感", "4",
         ["臉部基礎保養・清潔＋去角質＋精華液導入＋面膜", "頭部 EMS 奈米微晶導入", "頭皮水光槍修護", "頭皮舒壓按摩"]),
        ("../img/top2.jpg", "TOP 02", "24K 黃金撥筋課程", "$3,800", "撥筋手技・放鬆臉部・光澤感", "8",
         ["薰衣草熱蒸・喚醒肌膚", "韓式雙效水循環小氣泡", "手清粉刺・毛孔潔淨", "24K 緊緻安瓶・微針導入",
          "24K 金箔能量護理", "黃金面霜・撥筋按摩", "EMS 導入・緊緻提拉", "黃金軟膜・縮水修護"]),
        ("../img/top3.jpg", "TOP 03", "木乃伊緊緻術課程", "$3,800", "敷貼包覆・輪廓按摩・緊緻感", "6",
         ["薰衣草熱蒸", "韓式雙效水循環小氣泡", "手清粉刺・毛孔潔淨", "緊緻安瓶・微針導入", "木乃伊緊緻包覆術", "客製化保養導入"]),
    ]
    tc = "".join(f'''<div class="tc"><img src="{im}" alt=""><div class="b"><div class="rk">{rk}</div><h3>{t}</h3><div class="p">{p}</div>
<div class="tg">{tg}</div><div class="fh">課程流程・{n} 步驟</div><ol>{"".join(f"<li>{s}</li>" for s in st)}</ol></div></div>'''
                 for im, rk, t, p, tg, n, st in tops)

    pages = []
    pages.append(f'''<section class="page winter"><div class="in">
<div class="eyebrow">Winter Glow Season</div><h1>冬日亮膚季</h1><div class="date">2026.11.01 — 2027.01.31</div>
<div class="rule"><i></i><b></b><i></i></div><div class="sub">五大人氣課程　任選一堂</div>
<div class="price"><span class="lab">活動價</span><span class="num"><small>$</small>2,500</span></div>
<ol class="wl">{wl}</ol><div class="cta">掃描下方 QR Code・LINE 預約活動課程</div>
</div>{foot()}</section>''')
    pages.append(f'''<section class="page gift"><img class="bg" src="../img/giftbg.jpg" alt=""><div class="veil"></div><div class="in">
<div class="eyebrow">a little gift for you</div><h1>打卡就送</h1><div class="sub">隨身香氛清潔噴霧・檸檬草 20ml</div>
<div class="glass">
<div class="gstep"><span class="n">01</span><div><b>在店內拍照打卡</b><span>空間、療程、喜歡的角落都可以</span></div></div>
<div class="gstep"><span class="n">02</span><div><b>限動標記 @guangmeitaiwan</b><span>帳號記得公開，我們才看得到</span></div></div>
<div class="gstep"><span class="n">03</span><div><b>保留 24 小時，出示給我們</b><span>現場送你一個隨身噴霧</span></div></div>
</div>
<p class="brandline">加入法國有機芳療品牌 <i>Le Comptoir Aroma</i><br>檸檬草精油，清新草本柑橘香</p>
<p class="small">＊[活動期間・數量有限，送完為止]　外用清潔噴霧，請勿噴向眼睛，遠離火源</p>
</div>{foot()}</section>''')
    pages.append(f'''<section class="page"><div class="in">
<div class="eyebrow">Best Sellers</div><h2 class="h2">人氣 TOP 3</h2>
{Z(1.0, '<p class="lead">第一次來不知道選哪個？從大家最常做的開始。</p>' + tc)}
</div>{foot()}</section>''')
    pages.append(face_pages())
    pages.append(f'''<section class="page zs"><div class="in">
<div class="eyebrow">Scalp Care</div><h2 class="h2">頭皮養護</h2>
<div class="course" style="margin-top:4mm">
 <div class="ch"><h3>外泌體養髮<span class="badge">TOP 1</span><span class="badge">冬日活動</span></h3><span class="tm">90 分鐘</span><span class="pr"><s>$3,900</s><b>$2,500</b></span></div>
 <div class="info" style="margin-top:3mm"><div class="lab">課程內容</div><ol class="st">
 <li>臉部基礎保養・清潔＋去角質＋精華液導入＋面膜</li><li>頭部 EMS 奈米微晶導入</li><li>頭皮水光槍修護</li><li>頭皮舒壓按摩</li></ol>
 <p class="ds">頭皮養護加上臉部基礎保養，一次照顧頭皮與肌膚。</p>
 <p class="fit"><b>適合</b>頭皮容易出油、髮量稀疏困擾｜染燙受損｜想養護頭皮健康、讓秀髮光澤亮麗｜想好好舒壓放鬆的人</p></div>
</div>
<div class="plan">
 <div class="pl">頭皮養護，平均一次</div><div class="pb"><small>$</small>880</div><div class="pt">1 個月 5 次・<b>$4,400</b></div><hr>
 <div class="cols"><div><div class="lab" style="font-size:10pt">療程約 30 分鐘</div><ol class="st" style="font-size:11pt">
 <li>5 分鐘頭皮按摩</li><li>20 分鐘靈芝外泌體微晶導入</li><li>外泌體育髮精華按摩 3 分鐘</li><li>熱敷眼罩</li></ol></div>
 <div><div class="lab" style="font-size:10pt">注意事項</div><p class="note">・來店前務必清潔頭皮<br>・療程當天請勿洗頭<br>・限一個月內使用完畢</p></div></div>
</div>
</div>{foot()}</section>''')
    pages.append(f'''<section class="page zb"><div class="in">
<div class="eyebrow">Body・Healing・For Pros</div><h2 class="h2">身體・療癒・美業</h2>
<div class="cat"><div class="cat-h"><h3>身體・除毛</h3><span>Body &amp; Waxing</span></div>
<div class="it"><div class="r1"><span class="nm">全身除毛冰肌</span><span class="tm">[時間]</span></div><div class="d">以 Rica 熱蠟除去身體細毛，結束後冰鎮舒緩，皮膚摸起來更光滑。</div><div class="pz"><em>價格請洽官方 LINE</em></div></div></div>
<div class="cat"><div class="cat-h"><h3>水晶療癒</h3><span>Healing</span></div>
<div class="it"><div class="r1"><span class="nm">水晶盤浴</span><span class="tm">40 分鐘</span></div><div class="d">躺在溫熱的水晶盤上，放鬆身體、好好流汗，給自己一段安靜的時間。</div><div class="pz"><s>$1,800</s><b>$1,400</b></div></div>
<div class="it"><div class="r1"><span class="nm">水晶療癒課程</span><span class="tm">[時間]</span></div><div class="d">用水晶陪你沉澱心情，結束時會收到一張專屬祝福小卡。</div><div class="pz"><em>價格請洽官方 LINE</em></div></div></div>
<div class="cat"><div class="cat-h"><h3>美業教學・空間</h3><span>For Pros</span></div>
<div class="it"><div class="r1"><span class="nm">美業創業教學</span></div><div class="d">[課程內容待補]</div><div class="pz"><em>請洽官方 LINE</em></div></div>
<div class="it"><div class="r1"><span class="nm">美業空間出租</span><span class="tm">月租</span></div><div class="d">東區獨立工作空間，適合美甲師、美睫師、個人美業工作者。</div><div class="pz"><b>NT$12,000</b><em> / 月</em><span class="nego">可議價</span></div></div></div>
</div>{foot()}</section>''')
    pages.append(f'''<section class="page rent"><div class="in">
<div class="eyebrow">Space for Rent</div><h2 class="h2">美業獨立工作空間</h2>
<p class="lead">在台北東區，擁有一間屬於自己的工作室，專心服務、經營個人品牌。</p>
<div class="row"><div class="pic"><img src="../img/rent.jpg" alt=""><span>佈置示意圖</span></div>
<ul><li>東區核心地段・交通便利</li><li>獨立專屬空間・隱私佳</li><li>質感環境・專業形象加分</li><li>適合預約制・一對一精緻服務</li></ul></div>
<div class="rp"><span class="lead">月租</span><b>NT$12,000</b><span class="lead">/ 月</span><span class="nego">可議價</span></div>
<p class="lead">租期與價格都可以聊，歡迎 LINE 洽詢・預約參觀</p>
<p class="small">＊示意圖之家具與擺設以現場為準，歡迎預約參觀</p>
</div>{foot()}</section>''')

    return f'''<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8"><title>光美 A4 印刷版</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Noto+Serif+TC:wght@300;400;600;700;900&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>{"".join(pages)}</body></html>'''


(H / "a4.html").write_text(html(), encoding="utf-8")
print("wrote", H / "a4.html")
