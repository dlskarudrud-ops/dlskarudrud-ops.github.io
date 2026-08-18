import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const root = "C:/Project/dlskarudrud-ops.github.io";
const outputDir = path.join(root, "tmp", "pptx-v2-preview");
const panelDir = path.join(root, "assets", "images", "combat-presentation-v2");
const phantomPaths = [1, 2, 3, 4].map((index) => path.join(panelDir, `phantom-${index}.png`));
const statePaths = [1, 2, 3, 4].map((index) => path.join(panelDir, `state-${index}.png`));
const statusPaths = [1, 2, 3, 4].map((index) => path.join(panelDir, `status-${index}.png`));

const COLORS = {
  bg: "#10111A",
  panel: "#171927",
  panel2: "#20233A",
  line: "#4D5274",
  ink: "#F6F2FF",
  muted: "#C3BFD4",
  accent: "#B9A5FF",
  accent2: "#6FD0D3",
};

const FONT = "Noto Sans KR";

async function readBytes(filePath) {
  const bytes = await fs.readFile(filePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

function addRect(slide, name, x, y, w, h, fill = COLORS.panel, line = COLORS.line, lineWidth = 1) {
  return slide.shapes.add({
    geometry: "rect",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: line, width: lineWidth },
  });
}

function addText(slide, name, text, x, y, w, h, size, color = COLORS.ink, bold = false, align = "left") {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontSize: size,
    typeface: FONT,
    bold,
    color,
    alignment: align,
    autoFit: "none",
    verticalAlignment: "middle",
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  };
  return shape;
}

function addCroppedImage(slide, name, bytes, x, y, w, h, alt, fit = "cover") {
  return slide.images.add({
    blob: bytes,
    contentType: "image/png",
    alt,
    fit,
    position: { left: x, top: y, width: w, height: h },
    geometry: "rect",
    name,
  });
}

function addFieldList(slide, fields) {
  const x = 56;
  const y0 = 414;
  const rowH = 44;
  for (let i = 0; i < fields.length; i += 1) {
    const y = y0 + i * rowH;
    addRect(slide, `field-line-${i}`, x, y, 305, 1, COLORS.line, COLORS.line, 0);
    addText(slide, `field-label-${i}`, fields[i][0], x, y + 2, 112, 40, 12, COLORS.muted, false);
    addText(slide, `field-value-${i}`, fields[i][1], x + 118, y + 2, 187, 40, 12, COLORS.ink, true);
  }
  addRect(slide, "field-line-end", x, y0 + fields.length * rowH, 305, 1, COLORS.line, COLORS.line, 0);
}

function addSceneCard(slide, bytes, sceneIndex, title, note, x) {
  addRect(slide, `scene-card-${sceneIndex}`, x, 32, 264, 326, COLORS.panel, COLORS.line, 1);
  addCroppedImage(slide, `scene-image-${sceneIndex}`, bytes, x, 32, 264, 244, title, "cover");
  addRect(slide, `scene-caption-bg-${sceneIndex}`, x, 276, 264, 82, COLORS.panel2, COLORS.line, 0);
  addText(slide, `scene-title-${sceneIndex}`, title, x + 14, 286, 236, 26, 15, COLORS.accent, true);
  addText(slide, `scene-note-${sceneIndex}`, note, x + 14, 312, 236, 40, 12, COLORS.muted, false);
}

function addSequence(slide, label, steps) {
  addRect(slide, "sequence-panel", 410, 374, 838, 314, COLORS.panel, COLORS.line, 1);
  addText(slide, "sequence-title", label, 432, 394, 300, 36, 20, COLORS.ink, true);
  addText(slide, "sequence-order", "01 → 02 → 03", 1084, 400, 138, 24, 10, COLORS.muted, false, "right");
  for (let i = 0; i < steps.length; i += 1) {
    const x = 434 + i * 266;
    addRect(slide, `step-card-${i}`, x, 446, 244, 214, COLORS.panel2, COLORS.panel2, 0);
    addRect(slide, `step-accent-${i}`, x, 446, 5, 214, COLORS.accent, COLORS.accent, 0);
    addText(slide, `step-title-${i}`, `0${i + 1} · ${steps[i][0]}`, x + 20, 462, 204, 54, 12, COLORS.accent, true);
    addText(slide, `step-body-${i}`, steps[i][1], x + 20, 520, 204, 124, 12, COLORS.muted, false);
  }
}

