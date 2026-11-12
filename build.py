r"""account_dashboard/build.py: 계정 업로드 플랜 통합 대시보드 (박미경 · 하린 · 남AI 탭) — HTML 1장.

  python build.py           # 하린 날짜 폴더 동기화 + site/index.html + 드라이브 001/002/003 폴더에 플랜_대시보드.html
  python build.py --push    # 위 + git commit/push → GitHub Pages 배포

입력(단일 소스, 여기서는 읽기만):
  박미경  ../bench_account_moose  out/sim_calendar.json · reels_gen.json · kpi.csv · publish_plan.py
  하린    ../influencer_harin/publish_calendar.json  (시작 2026-11-12 09:30)
  남AI    소재·일정 없음 → 빈 탭
웹(https)에서는 file:// 링크가 막히므로 드라이브 웹 폴더 링크(DriveFS 메타데이터에서 ID 조회) + 경로 복사를 같이 둔다.
외부 도구는 PIL, ffmpeg(썸네일)만. 크레딧 0. 화면(CSS·JS)은 assets.py.
"""
from __future__ import annotations

import argparse
import base64
import csv
import datetime as dt
import hashlib
import html
import io
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).parent
PROJ = HERE.parent
PARK_P = PROJ / "bench_account_moose"
HARIN_P = PROJ / "influencer_harin"
sys.path.insert(0, str(PARK_P))
sys.path.insert(0, str(HERE))
import publish_plan as pp  # noqa: E402
from assets import CSS, JS  # noqa: E402

ROOT = pp.DRIVE.parent                       # 100. AI 소재 제작
PARK_DRIVE = pp.DRIVE                        # 001. 박미경 계정 업로드
HARIN_DRIVE = ROOT / "002. 하린 계정 업로드"
NAM_DRIVE = ROOT / "003. 남AI 계정 업로드"
PARK_ID = "1eWnbksQjuaQR3swQBFso-pzO606Av_-d"
HARIN_ID = "14g3XEruqpFCZSCvW3Lm8ZDVz2q4Khwm4"
HARIN_CAL = HARIN_P / "publish_calendar.json"
PAGES_URL = "https://geuneee.github.io/ai-account-plan/"
THUMBS = HERE / ".thumbs"
WD = "월화수목금토일"

DECISIONS = [
    ("④", "실촬영 전환일", "미정 — 손등·튜브 실제 촬영 30클립을 찍는 날. 찍기 전까지는 AI 이미지 영상 + AI 라벨 ON 그대로"),
    ("⑤", "CTA '곧 품절' / '3만원대'", "현재 유지(곧 품절) — 2026-11-11 '일단 그냥 둬'. 바꾸려면 v9 재생성"),
]
DECIDED = "결정 완료(2026-11-11): 광고 해시태그 줄(#광고 스팟이지 운영) 넣지 않음 · 섞기 표현 그대로 · 길이 그대로"


# ───────────────────────────────────────────────────────────── 공통 도구 ──
def e(s) -> str:
    return html.escape(str(s), quote=True)


def furl(p: Path) -> str:
    return "file:///" + quote(str(p).replace("\\", "/"), safe="/:._-()")


def win(p) -> str:
    return str(p).replace("/", "\\")


def md(d: str) -> str:
    return f"{int(d[5:7])}/{int(d[8:10])}"


def drive_children(parent_id: str) -> dict:
    """DriveFS 로컬 메타데이터에서 parent 폴더의 하위 폴더 {이름: 드라이브 ID}. 실패하면 빈 dict."""
    out = {}
    try:
        base = Path(os.environ["LOCALAPPDATA"]) / "Google" / "DriveFS"
        for db in base.glob("*/metadata_sqlite_db"):
            c = sqlite3.connect("file:" + db.as_posix() + "?mode=ro", uri=True, timeout=3)
            row = c.execute("select stable_id from items where id=?", (parent_id,)).fetchone()
            if row:
                for t, i in c.execute("select i.local_title,i.id from items i join stable_parents s on s.item_stable_id=i.stable_id "
                                      "where s.parent_stable_id=? and i.trashed=0 and i.is_folder=1 and i.id not like 'local-%' and i.is_folder=1", (row[0],)):
                    if i and not i.startswith("local"):
                        out[t] = i
            c.close()
    except Exception as ex:  # noqa: BLE001
        print(f"드라이브 ID 조회 실패: {ex}")
    return out


