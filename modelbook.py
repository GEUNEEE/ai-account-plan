# 계정 인물 모델 북(하린 컴카드와 같은 8컷 구성) — 인물 정의는 CHARS 한 곳
#   python modelbook.py park prompts          → 프롬프트만 쓰기
#   python modelbook.py park gen [컷이름 ...]  → 없는 컷만 한 장씩 생성(Codex, 0원). 컷이름 주면 그 컷만 다시
#   python modelbook.py park card             → 8컷 합본 + character/ 정본 + 드라이브 복사
import shutil, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

PROJ = Path(__file__).parent.parent
ROOT = Path(r"G:\.shortcut-targets-by-id\1aExMnOUaz0KyUTRAhiSvAjCebgHx7Wa1\스카이님 공유용 스프레드 개설"
            r"\701. 스팟멜트크림 후기 사진 DA\100. AI 소재 제작")
REF_NOTE = ("The reference image shows THIS person. Use it ONLY to keep the exact identity "
            "(face shape, eyes, brows, nose, lips, skin tone and texture, age, hair). Do NOT copy its framing, pose, clothes or background.\n\n")
STUDIO = ("STYLE: model comp card / polaroid digital, a real photograph, not CGI. Plain light grey-white seamless studio backdrop, "
          "soft large diffused key light from the front-left, gentle fill, natural shadows, true-to-life color, neutral white balance, "
          "skin never orange. Shot on a full-frame camera with an 85mm lens, crisp natural detail, NO retouching, NO skin smoothing, "
          "real age kept. Calm, friendly, subtle closed-mouth smile unless stated otherwise. NO text, NO logo, NO watermark, NO frame or border.")

# 컷: (파일 이름, 한글 라벨, 설명) — {hair_back} 는 인물별 문구
SHOTS = [
    ("01_front", "정면", "Vertical 1:2 frame. FRONT: head and shoulders, facing the camera straight on, eyes into the lens, faint closed-mouth smile."),
    ("02_left", "왼쪽 옆모습", "Vertical 1:2 frame. LEFT PROFILE: close head-and-shoulders, face turned in strict side profile toward the LEFT edge of the frame, ear and jawline visible."),
    ("03_right", "오른쪽 옆모습", "Vertical 1:2 frame. RIGHT PROFILE: close head-and-shoulders, face turned in strict side profile toward the RIGHT edge of the frame, ear and jawline visible."),
    ("04_three_quarter", "반측면", "Vertical 1:2 frame. THREE-QUARTER: head and shoulders turned three-quarters toward the right, eyes back to the lens, soft smile."),
    ("05_back", "뒷모습", "Vertical 1:2 frame. BACK: seen from directly behind from the head to the waist, {hair_back}, head turned very slightly so only a sliver of cheek shows."),
    ("06_upper_body", "상반신", "Vertical 1:2 frame. UPPER BODY: seated at a plain white table, forearms resting on it with hands loosely clasped, leaning slightly forward, warm smile into the lens."),
    ("07_half_body", "허리 위", "Vertical 1:2 frame. HALF BODY: standing, framed from head to mid-thigh, one hand lightly holding the other wrist in front, relaxed upright posture, smile into the lens."),
    ("08_full_body", "전신", "Vertical 1:2 frame. FULL BODY: standing head to toe with some floor visible, arms relaxed, weight on one leg, natural confident posture, looking into the lens."),
]