function addSlide(presentation, images, config, pageNo) {
  const slide = presentation.slides.add();
  slide.background.fill = COLORS.bg;
  addRect(slide, "spec-panel", 32, 32, 352, 656, COLORS.panel, COLORS.line, 1);
  addRect(slide, "spec-accent", 32, 32, 5, 656, COLORS.accent, COLORS.accent, 0);
  addText(slide, "kicker", "CHARACTER PRESENTATION", 56, 54, 280, 24, 10, COLORS.accent, true);
  addText(slide, "title", config.title, 56, 82, 290, 58, 34, COLORS.ink, true);
  addText(slide, "subtitle", config.subtitle, 56, 142, 290, 36, 15, COLORS.muted, true);
  addCroppedImage(slide, "character-reference", images[0], 86, 188, 244, 206, "캐릭터 레퍼런스", "contain");
  addFieldList(slide, config.fields);
  addSceneCard(slide, images[1], 1, config.scenes[0][0], config.scenes[0][1], 410);
  addSceneCard(slide, images[2], 2, config.scenes[1][0], config.scenes[1][1], 674);
  addSceneCard(slide, images[3], 3, config.scenes[2][0], config.scenes[2][1], 938);
  addSequence(slide, config.sequenceLabel, config.steps);
  addText(slide, "page-number", `${String(pageNo).padStart(2, "0")} / 03`, 1156, 690, 92, 18, 10, COLORS.muted, true, "right");
  return slide;
}