def gurl(i: str | None) -> str | None:
    return f"https://drive.google.com/drive/folders/{i}" if i else None


def thumb(src: Path | None) -> str:
    """mp4/이미지 → 폭 132px JPEG data URI (.thumbs 캐시, 키 = 경로+크기+수정시각)."""
    if not src or not src.exists():
        return ""
    st = src.stat()
    key = hashlib.md5(f"{src}|{st.st_size}|{int(st.st_mtime)}".encode()).hexdigest()
    THUMBS.mkdir(exist_ok=True)
    f = THUMBS / f"{key}.jpg"
    if not f.exists():
        try:
            from PIL import Image
            if src.suffix.lower() == ".mp4":
                raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "0.6", "-i", str(src), "-frames:v", "1", "-f", "image2pipe",
                                      "-vcodec", "png", "-"], capture_output=True, timeout=60).stdout
                im = Image.open(io.BytesIO(raw))
            else:
                im = Image.open(src)
            im = im.convert("RGB")
            im.thumbnail((132, 236))
            im.save(f, "JPEG", quality=62, optimize=True)
        except Exception as ex:  # noqa: BLE001
            print(f"썸네일 실패 {src.name}: {ex}")
            return ""
    return "data:image/jpeg;base64," + base64.b64encode(f.read_bytes()).decode()


def tag(cls: str, txt: str) -> str:
    return f'<span class="tag {cls}">{e(txt)}</span>'


def folder_actions(folder: Path, web: str | None, web_parent: str | None) -> str:
    b = []
    if web:
        b.append(f'<a class="btn p" href="{web}" target="_blank" rel="noopener">☁ 드라이브에서 열기</a>')
    elif web_parent:
        b.append(f'<a class="btn" href="{web_parent}" target="_blank" rel="noopener">☁ 드라이브(상위 폴더)</a>')
    b.append(f'<a class="btn local" href="{furl(folder)}" target="_blank">📂 PC 폴더 열기</a>')
    b.append(f'<button class="btn" data-cp="{e(win(folder))}">📋 경로 복사</button>')
    return " ".join(b)


def slot_card(s: dict) -> str:
    th = f'<img class="th" loading="lazy" alt="" src="{s["thumb"]}">' if s.get("thumb") else '<div class="th none">미리보기 없음</div>'
    plat_cls = "ig" if s["plat"].startswith("IG") else "tt"
    plat_txt = {"IG": "인스타", "TT": "틱톡", "IG 카드": "인스타 카드"}.get(s["plat"], s["plat"])
    head = (f'<div class="s1"><span class="tm">{e(s["time"])}</span><span class="pl {plat_cls}">{e(plat_txt)}</span>'
            f'{tag(*s["status"])}<span class="late"></span></div>')
    files = "".join(f"<div>{e(x)}</div>" for x in s.get("files", []))
    act = []
    if s.get("caption"):
        act.append(f'<button class="btn p" data-cp="{e(s.get("cap_copy") or s["caption"])}" data-msg="캡션 복사됨">📋 캡션 복사</button>')
    if s.get("url"):
        act.append(f'<a class="btn" href="{e(s["url"])}" target="_blank" rel="noopener">올린 글 보기</a>')
    cap = ""
    if s.get("caption"):
        lines = "\n".join(f'<span class="mk">{e(x)}</span>' if x.startswith("[결정②") else e(x) for x in s["caption"].rstrip("\n").splitlines())
        cap = f'<details class="capd"><summary>캡션 보기</summary><pre class="cap">{lines}</pre></details>'
    kpi = ""
    if s.get("track"):
        v = s.get("views") or ""
        jd = s.get("verdict") or ""
        jc = "ok" if jd.startswith("복제") else "acc" if jd.startswith("유지") else "bad"
        kpi = ('<div class="kpi">' + (tag("ok", "URL 기록됨") if s.get("url") else '<span class="sub">URL 미기록</span>')
               + (f" · 48h {e(v)}회" if v else "") + (f" {tag(jc, jd)}" if jd else "") + "</div>")
    note = f'<div class="note">{e(s["note"])}</div>' if s.get("note") else ""
    return (f'<div class="slot" data-dt="{e(s.get("dt", ""))}" data-track="{1 if s.get("track") else 0}" data-url="{1 if s.get("url") else 0}">{th}'
            f'<div class="sb">{head}<div class="ti">{e(s["title"])}</div>'
            + (f'<div class="sub">{e(s["sub"])}</div>' if s.get("sub") else "")
            + f'<div class="fn">{files}</div>{note}{kpi}<div class="act">{" ".join(act)}</div>{cap}</div></div>')