CHARS = {
    "park": dict(
        name="박미경", proj="bench_account_moose", ref="gen/PMK_B2.png", prefix="PMK_mb_",
        drive=ROOT / "001. 박미경 계정 업로드" / "인물 모델 북",
        hair_back="dark hair with a few gray strands gathered in a low elegant chignon at the nape, a few loose strands",
        identity=("IDENTITY (fictional new person, same woman in every shot): an elegant, graceful, well-kept Korean woman who is honestly 55, "
                  "not an actress and not a model. Soft heart-shaped face with a slightly loose jawline, fair neutral skin, gently arched brows, "
                  "warm rounded eyes with slightly hooded lids and smile lines, small refined nose, slightly full lips in a natural coral-beige. "
                  "Dark softly waved hair with a few gray strands at the temples, gathered in a low chignon, a few loose strands framing the face. "
                  "Tiny gold drop earrings. Slim, upright posture. She does not resemble any celebrity or any specific real person.\n\n"
                  "SKIN (real, age 55): matte natural skin with visible pores, crow's feet, fine creases under the eyes, natural nasolabial folds, "
                  "faint marionette lines, horizontal neck lines, a few small faint sun spots on the cheekbones, slight redness beside the nose. "
                  "Minimal everyday makeup. Not porcelain, not airbrushed, not glossy, not looking under 50."),
        wardrobe=("Wardrobe: cream silk blouse with a soft collar, sleeves to the wrist; when the legs are visible, beige wide-leg wool trousers "
                  "and low ivory block-heel pumps."),
    ),
    "nam": dict(
        name="남자 AI", proj="influencer_nam", ref="gen/NAM_ID.png", prefix="NAM_mb_",
        drive=ROOT / "003. 남AI 계정 업로드" / "인물 모델 북",
        hair_back="dark ash-brown medium-length wavy hair swept back, reaching the nape, broad muscular back and shoulders filling the t-shirt",
        # 2026-11-20 후보 3(gen/NAM_I.png) 확정 — 벤치 @bestar322 느낌, 20대 후반 피트니스·카페 인플루언서. 이전 41세 안은 gen/old_41
        identity=("IDENTITY (fictional new person, same man in every shot): a Korean man, 28, a fitness and cafe lifestyle influencer who also works "
                  "as a fashion model, strikingly handsome. Soft oval face with a clean defined jawline, straight dark brows, bright inner-double-eyelid "
                  "eyes that curve when he smiles, straight nose with a slightly rounded tip, medium lips, a small dimple on one cheek when smiling. "
                  "Dark ash-brown medium-length hair in loose natural waves swept back from the forehead, a few strands falling forward, tucked behind one ear. "
                  "Tall, about 184 cm, long legs, very muscular but lean: broad shoulders, big chest, thick defined arms, narrow waist, clearly visible "
                  "through his clothes, not a bodybuilder. He does not resemble any celebrity, idol, actor or any specific real person.\n\n"
                  "SKIN (real, age 28): real young male skin with visible fine pores, very faint shaving shadow on the upper lip and jaw, one or two tiny moles, "
                  "slight natural redness beside the nose, faint under-eye texture, natural slight facial asymmetry, a few flyaway hairs. "
                  "Not airbrushed, not porcelain, not glossy, no makeup look, no beauty filter."),
        wardrobe=("Wardrobe: fitted plain white crewneck t-shirt, a thin silver chain necklace, a simple watch; when the legs are visible, "
                  "black wide-leg slacks and black leather derby shoes."),
    ),
}


def prompts(c):
    p = PROJ / c["proj"]
    for n, _, shot in SHOTS:
        txt = REF_NOTE + shot.format(hair_back=c["hair_back"]) + "\n\n" + c["identity"] + "\n\n" + STUDIO + " " + c["wardrobe"]
        (p / f"prompts/{c['prefix']}{n}.txt").write_text(txt.replace('"', "'"), encoding="utf-8")


def gen(c, only):
    p = PROJ / c["proj"]
    assert (p / c["ref"]).exists(), f"기준 얼굴 없음: {p / c['ref']}"
    assert c["identity"], "identity 비어 있음"
    prompts(c)
    for n, ko, _ in SHOTS:
        name = c["prefix"] + n
        if (p / f"gen/{name}.png").exists() and n not in only:
            continue
        r = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command",
                            f"& ./gen.ps1 -Name {name} -PromptFile prompts/{name}.txt -Ref {c['ref']}"],
                           cwd=p, timeout=900, capture_output=True, text=True)
        print(ko, "OK" if (p / f"gen/{name}.png").exists() and r.returncode == 0 else "실패", flush=True)


def font(size):
    for f in ("C:/Windows/Fonts/malgunbd.ttf", "C:/Windows/Fonts/malgun.ttf"):
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def card(c):
    p = PROJ / c["proj"]
    CW, CH, GAP, LH, M = 560, 1120, 8, 110, 8
    W, H = M * 2 + CW * 4 + GAP * 3, M * 2 + (CH + LH) * 2
    im = Image.new("RGB", (W, H), (255, 255, 255))
    d, f = ImageDraw.Draw(im), font(34)
    ch = p / "character"
    ch.mkdir(exist_ok=True)
    c["drive"].mkdir(parents=True, exist_ok=True)
    for i, (n, ko, _) in enumerate(SHOTS):
        src = p / f"gen/{c['prefix']}{n}.png"
        r, col = divmod(i, 4)
        x, y = M + col * (CW + GAP), M + r * (CH + LH)
        im.paste(ImageOps.fit(Image.open(src).convert("RGB"), (CW, CH), centering=(0.5, 0.3)), (x, y))
        label = f"{i + 1}  {ko}"
        d.text((x + (CW - d.textlength(label, font=f)) / 2, y + CH + 34), label, fill=(70, 70, 70), font=f)
        for dst in (ch, c["drive"]):
            shutil.copy(src, dst / f"{i + 1}_{ko}.png")
    for dst in (ch, c["drive"]):
        im.save(dst / f"{c['name']}_모델 북.png")
        shutil.copy(p / c["ref"], dst / "0_기준 얼굴.png")
    (ch / "identity.txt").write_text(c["identity"] + "\n\n" + c["wardrobe"], encoding="utf-8")
    print(c["drive"] / f"{c['name']}_모델 북.png")


if __name__ == "__main__":
    c, cmd = CHARS[sys.argv[1]], sys.argv[2]
    {"prompts": lambda: prompts(c), "gen": lambda: gen(c, set(sys.argv[3:])), "card": lambda: card(c)}[cmd]()