async function main() {
  await fs.mkdir(outputDir, { recursive: true });
  const phantomBytes = await Promise.all(phantomPaths.map(readBytes));
  const stateBytes = await Promise.all(statePaths.map(readBytes));
  const statusBytes = await Promise.all(statusPaths.map(readBytes));
  const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });

  addSlide(presentation, phantomBytes, {
    title: "캐릭터 연출",
    subtitle: "이기어검 · 환영검 방출",
    fields: [
      ["동작 유형", "제자리 공격"],
      ["픽토그래피", "이동 없음 · 원격 검 제어"],
      ["컷씬", "사용 안 함"],
      ["추가 프랍 모델링", "기존 무기 모델링을 그대로 매시만 활용해서 이펙트로 사용"],
      ["애니메이션", "공격 준비 · 제자리 공격 · 대기 복귀"],
      ["이펙트", "영체·연기 효과와 함께 환영검을 방출한다. 검이 대상에게 꽂힌 뒤 1초 후 디졸브되어 사라진다."],
    ],
    scenes: [
      ["01 · 생성", "제자리를 유지하고 손을 들어 영체·연기와 함께 환영검을 생성한다."],
      ["02 · 방출", "한 손을 대상 방향으로 내밀어 이기어검으로 환영검을 방출한다."],
      ["03 · 적중·종료", "환영검이 대상에 꽂히고, 적중 1초 뒤 디졸브되어 사라진다."],
    ],
    sequenceLabel: "텍스트 시퀀스",
    steps: [
      ["Character_skill_ready.anim", "발과 골반을 고정하고 상체 중심을 낮춘다. 손을 들어 올리는 동작의 정점에 영체·연기 효과와 환영검을 생성한다."],
      ["Character_skill_attack.anim", "시선, 팔꿈치, 손끝 순으로 대상 방향을 연다. 손이 완전히 뻗는 프레임에 환영검을 출발시키며 캐릭터의 위치는 유지한다."],
      ["Character_skill_return.anim", "환영검 적중 후 손목과 팔을 회수하고 상체를 중립으로 돌린다. 환영검은 적중 1초 뒤 디졸브하고 대기 모션으로 블렌드한다."],
    ],
  }, 1);

  addSlide(presentation, stateBytes, {
    title: "전투 상태 연출",
    subtitle: "대기 · 자신의 턴 · 사망",
    fields: [
      ["대기 모션", "상체 호흡 루프 · 머리카락과 소매 후행"],
      ["자신의 턴", "시선 전환 · 손짓 · 환영검 생성 · 포즈 고정"],
      ["사망 연출", "상체 붕괴 · 무릎 접지 · 후행 동작 정리"],
      ["컷씬", "사용 안 함"],
      ["추가 프랍 모델링", "기존 무기 모델링의 매시 활용"],
      ["이펙트 종료", "사망 자세 고정 후 환영검과 연기 효과 디졸브"],
    ],
    scenes: [
      ["01 · 대기 모션", "골반과 발을 고정하고 상체 호흡과 후행 흔들림을 루프로 재생한다."],
      ["02 · 자신의 턴", "시선과 상체를 전환한 뒤 손을 들어 환영검 생성 포즈를 잡는다."],
      ["03 · 사망", "상체 붕괴 후 무릎이 닿고, 후행 동작이 끝난 자세를 고정한다."],
    ],
    sequenceLabel: "상태별 시퀀스",
    steps: [
      ["Character_idle.anim", "무게 중심은 골반에 두고 흉곽을 낮게 들고 내린다. 머리카락과 소매는 상체보다 늦게 따라오게 한다."],
      ["Character_Battle_idle.anim", "시선, 어깨, 손 순서로 대상 방향을 잡는다. 손이 정점에 도달하면 환영검과 연기 효과를 생성하고, 짧은 오버슈트 뒤 공격 대기 포즈로 정착한다."],
      ["Character_die_idle.anim", "피격 방향으로 상체가 무너진 뒤 무릎이 바닥에 닿는다. 손과 머리카락의 후행 동작이 끝난 프레임을 유지하고, 그 뒤 환영검과 연기 효과를 디졸브한다."],
    ],
  }, 2);

  addSlide(presentation, statusBytes, {
    title: "상태이상 연출",
    subtitle: "스턴 · 혼란 · 수면",
    fields: [
      ["스턴", "행동 불가 유지 · 상체 경직 · 작은 중심 흔들림"],
      ["혼란", "시선과 몸 방향 불일치 · 좌우 왕복"],
      ["수면", "고개 하강 · 어깨 이완 · 저속 호흡"],
      ["루트 모션", "사용 안 함 · 발 기준점 유지"],
      ["상태 표식", "스턴 궤도 · 혼란 ? · 수면 Zzz"],
      ["전환", "상태 진입·유지·해제를 기본 대기 모션과 블렌드"],
    ],
    scenes: [
      ["01 · 스턴", "발을 고정하고 팔 힘을 뺀 채 머리 위 궤도 표식과 작은 중심 흔들림을 유지한다."],
      ["02 · 혼란", "시선과 몸 방향을 엇갈리게 두고 ? 표식과 좌우 전환을 반복한다."],
      ["03 · 수면", "눈을 감고 고개와 어깨를 내린 자세에서 Zzz 표식과 낮은 호흡을 반복한다."],
    ],
    sequenceLabel: "상태별 시퀀스",
    steps: [
      ["Character_stun_idle.anim", "진입 시 상체와 팔을 짧게 경직한다. 발을 고정한 채 머리와 흉곽을 작은 범위로 흔들고, 해제 시 중심을 세워 대기 모션으로 블렌드한다."],
      ["Character_confusion_idle.anim", "진입 시 시선을 한쪽으로 먼저 돌리고 몸은 반대 방향으로 늦게 전환한다. 좌우 엇갈림을 반복하고, 해제 시 정면 대기 모션으로 블렌드한다."],
      ["Character_sleep_idle.anim", "진입 시 눈을 감고 고개·어깨·팔 순으로 힘을 뺀다. 낮은 흉곽 호흡을 유지하며, 해제 시 고개와 상체를 세워 대기 모션으로 블렌드한다."],
    ],
  }, 3);

  for (const [index, slide] of presentation.slides.items.entries()) {
    const stem = `slide-${index + 1}`;
    await writeBlob(path.join(outputDir, `${stem}.png`), await presentation.export({ slide, format: "png", scale: 1.25 }));
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(path.join(outputDir, `${stem}.layout.json`), await layout.text());
  }
  await writeBlob(path.join(outputDir, "montage.webp"), await presentation.export({ format: "webp", montage: true, scale: 1 }));
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(path.join(outputDir, "combat-presentation.pptx"));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