def day_card(d: str, meta: str, tags: str, folder: Path, web, web_parent, slots: list[dict]) -> str:
    date = dt.date.fromisoformat(d)
    return (f'<div class="day" data-date="{d}"><div class="dh"><span class="d">{date.month}/{date.day} ({WD[date.weekday()]})</span>'
            f'<span class="k">{e(meta)}</span>{tags}<span class="da">{folder_actions(folder, web, web_parent)}</span></div>'
            f'<div class="path">{e(win(folder))}</div><div class="slots">{"".join(slot_card(s) for s in slots)}</div></div>')


def path_table(rows) -> str:
    return ('<div class="box scroll"><table><tr><th>항목</th><th>전체 경로</th><th></th></tr>'
            + "".join(f'<tr><td>{e(a)}</td><td class="mono">{e(win(b))}</td><td class="nw"><a class="btn local" href="{furl(Path(b))}" target="_blank">열기</a> '
                      f'<button class="btn" data-cp="{e(win(b))}">복사</button></td></tr>' for a, b in rows) + "</table></div>")


def tiles(items) -> str:
    return '<div class="grid">' + "".join(f'<div class="tile"><div class="n">{e(n)}</div><div class="l">{e(l)}</div></div>' for n, l in items) + "</div>"


def no_mark(cap: str) -> str:
    return "\n".join(x for x in cap.splitlines() if not x.startswith("[결정②"))


# ───────────────────────────────────────────────────────────────── 박미경 ──
def load_kpi() -> dict:
    f = PARK_P / "kpi.csv"
    if not f.exists():
        return {}
    with f.open(encoding="utf-8-sig", newline="") as fh:
        return {(r["id"], r["account"], r["date"]): r for r in csv.DictReader(fh)}


def park_section() -> str:
    kpi = load_kpi()
    ids = drive_children(PARK_ID)
    days = sorted({r["date"] for r in pp.CAL})
    by_day = {d: [r for r in pp.CAL if r["date"] == d] for d in days}
    total = sum(2 if r["kind"] == "reel" else 1 for r in pp.CAL)
    posted = sum(1 for r in kpi.values() if r.get("url"))
    judged = sum(1 for r in kpi.values() if r.get("판정"))
    ready = sum(1 for d in days if (PARK_DRIVE / d).exists())
    out = ['<div class="hero"><h2>박미경 계정</h2><div class="sub">스팟멜트 기미조합 · 6주 운영 '
           f'{md(days[0])}~{md(days[-1])} · 인스타 10:30 / 15:00, 틱톡은 5분 뒤(반대 본), 카드뉴스 화·금 12:30</div></div>',
           tiles([(f"{posted}/{total}", "업로드 URL 기록"), (str(judged), "48h 판정 완료"), (f"{ready}/{len(days)}", "날짜 폴더 생성(전날 18:00 자동)"),
                  (f"{len(days)}일", "전체 일정")]),
           '<h3 class="sec">오늘 올릴 것</h3><div class="todaybox"></div>', '<h3 class="sec">전체 일정</h3>']
    for wk in sorted({r["wk"] for r in pp.CAL}):
        wdays = [d for d in days if by_day[d][0]["wk"] == wk]
        bon = "인스타 A본 · 틱톡 B본" if wk <= 3 else "인스타 B본 · 틱톡 A본"
        out.append(f'<details class="wk"><summary>{wk}주차 <span class="sub">{md(wdays[0])}~{md(wdays[-1])} · {bon}</span></summary>')
        for d in wdays:
            date = dt.date.fromisoformat(d)
            dayn = (date - pp.START).days + 1
            folder = PARK_DRIVE / d
            exists = folder.exists()
            files = {f.name for f in folder.iterdir()} if exists else set()
            slots = []
            for r in sorted(by_day[d], key=lambda x: x["slot"]):
                hh, mm = (int(x) for x in r["slot"].split(":"))
                if r["kind"] == "reel":
                    for plat, rid, t in (("IG", r["IG"], dt.time(hh, mm)),
                                         ("TT", r["TT"], (dt.datetime.combine(date, dt.time(hh, mm)) + pp.TT_OFFSET).time())):
                        base = f"{t:%H%M}_{plat}_{rid}"
                        src = PARK_P / "out" / f"{rid}.mp4"
                        v = pp.GEN.get(rid, {}).get("vars", {})
                        st = ("ok", "올릴 준비 완료") if f"{base}.mp4" in files else ("wait", "전날 18:00 폴더 복사") if src.exists() else ("bad", "미제작")
                        k = kpi.get((rid, plat, d), {})
                        cap = pp.reel_caption(rid, plat)
                        cov = folder / f"{base}_cover.png"
                        slots.append(dict(
                            time=f"{t:%H:%M}", plat=plat, title=f"{rid} · {'B' if rid.endswith('B') else 'A'}본",
                            sub=" · ".join(x for x in (v.get("나이"), v.get("고민"), v.get("약국템"), v.get("권위")) if x),
                            status=st, files=[f"{base}.mp4", f"{base}_cover.png (커버)"], thumb=thumb(cov if cov.exists() else src),
                            caption=cap, cap_copy=no_mark(cap), url=k.get("url"), views=k.get("views_48h"), verdict=k.get("판정"),
                            track=True, dt=f"{d}T{t:%H:%M}"))
                else:
                    cid = r["IG"]
                    basec = cid.rstrip("b")
                    hhmm = f"{hh:02d}{mm:02d}"
                    srcc = pp.CARDS_DIR / f"{basec}_1.jpg" if pp.CARDS_DIR else None
                    st = (("ok", "올릴 준비 완료") if f"{hhmm}_IG_{cid}_1.jpg" in files
                          else ("wait", "전날 18:00 폴더 복사") if srcc and srcc.exists() else ("bad", "미제작"))
                    k = kpi.get((cid, "IG", d), {})
                    cap = pp.card_caption(cid)
                    slots.append(dict(
                        time=r["slot"], plat="IG 카드", title=f"{cid} · {pp.CARD_TITLE[basec]}", sub="카드뉴스 2장",
                        status=st, files=[f"{hhmm}_IG_{cid}_1.jpg", f"{hhmm}_IG_{cid}_2.jpg"], thumb=thumb(srcc),
                        caption=cap, cap_copy=no_mark(cap), note="b본 문구 변형 미제작 → A본 사진 사용" if cid.endswith("b") else "",
                        url=k.get("url"), views=k.get("views_48h"), verdict=k.get("판정"), track=True, dt=f"{d}T{r['slot']}"))
            slots.sort(key=lambda s: s["time"])
            tags = tag("ok", "폴더 있음") if exists else tag("wait", "전날 18:00 생성")
            if dayn <= pp.PROTECT_DAYS:
                tags += tag("bad", "첫 3일 보호: 하루 2편·링크 없음")
            elif dayn == pp.PROTECT_DAYS + 1:
                tags += tag("acc", "틱톡 바이오 링크 넣는 날")
            rec = date + dt.timedelta(days=2)
            out.append(day_card(d, f"{dayn}일차 · 업로드 {len(slots)}회 · 조회수 기록 {rec.month}/{rec.day} 09:00", tags, folder,
                                gurl(ids.get(d)), gurl(PARK_ID), slots))
        out.append("</details>")
    out.append('<h3 class="sec">올리는 법</h3><div class="box"><ol class="how">'
               '<li><b>PC</b>: 날짜 칸의 <b>경로 복사</b> → 인스타/틱톡 업로드 창 "컴퓨터에서 선택" → 파일 대화상자 주소칸에 붙여넣기 + Enter. '
               '<b>폰</b>: 드라이브에서 열기 → 파일 저장.</li>'
               '<li>파일명 앞 숫자가 올릴 시각(1030 = 10:30). <b>캡션 복사</b> 버튼으로 캡션을 그대로 붙여넣으면 됩니다. 커버는 <code>_cover.png</code>, AI 라벨 ON.</li>'
               '<li>올린 링크를 알려 주시면(또는 <code>python kpi.py url D01 IG 링크</code>) 장부에 기록 → 48시간 뒤 조회수 → 판정이 칸에 표시됩니다.</li>'
               '<li>슬롯을 놓치면 몰아 올리지 말고 하루 뒤로 미룹니다.</li></ol>'
               '<div class="sub" style="margin-top:8px">판정 기준(인스타 48h): 3만↑ 복제 / 1만~3만 유지 / 1천~1만 훅 교체 / 1천 미만 3연속 고민 교체. 틱톡 1주차는 1/3 척도.</div></div>')
    out.append('<h3 class="sec">결정 대기</h3><div class="sub">' + e(DECIDED) + '</div><div class="box scroll"><table>'
               + "".join(f"<tr><td class='nw'><b>{a}</b> {e(b)}</td><td>{e(c)}</td></tr>" for a, b, c in DECISIONS) + "</table></div>")
    out.append('<h3 class="sec">경로 모음</h3>' + path_table([
        ("업로드 폴더(날짜별)", PARK_DRIVE), ("프로젝트", PARK_P), ("캘린더 단일 소스", PARK_P / "out" / "sim_calendar.json"),
        ("KPI 장부", PARK_P / "kpi.csv"), ("운영 런북", PARK_P / "운영_런북_인스타.md"), ("운영 계획 정본", PARK_P / "운영계획_최종.md"),
        ("전날 18:00 스케줄러", PARK_P / "run_publish_tomorrow.cmd"), ("대시보드 생성기", HERE / "build.py")]))
    return "".join(out)


# ─────────────────────────────────────────────────────────────────── 하린 ──
def harin_names(it: dict) -> tuple[list[tuple[Path, str]], str]:
    """(원본, 업로드 폴더 파일명) 목록과 캡션 파일명."""
    base = f"{it['time'].replace(':', '')}_{it['plat']}_{it['id']}"
    srcs = [ROOT / s for s in it.get("src", [])]
    if len(srcs) == 1:
        pairs = [(srcs[0], base + srcs[0].suffix.lower())]
    else:
        pairs = [(s, f"{base}_{i}{s.suffix.lower()}") for i, s in enumerate(srcs, 1)]
    return pairs, base + "_캡션.txt"


def cap_body(text: str) -> str:
    """캡션 파일에서 올릴 글만. '----' 줄 아래([레퍼런스]·[업로드] 제작 메모)는 붙여넣으면 안 되므로 뺀다."""
    out = []
    for ln in text.splitlines():
        if ln.strip().startswith("----"):
            break
        out.append(ln)
    return "\n".join(out).strip()


def harin_sync(cal: dict) -> None:
    """ready 항목을 002. 하린 계정 업로드\\YYYY-MM-DD\\ 로 복사(같은 크기면 건너뜀). 원본은 건드리지 않음."""
    for it in cal["items"]:
        if it["status"] != "ready":
            continue
        folder = HARIN_DRIVE / it["date"]
        folder.mkdir(parents=True, exist_ok=True)
        pairs, capname = harin_names(it)
        for src, name in pairs:
            dst = folder / name
            if src.exists() and not (dst.exists() and dst.stat().st_size == src.stat().st_size):
                shutil.copy2(src, dst)
        if it.get("caption_src"):
            cs = ROOT / it["caption_src"]
            if cs.exists():
                (folder / capname).write_text(cap_body(cs.read_text(encoding="utf-8-sig")) + "\n", encoding="utf-8")
        elif it.get("caption"):
            (folder / capname).write_text(it["caption"].strip() + "\n", encoding="utf-8")
        if it.get("cover"):
            cv = ROOT / it["cover"]
            dst = folder / (capname[:-len("_캡션.txt")] + "_cover" + cv.suffix.lower())
            if cv.exists() and not (dst.exists() and dst.stat().st_size == cv.stat().st_size):
                shutil.copy2(cv, dst)


def harin_section() -> str:
    cal = json.loads(HARIN_CAL.read_text(encoding="utf-8"))
    try:
        harin_sync(cal)
    except OSError as ex:
        print(f"하린 폴더 동기화 실패: {ex}")
    ids = drive_children(HARIN_ID)
    days = sorted({it["date"] for it in cal["items"]})
    n_ready = sum(1 for it in cal["items"] if it["status"] == "ready")
    n_todo = sum(1 for it in cal["items"] if it["status"] == "todo")
    out = ['<div class="hero"><h2>하린 계정</h2><div class="sub">벤치마킹 조합 영상(아젤리아·비판텐) 하루 2편 + 기존 하린 소재 · 3일치씩 배치 후 검토 · '
           '<b>시작 11/12(목) 오전</b></div></div>',
           tiles([(f"{n_ready}건", "올릴 준비된 소재"), (f"{n_todo}건", "미제작"), (f"{len(cal.get('hold', []))}건", "보류"),
                  (f"{md(days[0])}~{md(days[-1])}", "일정 잡힌 기간")]),
           '<div class="box warn"><b>확인 필요</b><ul class="how"><li>이미 만들어 둔 벤치마킹 조합 영상(아젤리아·비판텐)을 날짜 폴더에 넣었습니다. 지금은 <b>3일치(11/12~14)</b>만 배치했고, 검토 후 다음 3일치를 넣습니다.</li><li>박미경 계정과 같은 영상이 겹치지 않도록 하린은 D29~D34 편을 썼습니다.</li><li>2026-11-12에 새로 만든 전신·운동·데일리룩 사진은 일정에서 빼고 보류 칸에 두었습니다(검토 후 결정).</li><li>11/13 릴스 1편은 캡션이 없습니다. 목소리 미확정 → 릴스 2편(외박쌩얼)은 보류 칸.</li></ul></div>',
           '<h3 class="sec">오늘 올릴 것</h3><div class="todaybox"></div>', '<h3 class="sec">전체 일정</h3>',
           f'<details class="wk"><summary>1주차 <span class="sub">{md(days[0])}~{md(days[-1])} · 소재 있는 날만</span></summary>']
    for d in days:
        folder = HARIN_DRIVE / d
        files = {f.name for f in folder.iterdir()} if folder.exists() else set()
        slots = []
        for it in sorted((x for x in cal["items"] if x["date"] == d), key=lambda x: x["time"]):
            pairs, capname = harin_names(it)
            cap = ""
            if it.get("caption_src") and (ROOT / it["caption_src"]).exists():
                cap = cap_body((ROOT / it["caption_src"]).read_text(encoding="utf-8-sig"))
            elif it.get("caption"):
                cap = it["caption"].strip()
            if it["status"] == "todo":
                st = ("bad", "미제작")
            elif pairs and all(n in files for _, n in pairs):
                st = ("ok", "올릴 준비 완료")
            else:
                st = ("wait", "폴더 복사 대기")
            names = [n for _, n in pairs]
            shown = names if len(names) <= 2 else [f"{names[0]} ~ {names[-1]} ({len(names)}장)"]
            slots.append(dict(time=it["time"], plat=it["plat"], title=it["title"], sub=it["kind"], status=st,
                              files=shown + ([capname] if cap else []), thumb=thumb(pairs[0][0]) if pairs else "",
                              caption=cap, note=it.get("note", ""), track=False, dt=f"{d}T{it['time']}"))
        n_ok = sum(1 for s in slots if s["status"][0] == "ok")
        tags = tag("ok", "폴더 있음") if folder.exists() else tag("wait", "폴더 없음")
        out.append(day_card(d, f"{n_ok}/{len(slots)}건 준비", tags, folder, gurl(ids.get(d)), gurl(HARIN_ID), slots))
    out.append("</details>")
    hold = "".join(f'<tr><td><b>{e(h["title"])}</b></td><td>{e(h["reason"])}</td><td class="mono">{e(win(ROOT / h["src"]))}</td>'
                   f'<td class="nw"><button class="btn" data-cp="{e(win(ROOT / h["src"]))}">복사</button></td></tr>' for h in cal.get("hold", []))
    out.append(f'<h3 class="sec">보류</h3><div class="box scroll"><table><tr><th>소재</th><th>이유</th><th>위치</th><th></th></tr>{hold}</table></div>')
    lib = []
    for d in sorted(ROOT.iterdir()):
        if d.is_dir() and "하린" in d.name and d != HARIN_DRIVE:
            vs = sorted((x for x in d.glob("v*_*") if x.is_dir()), key=lambda x: x.name)
            lib.append((d.name + (f" · 최신 {vs[-1].name}" if vs else ""), vs[-1] if vs else d))
    out.append('<h3 class="sec">소재 보관함 · 경로 모음</h3>' + path_table(
        [("업로드 폴더(날짜별)", HARIN_DRIVE), ("캘린더 단일 소스(여기만 고치면 반영)", HARIN_CAL), ("프로젝트", HARIN_P)] + lib))
    return "".join(out)


# ─────────────────────────────────────────────────────────────────── 남AI ──
def nam_section() -> str:
    try:
        NAM_DRIVE.mkdir(exist_ok=True)
    except OSError as ex:
        print(f"남AI 폴더 생성 실패: {ex}")
    return ('<div class="hero"><h2>남AI 계정</h2><div class="sub">아직 소재·일정이 없습니다. 탭과 업로드 폴더만 준비해 둔 상태입니다.</div></div>'
            + tiles([("0건", "올릴 준비된 소재"), ("미정", "시작일"), ("미정", "플랫폼·하루 편수"), ("미정", "캐릭터·콘셉트")])
            + '<h3 class="sec">오늘 올릴 것</h3><div class="todaybox"></div>'
            '<div class="box warn"><b>시작하려면 정해 주실 것</b><ol class="how"><li>캐릭터(이름·나이대·직업 설정)와 다룰 제품</li>'
            '<li>플랫폼(인스타/틱톡)과 하루 편수, 시작일</li><li>벤치마킹할 계정이나 참고 영상</li></ol>'
            '<div class="sub" style="margin-top:6px">정해지면 박미경·하린과 같은 구조(캘린더 1개 → 날짜별 폴더 → 이 탭)로 채웁니다.</div></div>'
            + '<h3 class="sec">경로 모음</h3>' + path_table([("업로드 폴더(비어 있음)", NAM_DRIVE)]))


# ───────────────────────────────────────────────────────────────── 페이지 ──
def render() -> str:
    now = dt.datetime.now()
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex, nofollow"><title>계정 업로드 플랜</title>'
            f'<style>{CSS}</style></head><body data-default="park">'
            '<div class="top"><div class="topin"><h1>계정 업로드 플랜</h1>'
            f'<div class="gen">갱신 {now:%m/%d %H:%M} · 매일 18:00 자동</div><div class="tabs">'
            '<button class="tab" data-t="park">박미경<span class="c"></span></button><button class="tab" data-t="harin">하린<span class="c"></span></button>'
            '<button class="tab" data-t="nam">남AI<span class="c"></span></button></div></div></div>'
            f'<div class="wrap"><section class="pane" id="park">{park_section()}</section><section class="pane" id="harin">{harin_section()}</section>'
            f'<section class="pane" id="nam">{nam_section()}</section>'
            f'<div class="sub" style="margin:28px 0 10px">웹 주소 <a href="{PAGES_URL}">{PAGES_URL}</a> · 영상 업로드는 직접, 나머지(폴더·캡션·기록)는 자동 준비</div></div>'
            f'<div id="toast" class="toast"></div><script>{JS}</script></body></html>')


def build(push: bool = False) -> list[Path]:
    doc = render()
    (HERE / "site").mkdir(exist_ok=True)
    targets = [(HERE / "site" / "index.html", "park"), (PARK_P / "publish" / "플랜_대시보드.html", "park"),
               (PARK_DRIVE / "플랜_대시보드.html", "park"), (HARIN_DRIVE / "플랜_대시보드.html", "harin"),
               (HARIN_P / "out" / "플랜_대시보드.html", "harin"), (NAM_DRIVE / "플랜_대시보드.html", "nam")]
    written = []
    for dst, tab in targets:
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(doc.replace('<body data-default="park">', f'<body data-default="{tab}">', 1), encoding="utf-8")
            written.append(dst)
        except OSError as ex:
            print(f"쓰기 실패 {dst}: {ex}")
    (HERE / "site" / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    if push and (HERE / ".git").exists():
        def git(*a):
            return subprocess.run(["git", "-C", str(HERE), *a], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
        git("add", "-A")
        if git("diff", "--cached", "--quiet").returncode:
            git("commit", "-m", f"대시보드 갱신 {dt.datetime.now():%Y-%m-%d %H:%M}")
            r = git("push")
            print("push:", "OK" if r.returncode == 0 else r.stderr.strip()[-300:])
    return written


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()
    for p in build(a.push):
        print(p)
