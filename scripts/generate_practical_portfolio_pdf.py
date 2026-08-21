from __future__ import annotations

import argparse
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle


PAGE_W = 960
PAGE_H = 540
MARGIN_X = 56
CONTENT_W = PAGE_W - MARGIN_X * 2
SQUAD_IMAGE = Path(__file__).resolve().parents[1] / "assets" / "images" / "tower-ui-original-squad.png"
COMBAT_PHANTOM_IMAGE = Path(__file__).resolve().parents[1] / "assets" / "images" / "combat-presentation-phantom-sword-v2.png"
COMBAT_STATE_IMAGE = Path(__file__).resolve().parents[1] / "assets" / "images" / "combat-presentation-state-v3.png"
COMBAT_STATUS_IMAGE = Path(__file__).resolve().parents[1] / "assets" / "images" / "combat-presentation-status-effect-v2.png"
TOWER_UI_BACKGROUND = Path(__file__).resolve().parents[1] / "assets" / "images" / "tower-ui-background-v1.png"

BG = HexColor("#F5F2EC")
SURFACE = HexColor("#FFFCF7")
PALE = HexColor("#EDE8DF")
PALE_2 = HexColor("#E3DBCF")
INK = HexColor("#24211E")
MUTED = HexColor("#675F55")
BLUE = HexColor("#8F5F20")
BLUE_DARK = HexColor("#79511F")
BORDER = HexColor("#C8BFB2")
WARN = HexColor("#8D4A3F")
WARN_BG = HexColor("#F3E7E2")

FONT_REG = "Malgun"
FONT_BOLD = "MalgunBold"


def set_theme(theme: str) -> None:
    global BG, SURFACE, PALE, PALE_2, INK, MUTED, BLUE, BLUE_DARK, BORDER, WARN, WARN_BG
    if theme == "dark":
        BG = HexColor("#141416")
        SURFACE = HexColor("#1D1E21")
        PALE = HexColor("#25262A")
        PALE_2 = HexColor("#2E2B27")
        INK = HexColor("#F2EDE4")
        MUTED = HexColor("#B4AA9E")
        BLUE = HexColor("#C79A58")
        BLUE_DARK = HexColor("#8C622B")
        BORDER = HexColor("#45423E")
        WARN = HexColor("#D38B7C")
        WARN_BG = HexColor("#332522")
    elif theme == "light":
        BG = HexColor("#F5F2EC")
        SURFACE = HexColor("#FFFCF7")
        PALE = HexColor("#EDE8DF")
        PALE_2 = HexColor("#E3DBCF")
        INK = HexColor("#24211E")
        MUTED = HexColor("#675F55")
        BLUE = HexColor("#8F5F20")
        BLUE_DARK = HexColor("#79511F")
        BORDER = HexColor("#C8BFB2")
        WARN = HexColor("#8D4A3F")
        WARN_BG = HexColor("#F3E7E2")
    else:
        raise ValueError(f"Unknown theme: {theme}")


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont(FONT_REG, r"C:\Windows\Fonts\malgun.ttf"))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, r"C:\Windows\Fonts\malgunbd.ttf"))
    pdfmetrics.registerFontFamily("Malgun", normal=FONT_REG, bold=FONT_BOLD)


def build_styles() -> dict[str, ParagraphStyle]:
    return {
        "table_header": ParagraphStyle(
            "TableHeader", fontName=FONT_BOLD, fontSize=9.5, leading=12,
            textColor=colors.white, alignment=TA_LEFT,
        ),
        "table_body": ParagraphStyle(
            "TableBody", fontName=FONT_REG, fontSize=9.3, leading=13,
            textColor=MUTED, alignment=TA_LEFT,
        ),
        "table_key": ParagraphStyle(
            "TableKey", fontName=FONT_BOLD, fontSize=9.3, leading=13,
            textColor=INK, alignment=TA_LEFT,
        ),
        "table_field": ParagraphStyle(
            "TableField", fontName=FONT_BOLD, fontSize=9.3, leading=13,
            textColor=BLUE, alignment=TA_LEFT,
        ),
        "card_label": ParagraphStyle(
            "CardLabel", fontName=FONT_BOLD, fontSize=8.5, leading=10,
            textColor=BLUE, alignment=TA_LEFT,
        ),
        "card_title": ParagraphStyle(
            "CardTitle", fontName=FONT_BOLD, fontSize=12.5, leading=16,
            textColor=INK, alignment=TA_LEFT,
        ),
        "card_body": ParagraphStyle(
            "CardBody", fontName=FONT_REG, fontSize=9.5, leading=14,
            textColor=MUTED, alignment=TA_LEFT,
        ),
        "note": ParagraphStyle(
            "Note", fontName=FONT_REG, fontSize=9.5, leading=14,
            textColor=MUTED, alignment=TA_LEFT,
        ),
        "bullet": ParagraphStyle(
            "Bullet", fontName=FONT_REG, fontSize=10.5, leading=17,
            leftIndent=12, firstLineIndent=-10, bulletIndent=0,
            textColor=MUTED, alignment=TA_LEFT,
        ),
    }


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def draw_background(c: canvas.Canvas) -> None:
    c.setFillColor(BG)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)


def draw_footer(c: canvas.Canvas, page_no: int, total: int) -> None:
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.7)
    c.line(MARGIN_X, 30, PAGE_W - MARGIN_X, 30)
    c.setFont(FONT_REG, 8.5)
    c.setFillColor(MUTED)
    c.drawString(MARGIN_X, 15, "이남경 · SYSTEM & COMBAT DESIGN")
    c.drawRightString(PAGE_W - MARGIN_X, 15, f"{page_no:02d} / {total:02d}")


def draw_cover(c: canvas.Canvas, title: str, subtitle: str) -> None:
    draw_background(c)
    c.setFont(FONT_BOLD, 10)
    c.setFillColor(BLUE)
    c.drawString(MARGIN_X, 390, "DESIGN DOCUMENT")
    c.setFont(FONT_BOLD, 38)
    c.setFillColor(INK)
    c.drawString(MARGIN_X, 320, title)
    c.setStrokeColor(BLUE)
    c.setLineWidth(2)
    c.line(MARGIN_X, 278, MARGIN_X + 72, 278)
    c.setFont(FONT_REG, 15)
    c.setFillColor(MUTED)
    c.drawString(MARGIN_X, 235, subtitle)


def draw_header(c: canvas.Canvas, label: str, title: str, subtitle: str, page_no: int, total: int) -> None:
    draw_background(c)
    c.setFont(FONT_BOLD, 9.5)
    c.setFillColor(BLUE)
    c.drawString(MARGIN_X, 494, label.upper())
    c.setFont(FONT_BOLD, 27)
    c.setFillColor(INK)
    c.drawString(MARGIN_X, 451, title)
    c.setFont(FONT_REG, 11.5)
    c.setFillColor(MUTED)
    c.drawString(MARGIN_X, 420, subtitle)
    c.setStrokeColor(BLUE)
    c.setLineWidth(1.2)
    c.line(MARGIN_X, 399, PAGE_W - MARGIN_X, 399)
    draw_footer(c, page_no, total)


def draw_table(
    c: canvas.Canvas,
    styles: dict[str, ParagraphStyle],
    x: float,
    y_top: float,
    headers: list[str],
    rows: list[list[str]],
    widths: list[float],
    first_col_key: bool = True,
    row_padding: float = 7,
) -> float:
    data: list[list[Paragraph]] = [
        [paragraph(value, styles["table_header"]) for value in headers]
    ]
    field_column = headers.index("컬럼명") if "컬럼명" in headers else -1
    for row in rows:
        cells: list[Paragraph] = []
        for index, value in enumerate(row):
            if index == field_column:
                style = styles["table_field"]
            elif first_col_key and index == 0:
                style = styles["table_key"]
            else:
                style = styles["table_body"]
            cells.append(paragraph(value, style))
        data.append(cells)

    table = Table(data, colWidths=widths, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_DARK),
        ("BACKGROUND", (0, 1), (-1, -1), SURFACE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [SURFACE, PALE]),
        ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), row_padding),
        ("BOTTOMPADDING", (0, 0), (-1, -1), row_padding),
    ]))
    width, height = table.wrap(sum(widths), PAGE_H)
    bottom = y_top - height
    if bottom < 44:
        raise ValueError(f"Table crosses the footer safety line: {bottom:.1f}")
    table.drawOn(c, x, bottom)
    return bottom


def draw_note(
    c: canvas.Canvas,
    styles: dict[str, ParagraphStyle],
    x: float,
    y_top: float,
    width: float,
    title: str,
    body: str,
    warning: bool = False,
) -> float:
    bg = WARN_BG if warning else PALE_2
    line = WARN if warning else BLUE
    title_color = WARN if warning else BLUE_DARK
    title_p = paragraph(title, ParagraphStyle(
        "InlineNoteTitle", parent=styles["card_title"], fontSize=10.5,
        leading=13, textColor=title_color,
    ))
    body_p = paragraph(body, styles["note"])
    box = Table([[title_p, body_p]], colWidths=[118, width - 118])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0, bg),
        ("LINEBEFORE", (0, 0), (0, 0), 3, line),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    _, height = box.wrap(width, PAGE_H)
    box.drawOn(c, x, y_top - height)
    return y_top - height


def draw_cards(
    c: canvas.Canvas,
    styles: dict[str, ParagraphStyle],
    cards: list[tuple[str, str, str]],
    x: float,
    y_top: float,
    width: float,
    columns: int,
    gap: float = 12,
    row_height: float = 105,
) -> float:
    card_w = (width - gap * (columns - 1)) / columns
    rows = (len(cards) + columns - 1) // columns
    for index, (label, title, body) in enumerate(cards):
        col = index % columns
        row = index // columns
        card_x = x + col * (card_w + gap)
        card_y = y_top - row * (row_height + gap) - row_height
        c.setFillColor(SURFACE)
        c.setStrokeColor(BORDER)
        c.roundRect(card_x, card_y, card_w, row_height, 10, fill=1, stroke=1)
        c.setFillColor(BLUE)
        c.roundRect(card_x, card_y, 4, row_height, 2, fill=1, stroke=0)
        label_p = paragraph(label, styles["card_label"])
        title_p = paragraph(title, styles["card_title"])
        body_p = paragraph(body, styles["card_body"])
        _, label_h = label_p.wrap(card_w - 30, row_height)
        _, title_h = title_p.wrap(card_w - 30, row_height)
        _, body_h = body_p.wrap(card_w - 30, row_height)
        if label_h + title_h + body_h + 34 > row_height:
            raise ValueError(f"Card content overflow: {title}")
        label_p.wrapOn(c, card_w - 30, 20)
        label_p.drawOn(c, card_x + 16, card_y + row_height - 24)
        title_p.wrapOn(c, card_w - 30, 32)
        title_p.drawOn(c, card_x + 16, card_y + row_height - 50)
        body_p.wrapOn(c, card_w - 30, 45)
        body_p.drawOn(c, card_x + 16, card_y + 14)
    return y_top - rows * row_height - (rows - 1) * gap


def draw_bullets(
    c: canvas.Canvas,
    styles: dict[str, ParagraphStyle],
    items: list[str],
    x: float,
    y_top: float,
    width: float,
    line_gap: float = 4,
) -> float:
    y = y_top
    for item in items:
        p = paragraph("• " + item, styles["bullet"])
        _, height = p.wrap(width, 80)
        p.drawOn(c, x, y - height)
        y -= height + line_gap
    return y


def draw_portrait(
    c: canvas.Canvas,
    image: ImageReader,
    quadrant: int,
    x: float,
    y: float,
    size: float,
) -> None:
    """Draw one cell from the generated 2 x 2 portrait sheet."""
    if quadrant not in (1, 2, 3, 4):
        raise ValueError(f"Unknown portrait quadrant: {quadrant}")
    c.saveState()
    clip = c.beginPath()
    clip.rect(x, y, size, size)
    c.clipPath(clip, stroke=0, fill=0)
    draw_x = x if quadrant in (1, 3) else x - size
    draw_y = y - size if quadrant in (1, 2) else y
    c.drawImage(image, draw_x, draw_y, width=size * 2, height=size * 2, preserveAspectRatio=False, mask="auto")
    c.restoreState()
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.7)
    c.rect(x, y, size, size, fill=0, stroke=1)


def draw_ui_label(c: canvas.Canvas, text: str, x: float, y: float, width: float, active: bool = False) -> None:
    c.setFillColor(BLUE if active else SURFACE)
    c.setStrokeColor(BLUE if active else BORDER)
    c.rect(x, y, width, 27, fill=1, stroke=1)
    c.setFillColor(BG if active else MUTED)
    c.setFont(FONT_BOLD if active else FONT_REG, 8.3)
    c.drawCentredString(x + width / 2, y + 9, text)


def add_cover(c: canvas.Canvas, title: str, subtitle: str) -> None:
    draw_cover(c, title, subtitle)
    c.showPage()


def add_battle_pages(c: canvas.Canvas, styles: dict[str, ParagraphStyle]) -> None:
    total = 5
    add_cover(
        c,
        "배틀 옵션",
        "데이터 항목, 입력 예시, 발동 순서와 조합 제한",
    )

    draw_header(c, "01 / DATA FIELDS", "효과 한 건을 구성하는 대표 항목", "스킬과 장비 효과를 같은 레코드 형식으로 기록합니다.", 2, total)
    y = draw_table(c, styles, MARGIN_X, 378,
        ["항목", "컬럼명", "형식", "용도"],
        [
            ["발동 단계", "trigger_timing", "enum", "전투 시작, 턴 시작, 행동 전후, 피격, 사망 등 확인 시점."],
            ["실행 기능", "effect_type", "enum", "공격, 회복, 상태 부여, 수치 보정, 게이지 변경 등 적용 결과."],
            ["대상 규칙", "target_type", "enum", "자신, 아군, 적, 직전 적중 대상 등 후보 선택 기준."],
            ["시전자 조건", "caster_condition", "enum", "효과 보유자의 체력, 상태, 사용 스킬, 공격 결과 조건."],
            ["대상 조건", "target_condition", "enum", "선택 대상의 체력, 상태, 속성, 역할 조건."],
            ["재사용 제한", "cooldown_check", "boolean", "스킬 재사용 대기시간과 함께 검사할지 지정."],
            ["발동 판정", "trigger_rate", "float", "확정, 고정 확률, 명중·회피 반영 확률을 구분."],
            ["기능 인수", "effect_params", "number[]", "지속 턴, 적용 횟수, 계수처럼 기능마다 필요한 값."],
        ], [125, 175, 95, 453], row_padding=5.2)
    c.showPage()

    draw_header(c, "02 / INPUT EXAMPLES", "대표 입력과 호출 순서", "서로 다른 효과를 같은 항목으로 기록하고 전투 상태 처리 뒤 호출합니다.", 3, total)
    y = draw_table(c, styles, MARGIN_X, 379,
        ["발동 단계", "기능", "대상", "조건", "제한", "인수"],
        [
            ["턴 시작 처리 후", "체력 회복", "체력이 낮은 아군", "대상 체력 N% 이하", "적용", "최대 체력 기준 계수"],
            ["공격 계산 중", "피해량 보정", "직전 피격 대상", "특정 상태 보유", "예외", "중첩당 보정 계수"],
            ["피격 처리 후", "지속 회복", "자신", "피격 후 체력 N% 이하", "적용", "지속 턴·회복 계수"],
        ], [145, 115, 140, 180, 78, 190], row_padding=6)
    draw_cards(c, styles, [
        ("01", "기본 처리", "턴 시작 피해와 행동 결과 등 전투 상태를 먼저 반영."),
        ("02", "주체·조건", "공격자, 피격자, 턴 소유자와 조건을 확인."),
        ("03", "대상 선택", "단일 대상과 대상 목록을 발동 단계에 맞춰 구분."),
        ("04", "기능 실행", "발동 판정 뒤 계산 전용 또는 연출 포함 처리."),
    ], MARGIN_X, y - 20, CONTENT_W, columns=4, row_height=108)
    c.showPage()

    draw_header(c, "03 / COMBINATION RULES", "발동 단계와 기능의 조합 제한", "특정 기능은 지정된 단계와 대상 규칙에서만 사용합니다.", 4, total)
    draw_table(c, styles, MARGIN_X, 379,
        ["구분", "작성 규칙", "확인할 오류"],
        [
            ["계산 전용 효과", "별도 연출 없이 계산에만 사용하며 자신을 대상으로 설정.", "연출 중복, 적용 대상 오해."],
            ["직전 적용 대상", "행동·공격 단계는 단일 대상, 그 밖의 단계는 대상 목록을 구분.", "다중 공격의 잘못된 대상 참조."],
            ["협동 공격", "지정된 발동 단계에서만 실행.", "재귀 호출, 행동 순서 충돌."],
            ["후속 스킬", "행동 종료 뒤 별도 단계에서 실행.", "턴 소유권과 종료 판정 충돌."],
            ["지속 피해 면역", "상시 적용 단계에서 사용.", "일시 효과로 잘못 등록."],
            ["효과 복사", "시전자 정보가 필요한 상태는 복사·이동 대상에서 제외.", "보호·도발 관계의 주체 손실."],
        ], [155, 430, 263], row_padding=7)
    c.showPage()

    draw_header(c, "04 / QA", "테스트 케이스(QA)", "입력값과 실행 결과를 함께 확인합니다.", 5, total)
    draw_cards(c, styles, [
        ("입력", "기능 인수", "실행 기능마다 의미와 자료형이 달라 입력 검사가 필요."),
        ("입력", "문자열 추가값", "빈 값, 구분자, 잘못된 열거값 처리 확인."),
        ("단계", "턴 종료", "정의에는 남아 있으나 본문에서는 사용하지 않는 것으로 기록."),
        ("동기화", "명칭 변경", "갱신 기록과 현재 본문의 명칭을 실제 열거값과 대조."),
        ("실행", "연쇄 행동", "협동 공격, 추가 행동, 후속 스킬의 중복·재귀 제한 확인."),
        ("한계", "호출 순서", "조건·대상·확률의 내부 호출 순서는 코드 확인 필요."),
    ], MARGIN_X, 376, CONTENT_W, columns=3, row_height=125)
    draw_note(c, styles, MARGIN_X, 96, CONTENT_W, "확인 범위", "자동 검사 도구와 런타임 내부 호출 순서는 구현 자료 확인이 필요합니다.", warning=True)
    c.showPage()


def add_tactical_pages(c: canvas.Canvas, styles: dict[str, ParagraphStyle]) -> None:
    total = 5
    add_cover(
        c,
        "전술 연구",
        "일일 피해 측정과 보상 정산 규칙",
    )

    draw_header(c, "01 / BATTLE & DATA", "전투 종료와 보상 데이터", "누적 피해량을 기록하고 결과 등급으로 회차 지급량을 결정합니다.", 2, total)
    draw_table(c, styles, MARGIN_X, 378,
        ["전투 항목", "처리"],
        [
            ["진입 비용", "별도 입장 재화를 소모하지 않음."],
            ["도전 횟수", "반복 도전 가능."],
            ["측정값", "전투 종료까지 보스에게 가한 누적 피해량."],
            ["정상 종료", "보스가 설정된 턴에 도달하면 클리어 처리."],
            ["조기 종료", "아군 전멸 또는 게임 내 중도 이탈도 클리어 처리."],
        ], [160, 250], row_padding=6)
    draw_table(c, styles, MARGIN_X + 432, 378,
        ["보상 항목", "컬럼명", "용도"],
        [
            ["보상 등급", "reward_grade", "피해량 기준의 결과 단계."],
            ["등급 도달 기준", "score_threshold", "등급에 필요한 최소 피해량."],
            ["회차 지급 배수", "reward_multiplier", "이번 클리어의 지급 시도 횟수."],
            ["일일 획득 상한", "daily_reward_limit", "해당 일자의 누적 지급 한도."],
        ], [112, 150, 174], row_padding=5.7)
    draw_note(c, styles, MARGIN_X, 95, CONTENT_W, "종료 정책", "앱 종료와 통신 단절 시 완료 정책을 별도로 정의합니다.", warning=True)
    c.showPage()

    draw_header(c, "02 / SETTLEMENT", "최고 기록과 이번 결과를 분리", "일일 상한은 최고 등급, 이번 지급 배수는 현재 도전 등급을 사용합니다.", 3, total)
    y = draw_table(c, styles, MARGIN_X, 378,
        ["계산 대상", "적용 기준"],
        [
            ["일일 획득 상한", "해당 일자의 최고 기록 등급."],
            ["이번 지급 배수", "이번 도전에서 획득한 등급."],
        ], [250, 598], row_padding=8)
    draw_note(c, styles, MARGIN_X, y - 16, CONTENT_W, "정산 규칙", "남은 지급 가능 횟수는 일일 상한에서 누적 지급을 뺀 값입니다. 지급 배수는 반복 플레이를 줄이기 위한 편의 기능입니다.")
    draw_table(c, styles, MARGIN_X, y - 88,
        ["도전", "지급 배수", "진입 전 누적", "실제 지급", "지급 후 누적"],
        [
            ["1회차", "5배수", "0회", "5회", "5회"],
            ["2회차", "5배수", "5회", "5회", "10회"],
            ["추가 재진입", "5배수", "10회", "0회", "10회"],
        ], [170, 170, 170, 170, 168], row_padding=5.5)
    c.showPage()

    draw_header(c, "03 / DAILY RESET", "Daily 초기화와 결과 처리", "서버 업데이트 시점에 일일 상태를 초기화하고 전투 시작 시점을 기준으로 정산합니다.", 4, total)
    draw_table(c, styles, MARGIN_X, 378,
        ["시점", "처리"],
        [
            ["Daily 초기화", "서버 기준 Daily 초기화 업데이트 시점에 일일 상태와 보상 누적값을 초기화."],
            ["초기화 직전 진입", "종료 시각이 아니라 전투 시작 시점의 Daily 상태로 정산."],
        ], [170, 678], row_padding=6.5)
    draw_cards(c, styles, [
        ("클라이언트", "대미지 선계산", "실드 버프가 흡수한 피해는 제외하고 독·출혈 피해는 포함합니다. 계산 결과를 패킷으로 전송합니다."),
        ("서버", "이용자 정보 갱신", "클라이언트의 대미지 결과 패킷을 받아 최고 기록과 누적 지급 상태를 갱신하고 보상을 지급합니다."),
    ], MARGIN_X, 260, CONTENT_W, columns=2, row_height=132)
    draw_note(c, styles, MARGIN_X, 108, CONTENT_W, "처리 순서", "클라이언트 대미지 선계산 → 결과 패킷 전송 → 서버 이용자 정보 갱신.")
    c.showPage()

    draw_header(c, "04 / QA", "테스트 케이스(QA)", "결과 패킷과 지급 상태를 검증합니다.", 5, total)
    draw_table(c, styles, MARGIN_X, 378,
        ["검사", "판정"],
        [
            ["deck_id가 비어 있는가", "캐릭터를 편성하지 않은 상태에서는 클리어할 수 없으므로 유효하지 않은 결과로 처리."],
            ["turn_count가 0인가", "0턴 클리어는 존재할 수 없으므로 유효하지 않은 결과로 처리."],
            ["같은 완료 요청이 재전송되는가", "이미 반영한 요청은 중복 지급하지 않음."],
            ["최고 기록으로 상한이 증가했는가", "기존 누적 지급량을 차감한 남은 횟수만 지급."],
            ["Daily 초기화 직전에 진입했는가", "전투 시작 시점의 일일 상태로 정산."],
        ], [270, 578], row_padding=6.5)
    c.showPage()


def draw_combat_slide(
    c: canvas.Canvas,
    styles: dict[str, ParagraphStyle],
    sheet: ImageReader,
    page_no: int,
    title: str,
    subtitle: str,
    fields: list[tuple[str, str]],
    scene_titles: tuple[str, str, str],
    scene_notes: tuple[str, str, str],
    sequence_label: str,
    sequence: tuple[tuple[str, str], tuple[str, str], tuple[str, str]],
) -> None:
    font_title = 26
    font_heading = 14
    font_sub = 11.5
    font_body = 12
    font_meta = 7.5
    draw_background(c)
    margin = 24
    gap = 14
    left_x, left_y, left_w, left_h = margin, margin, 272, PAGE_H - margin * 2
    right_x = left_x + left_w + gap
    right_w = PAGE_W - right_x - margin
    scene_y, scene_h = 264, PAGE_H - margin - 264
    sequence_y, sequence_h = margin, scene_y - gap - margin

    c.setFillColor(SURFACE)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.8)
    c.rect(left_x, left_y, left_w, left_h, fill=1, stroke=1)
    c.setFillColor(BLUE)
    c.setFont(FONT_BOLD, font_meta)
    c.drawString(left_x + 18, left_y + left_h - 24, "CHARACTER PRESENTATION")
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, font_title)
    c.drawString(left_x + 18, left_y + left_h - 61, title)
    c.setFillColor(MUTED)
    c.setFont(FONT_BOLD, font_sub)
    c.drawString(left_x + 18, left_y + left_h - 85, subtitle)

    portrait_size = 122
    draw_portrait(c, sheet, 1, left_x + (left_w - portrait_size) / 2, left_y + 266, portrait_size)

    value_style = ParagraphStyle(
        "CombatFieldValue", parent=styles["table_body"], fontName=FONT_BOLD,
        fontSize=font_body, leading=14, textColor=INK,
    )
    field_top = left_y + 252
    remaining_height = field_top - (left_y + 14)
    row_heights: list[float] = []
    value_paragraphs: list[Paragraph] = []
    for _, value in fields:
        value_p = paragraph(value, value_style)
        _, value_h = value_p.wrap(158, remaining_height)
        value_paragraphs.append(value_p)
        row_heights.append(max(22, value_h + 6))
    total_rows = sum(row_heights)
    if total_rows > remaining_height:
        raise ValueError(f"Combat field list crosses slide boundary: {title}")
    current_top = field_top
    for (label, _), value_p, row_h in zip(fields, value_paragraphs, row_heights):
        row_bottom = current_top - row_h
        c.setStrokeColor(BORDER)
        c.line(left_x + 18, current_top, left_x + left_w - 18, current_top)
        c.setFillColor(MUTED)
        c.setFont(FONT_REG, font_meta)
        c.drawString(left_x + 18, row_bottom + row_h / 2 - 2, label)
        value_p.wrapOn(c, 158, row_h - 4)
        _, value_h = value_p.wrap(158, row_h - 4)
        value_p.drawOn(c, left_x + 96, row_bottom + (row_h - value_h) / 2)
        current_top = row_bottom
    c.line(left_x + 18, current_top, left_x + left_w - 18, current_top)

    scene_w = (right_w - gap * 2) / 3
    for index, (scene_title, scene_note) in enumerate(zip(scene_titles, scene_notes)):
        x = right_x + index * (scene_w + gap)
        c.setFillColor(SURFACE)
        c.setStrokeColor(BORDER)
        c.rect(x, scene_y, scene_w, scene_h, fill=1, stroke=1)
        caption_h = 96
        image_size = scene_h - caption_h
        image_x = x + (scene_w - image_size) / 2
        draw_portrait(c, sheet, index + 2, image_x, scene_y + caption_h, image_size)
        c.setFillColor(PALE)
        c.rect(x, scene_y, scene_w, caption_h, fill=1, stroke=0)
        c.setFillColor(BLUE)
        c.setFont(FONT_BOLD, font_sub)
        c.drawString(x + 12, scene_y + caption_h - 22, scene_title)
        note_p = paragraph(scene_note, ParagraphStyle(
            f"CombatSceneNote{page_no}{index}", parent=styles["card_body"],
            fontSize=font_body, leading=14.5, textColor=MUTED,
        ))
        _, note_h = note_p.wrap(scene_w - 24, caption_h - 38)
        if note_h > caption_h - 38:
            raise ValueError(f"Combat scene note overlaps title: {scene_title}")
        note_p.drawOn(c, x + 12, scene_y + caption_h - 35 - note_h)

    c.setFillColor(SURFACE)
    c.setStrokeColor(BORDER)
    c.rect(right_x, sequence_y, right_w, sequence_h, fill=1, stroke=1)
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, font_heading)
    c.drawString(right_x + 18, sequence_y + sequence_h - 30, sequence_label)
    c.setFillColor(MUTED)
    c.setFont(FONT_REG, font_meta)
    c.drawRightString(right_x + right_w - 18, sequence_y + sequence_h - 28, "01 → 02 → 03")

    step_gap = 12
    step_w = (right_w - 36 - step_gap * 2) / 3
    step_y = sequence_y + 22
    step_h = sequence_h - 68
    for index, (step_title, step_body) in enumerate(sequence):
        x = right_x + 18 + index * (step_w + step_gap)
        c.setFillColor(PALE)
        c.rect(x, step_y, step_w, step_h, fill=1, stroke=0)
        c.setFillColor(BLUE)
        c.rect(x, step_y, 4, step_h, fill=1, stroke=0)
        title_text = f"0{index + 1} · {step_title}"
        title_size = font_body
        while title_size > 8 and c.stringWidth(title_text, FONT_BOLD, title_size) > step_w - 28:
            title_size -= 0.5
        c.setFont(FONT_BOLD, title_size)
        c.drawString(x + 14, step_y + step_h - 24, title_text)
        body_p = paragraph(step_body, ParagraphStyle(
            f"CombatStep{page_no}{index}", parent=styles["card_body"],
            fontSize=font_body, leading=15, textColor=MUTED,
        ))
        _, body_h = body_p.wrap(step_w - 28, step_h - 52)
        if body_h > step_h - 52:
            raise ValueError(f"Combat sequence copy crosses card boundary: {step_title}")
        body_p.drawOn(c, x + 14, step_y + step_h - 48 - body_h)

    c.setFillColor(MUTED)
    c.setFont(FONT_BOLD, font_meta)
    c.drawRightString(PAGE_W - 28, 10, f"{page_no:02d} / 03")
    c.showPage()


def add_combat_presentation_pages(c: canvas.Canvas, styles: dict[str, ParagraphStyle]) -> None:
    for path in (COMBAT_PHANTOM_IMAGE, COMBAT_STATE_IMAGE, COMBAT_STATUS_IMAGE):
        if not path.exists():
            raise FileNotFoundError(f"Missing combat presentation image: {path}")
    phantom_sheet = ImageReader(str(COMBAT_PHANTOM_IMAGE))
    state_sheet = ImageReader(str(COMBAT_STATE_IMAGE))
    status_sheet = ImageReader(str(COMBAT_STATUS_IMAGE))

    draw_combat_slide(
        c, styles, phantom_sheet, 1, "캐릭터 연출", "이기어검 · 환영검 방출",
        [
            ("동작 유형", "제자리 공격"),
            ("픽토그래피", "이동 없음 · 원격 검 제어"),
            ("컷씬", "사용 안 함"),
            ("추가 프랍 모델링", "기존 무기 모델링을 그대로 매시만 활용해서 이펙트로 사용"),
            ("애니메이션", "공격 준비 · 제자리 공격 · 대기 복귀"),
            ("이펙트", "영체·연기 효과와 함께 환영검을 방출한다. 검이 대상에게 꽂힌 뒤 1초 후 디졸브되어 사라진다."),
        ],
        ("01 · 생성", "02 · 방출", "03 · 적중·종료"),
        (
            "제자리를 유지하고 손을 들어 영체·연기와 함께 환영검을 생성한다.",
            "한 손을 대상 방향으로 내밀어 이기어검으로 환영검을 방출한다.",
            "환영검이 대상에 꽂히고, 적중 1초 뒤 디졸브되어 사라진다.",
        ),
        "텍스트 시퀀스",
        (
            ("Character_skill_ready.anim", "발과 골반을 고정하고 상체 중심을 낮춘다. 손을 들어 올리는 동작의 정점에 영체·연기 효과와 환영검을 생성한다."),
            ("Character_skill_attack.anim", "시선, 팔꿈치, 손끝 순으로 대상 방향을 연다. 손이 완전히 뻗는 프레임에 환영검을 출발시키며 캐릭터의 위치는 유지한다."),
            ("Character_skill_return.anim", "환영검 적중 후 손목과 팔을 회수하고 상체를 중립으로 돌린다. 환영검은 적중 1초 뒤 디졸브하고 대기 모션으로 블렌드한다."),
        ),
    )

    draw_combat_slide(
        c, styles, state_sheet, 2, "전투 상태 연출", "대기 · 자신의 턴 · 사망",
        [
            ("대기 모션", "상체 호흡 루프 · 머리카락과 소매 후행"),
            ("자신의 턴", "시선 전환 · 손짓 · 환영검 생성 · 포즈 고정"),
            ("사망 연출", "상체 붕괴 · 무릎 접지 · 후행 동작 정리"),
            ("컷씬", "사용 안 함"),
            ("추가 프랍 모델링", "기존 무기 모델링의 매시 활용"),
            ("이펙트 종료", "사망 자세 고정 후 환영검과 연기 효과 디졸브"),
        ],
        ("01 · 대기 모션", "02 · 자신의 턴", "03 · 사망"),
        (
            "골반과 발을 고정하고 상체 호흡과 후행 흔들림을 루프로 재생한다.",
            "시선과 상체를 전환한 뒤 손을 들어 환영검 생성 포즈를 잡는다.",
            "상체 붕괴 후 무릎이 닿고, 후행 동작이 끝난 자세를 고정한다.",
        ),
        "상태별 시퀀스",
        (
            ("Character_idle.anim", "무게 중심은 골반에 두고 흉곽을 낮게 들고 내린다. 머리카락과 소매는 상체보다 늦게 따라오게 한다."),
            ("Character_Battle_idle.anim", "시선, 어깨, 손 순서로 대상 방향을 잡는다. 손이 정점에 도달하면 환영검과 연기 효과를 생성하고, 짧은 오버슈트 뒤 공격 대기 포즈로 정착한다."),
            ("Character_die_idle.anim", "피격 방향으로 상체가 무너진 뒤 무릎이 바닥에 닿는다. 손과 머리카락의 후행 동작이 끝난 프레임을 유지하고, 그 뒤 환영검과 연기 효과를 디졸브한다."),
        ),
    )

    draw_combat_slide(
        c, styles, status_sheet, 3, "상태이상 연출", "스턴 · 혼란 · 수면",
        [
            ("스턴", "행동 불가 유지 · 상체 경직 · 작은 중심 흔들림"),
            ("혼란", "시선과 몸 방향 불일치 · 좌우 왕복"),
            ("수면", "고개 하강 · 어깨 이완 · 저속 호흡"),
            ("루트 모션", "사용 안 함 · 발 기준점 유지"),
            ("상태 표식", "스턴 궤도 · 혼란 ? · 수면 Zzz"),
            ("전환", "상태 진입·유지·해제를 기본 대기 모션과 블렌드"),
        ],
        ("01 · 스턴", "02 · 혼란", "03 · 수면"),
        (
            "발을 고정하고 팔 힘을 뺀 채 머리 위 궤도 표식과 작은 중심 흔들림을 유지한다.",
            "시선과 몸 방향을 엇갈리게 두고 ? 표식과 좌우 전환을 반복한다.",
            "눈을 감고 고개와 어깨를 내린 자세에서 Zzz 표식과 낮은 호흡을 반복한다.",
        ),
        "상태별 시퀀스",
        (
            ("Character_stun_idle.anim", "진입 시 상체와 팔을 짧게 경직한다. 발을 고정한 채 머리와 흉곽을 작은 범위로 흔들고, 해제 시 중심을 세워 대기 모션으로 블렌드한다."),
            ("Character_confusion_idle.anim", "진입 시 시선을 한쪽으로 먼저 돌리고 몸은 반대 방향으로 늦게 전환한다. 좌우 엇갈림을 반복하고, 해제 시 정면 대기 모션으로 블렌드한다."),
            ("Character_sleep_idle.anim", "진입 시 눈을 감고 고개·어깨·팔 순으로 힘을 뺀다. 낮은 흉곽 호흡을 유지하며, 해제 시 고개와 상체를 세워 대기 모션으로 블렌드한다."),
        ),
    )


def add_tower_pages(c: canvas.Canvas, styles: dict[str, ParagraphStyle]) -> None:
    total = 5
    add_cover(
        c,
        "타워",
        "층 진행, 보상, 미션, 순위와 초기화 규칙",
    )

    draw_header(c, "01 / PROGRESSION", "진행과 재도전 경로", "현재 진행 상태에 따라 입장 가능한 층과 지급 항목을 구분합니다.", 2, total)
    y = draw_table(c, styles, MARGIN_X, 378,
        ["구분", "대상 층", "처리"],
        [
            ["진행", "다음 미클리어 층", "최초 보상과 반복 보상 지급, 진행 상태 갱신."],
            ["재도전", "가장 최근 클리어 층", "반복 보상 지급."],
            ["미션", "이미 클리어한 미션 층", "달성하지 못한 층 목표 재도전."],
            ["입장 불가", "그 밖의 일반 클리어 층", "진행 경로와 반복 보상 지점 제한."],
        ], [130, 220, 498], row_padding=7)
    draw_cards(c, styles, [
        ("입장", "전용 재화", "전투 진입 시 지정된 입장 재화를 사용."),
        ("편성", "복수 제한", "속성과 희귀도 조건을 함께 적용 가능."),
        ("연동", "상품 노출", "특정 층 클리어 상태를 노출 조건으로 사용 가능."),
    ], MARGIN_X, y - 20, CONTENT_W, columns=3, row_height=108)
    c.showPage()

    draw_header(c, "02 / DATA & REWARD", "대표 데이터 항목과 지급 규칙", "층 연결, 편성 제한, 최초·반복 보상과 미션 효과를 구분합니다.", 3, total)
    y = draw_table(c, styles, MARGIN_X, 378,
        ["항목", "컬럼명", "형식", "용도"],
        [
            ["층 참조값", "stage_ref_id", "integer", "미션 효과가 적용되는 층 지정."],
            ["진행 연결값", "next_stage_id", "integer", "선행 층과 다음 층의 관계 확인."],
            ["편성 제한 목록", "formation_rules", "integer", "속성과 희귀도 제한값을 '/' 구분자로 복수 입력."],
            ["보상 참조값", "first_clear_reward_id<br/>repeat_reward_id", "integer", "최초 보상과 반복 보상을 구분."],
            ["달성 단계별 효과", "mission_effect_id<br/>mission_effect_value", "integer · float", "달성 단계에 대응하는 효과 한 건과 적용값 지정."],
        ], [130, 180, 120, 418], row_padding=5.2)
    draw_cards(c, styles, [
        ("최초", "다음 층 클리어", "최초 보상과 반복 보상을 함께 지급."),
        ("반복", "최근 층 재도전", "반복 보상만 지급하고 월간 상한 확인."),
        ("미션", "달성 단계", "해당 단계 효과 한 건만 적용하고 하위 효과는 누적하지 않음."),
        ("상한", "초과분", "남은 수량까지만 지급하고 초과분은 제외."),
    ], MARGIN_X, min(188, y - 16), CONTENT_W, columns=4, row_height=105)
    c.showPage()

    draw_header(c, "03 / RANK & RESET", "순위 판정과 월간 초기화", "클리어 직후 기록을 비교하고 월간 경계에서 진행 상태를 교체합니다.", 4, total)
    draw_table(c, styles, MARGIN_X, 378,
        ["순서", "비교 기준", "우선 기록"],
        [["1", "도달 층", "더 높은 층."], ["2", "클리어 턴 수", "더 적은 턴."], ["3", "기록 시각", "먼저 생성된 기록."]],
        [120, 300, 428], row_padding=7)
    draw_cards(c, styles, [
        ("초기화", "진행 기록", "층 진행과 클리어 기록을 초기화."),
        ("초기화", "보상 상태", "전용 재료 수량과 미션 보상 상태를 초기화."),
        ("초기화", "순위·구매", "순위 상태와 관련 구매 기록을 초기화."),
        ("이전 시즌", "순위 보상", "이전 시즌 결과를 정한 뒤 다음 화면 진입 시 지급."),
        ("경계", "전투 시작 시점", "초기화 전 시작한 전투는 이전 시즌 기준으로 정산."),
        ("표시", "순위 행", "이용자명은 UUID로 익명 표시. 소속 태그, 도달 층, 턴 수, 클리어 편성."),
    ], MARGIN_X, 246, CONTENT_W, columns=3, row_height=94)
    c.showPage()

    draw_header(c, "04 / QA", "테스트 케이스(QA)", "진행 연결과 전투 결과를 확인하고 설정 변경 시 검증 조건을 다시 봅니다.", 5, total)
    y = draw_table(c, styles, MARGIN_X, 378,
        ["항목", "현재 처리", "추가 확인"],
        [
            ["층 건너뛰기", "선행 층과 다음 층 관계를 서버에서 확인.", "동시 완료 요청의 순서 처리."],
            ["0턴 클리어", "문서 작성 시점에는 성립하지 않는 결과.", "전투 시작 효과 추가 시 조건 재검토."],
            ["빈 편성", "유닛 없이 클리어한 결과를 비정상 처리.", "시작 편성과 결과 편성의 일치."],
            ["미션 결과", "전달받은 달성 단계에 따라 효과 적용.", "서버 재검증 방식은 확인되지 않음."],
        ], [150, 390, 308], row_padding=7)
    draw_note(c, styles, MARGIN_X, y - 16, CONTENT_W, "보상 상한", "상한 검사는 반복 보상 위치를 대상으로 합니다. 다른 보상 위치에 같은 재료를 넣을 때는 검사 범위를 다시 확인해야 합니다.", warning=True)
    draw_note(c, styles, MARGIN_X, 104, CONTENT_W, "시즌 보상", "화면 진입 시 지급하는 이전 시즌 보상은 미접속, 재접속, 중복 요청을 구분하는 지급 상태가 필요합니다.")
    c.showPage()


def add_tower_ui_pages(c: canvas.Canvas, styles: dict[str, ParagraphStyle]) -> None:
    total = 5
    for path in (SQUAD_IMAGE, TOWER_UI_BACKGROUND):
        if not path.exists():
            raise FileNotFoundError(f"Missing tower UI image: {path}")
    squad_image = ImageReader(str(SQUAD_IMAGE))
    tower_background = ImageReader(str(TOWER_UI_BACKGROUND))

    ui_bg = HexColor("#111629")
    ui_panel = HexColor("#151C36")
    ui_panel_2 = HexColor("#202A4A")
    ui_ink = HexColor("#F4F5FF")
    ui_muted = HexColor("#B7BFD8")
    ui_line = HexColor("#64708E")
    ui_gold = HexColor("#D2B46D")
    ui_cyan = HexColor("#73C1D2")
    ui_pink = HexColor("#D66C91")

    def alpha_rect(color: colors.Color, x: float, y: float, w: float, h: float, alpha: float) -> None:
        c.saveState()
        c.setFillColor(color)
        c.setFillAlpha(alpha)
        c.rect(x, y, w, h, fill=1, stroke=0)
        c.restoreState()

    def cut_panel(x: float, y: float, w: float, h: float, fill: colors.Color = ui_panel) -> None:
        cut = 14
        path = c.beginPath()
        path.moveTo(x + cut, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h - cut)
        path.lineTo(x + w - cut, y + h)
        path.lineTo(x, y + h)
        path.lineTo(x, y + cut)
        path.close()
        c.setFillColor(fill)
        c.setStrokeColor(ui_line)
        c.setLineWidth(1.2)
        c.drawPath(path, fill=1, stroke=1)
        c.setStrokeColor(ui_gold)
        c.setLineWidth(2)
        c.line(x + 18, y + h - 6, x + 78, y + h - 6)
        c.line(x + w - 78, y + 6, x + w - 18, y + 6)

    def draw_floor_rail() -> None:
        alpha_rect(ui_bg, 0, 0, 82, PAGE_H - 44, 0.94)
        c.setStrokeColor(ui_line)
        c.setLineWidth(0.8)
        c.line(82, 0, 82, PAGE_H - 44)
        c.setFillColor(ui_muted)
        c.setFont(FONT_BOLD, 18)
        c.drawCentredString(41, 464, "⌃")
        rail_items = [("17층", "READY"), ("16층", "READY"), ("15층", "NOW"), ("14층", "CLEAR"), ("13층", "CLEAR")]
        for index, (floor_label, state_label) in enumerate(rail_items):
            active = state_label == "NOW"
            clear = state_label == "CLEAR"
            cy = 406 - index * 76
            c.setFillColor(ui_gold if active else ui_panel_2)
            c.setStrokeColor(ui_gold if active or clear else ui_line)
            c.setLineWidth(2 if active else 1)
            c.circle(41, cy, 27, fill=1, stroke=1)
            c.setStrokeColor(ui_ink if active else ui_line)
            c.circle(41, cy, 21, fill=0, stroke=1)
            c.setFillColor(ui_bg if active else (ui_cyan if clear else ui_muted))
            c.setFont(FONT_BOLD, 8.2)
            c.drawCentredString(41, cy + 3, floor_label)
            c.setFont(FONT_BOLD, 5.5)
            c.drawCentredString(41, cy - 9, state_label)
        c.setFillColor(ui_muted)
        c.setFont(FONT_BOLD, 18)
        c.drawCentredString(41, 16, "⌄")

    def draw_game_base(dim: float = 0.26) -> None:
        c.drawImage(tower_background, 0, 0, width=PAGE_W, height=PAGE_H, preserveAspectRatio=False, mask="auto")
        alpha_rect(ui_bg, 0, 0, PAGE_W, PAGE_H, dim)
        alpha_rect(ui_bg, 0, PAGE_H - 44, PAGE_W, 44, 0.94)
        c.setStrokeColor(ui_line)
        c.setLineWidth(0.8)
        c.line(0, PAGE_H - 44, PAGE_W, PAGE_H - 44)
        c.setFillColor(ui_ink)
        c.setFont(FONT_BOLD, 22)
        c.drawString(23, PAGE_H - 29, "‹")
        c.setFont(FONT_BOLD, 13)
        c.drawString(68, PAGE_H - 28, "타워")
        c.setFillColor(ui_muted)
        c.setFont(FONT_BOLD, 7.5)
        c.drawRightString(PAGE_W - 18, PAGE_H - 27, "TOWER / SEASON")
        draw_floor_rail()

    def draw_node(cx: float, cy: float, stage: str, floor: str, active: bool = False) -> None:
        radius = 34
        points = []
        for px, py in ((0, radius), (29, 17), (29, -17), (0, -radius), (-29, -17), (-29, 17)):
            points.append((cx + px, cy + py))
        path = c.beginPath()
        path.moveTo(*points[0])
        for point in points[1:]:
            path.lineTo(*point)
        path.close()
        c.setFillColor(ui_gold if active else ui_panel_2)
        c.setStrokeColor(ui_gold if active else ui_line)
        c.setLineWidth(2)
        c.drawPath(path, fill=1, stroke=1)
        c.setFillColor(ui_bg if active else ui_ink)
        c.setFont(FONT_BOLD, 8.5)
        c.drawCentredString(cx, cy + 4, stage)
        c.setFont(FONT_BOLD, 7.3)
        c.drawCentredString(cx, cy - 10, floor)

    add_cover(
        c,
        "타워 UI",
        "층 진행, 강화 효과와 랭킹 보상 화면 정의",
    )

    draw_game_base()
    cut_panel(104, 330, 230, 142)
    draw_portrait(c, squad_image, 2, 118, 356, 88)
    c.setFillColor(ui_ink)
    c.setFont(FONT_BOLD, 13)
    c.drawString(220, 426, "랭킹 정보")
    c.setFillColor(ui_muted)
    c.setFont(FONT_REG, 7.8)
    c.drawString(220, 409, "최고 도달 층 · 편성")
    for index, label in enumerate(("랭킹 보상", "구매 보상")):
        x = 104 + index * 116
        cut_panel(x, 274, 108, 46, ui_panel_2)
        c.setFillColor(ui_gold if index == 0 else ui_cyan)
        c.circle(x + 18, 297, 8, fill=0, stroke=1)
        c.setFillColor(ui_ink)
        c.setFont(FONT_BOLD, 8.5)
        c.drawString(x + 34, 294, label)

    cut_panel(606, 312, 318, 146)
    c.setFillColor(ui_muted)
    c.setFont(FONT_BOLD, 8)
    c.drawString(626, 432, "기간 내 최대 획득 수량")
    c.setFillColor(ui_ink)
    c.setFont(FONT_BOLD, 14)
    c.drawString(626, 404, "REWARD_A × N")
    c.setFillColor(ui_panel_2)
    c.rect(626, 383, 270, 9, fill=1, stroke=0)
    c.setFillColor(ui_gold)
    c.rect(626, 383, 168, 9, fill=1, stroke=0)
    c.setFillColor(ui_ink)
    c.setFont(FONT_BOLD, 10)
    c.drawString(626, 354, "총 달성 정보")
    c.setFillColor(ui_muted)
    c.setFont(FONT_REG, 8)
    c.drawString(626, 334, "현재 층  15층")
    c.drawRightString(896, 334, "반복 보상  REWARD_A × N")

    alpha_rect(ui_bg, 100, 54, 430, 142, 0.82)
    c.setFillColor(ui_ink)
    c.setFont(FONT_BOLD, 11)
    c.drawString(114, 173, "타워 강화 효과")
    c.setStrokeColor(ui_gold)
    c.setLineWidth(2)
    c.line(152, 111, 478, 111)
    floors = ("10층", "20층", "30층", "40층")
    for index, stage in enumerate(("1단계", "2단계", "3단계", "4단계")):
        draw_node(160 + index * 104, 111, stage, floors[index], active=index == 0)

    c.setFillColor(ui_muted)
    c.setFont(FONT_BOLD, 7.5)
    c.drawRightString(918, 94, "초기화까지 남은 시간")
    for index, (label, color) in enumerate((("반복 전투", ui_cyan), ("다음 층 도전", ui_pink))):
        x = 610 + index * 158
        cut_panel(x, 34, 148, 48, ui_panel)
        c.setStrokeColor(color)
        c.setLineWidth(2)
        c.line(x + 8, 35, x + 140, 35)
        c.setFillColor(color)
        c.setFont(FONT_BOLD, 10)
        c.drawCentredString(x + 74, 53, label)
    c.showPage()

    draw_game_base(0.7)
    panel_x, panel_y, panel_w, panel_h = 166, 72, 644, 384
    cut_panel(panel_x, panel_y, panel_w, panel_h)
    c.setFillColor(ui_panel_2)
    c.rect(panel_x + 2, panel_y + panel_h - 48, panel_w - 4, 46, fill=1, stroke=0)
    c.setFillColor(ui_ink)
    c.setFont(FONT_BOLD, 14)
    c.drawString(panel_x + 24, panel_y + panel_h - 31, "타워 강화 효과")
    c.setFillColor(ui_muted)
    c.setFont(FONT_BOLD, 9)
    c.drawRightString(panel_x + panel_w - 22, panel_y + panel_h - 31, "닫기  ×")

    badge_x, badge_y = panel_x + 65, panel_y + 278
    draw_node(badge_x, badge_y, "강화", "효과", active=True)
    c.setFillColor(ui_ink)
    c.setFont(FONT_BOLD, 15)
    c.drawString(panel_x + 118, panel_y + 294, "EFFECT_NAME")
    c.setFillColor(ui_muted)
    c.setFont(FONT_REG, 8.5)
    c.drawString(panel_x + 118, panel_y + 274, "EFFECT_DESCRIPTION")

    header_y = panel_y + 226
    c.setFillColor(ui_panel_2)
    c.rect(panel_x + 20, header_y, panel_w - 40, 30, fill=1, stroke=0)
    columns = (panel_x + 34, panel_x + 130, panel_x + 356, panel_x + 484)
    for x, label in zip(columns, ("단계", "효과", "획득 조건", "상태")):
        c.setFillColor(ui_muted)
        c.setFont(FONT_BOLD, 7.5)
        c.drawString(x, header_y + 10, label)
    rows = [
        ("1단계", "EFFECT_VALUE_A", "10층", "적용 중"),
        ("2단계", "EFFECT_VALUE_B", "20층", "미획득"),
        ("3단계", "EFFECT_VALUE_C", "30층", "미획득"),
        ("4단계", "EFFECT_VALUE_D", "40층", "미획득"),
    ]
    for index, row in enumerate(rows):
        y = header_y - (index + 1) * 38
        if index == 0:
            alpha_rect(ui_gold, panel_x + 20, y, panel_w - 40, 36, 0.12)
            c.setFillColor(ui_gold)
            c.rect(panel_x + 20, y, 4, 36, fill=1, stroke=0)
        c.setStrokeColor(ui_line)
        c.setLineWidth(0.5)
        c.line(panel_x + 20, y, panel_x + panel_w - 20, y)
        for x, value in zip(columns, row):
            c.setFillColor(ui_gold if index == 0 else ui_ink)
            c.setFont(FONT_BOLD if index == 0 else FONT_REG, 8.5)
            c.drawString(x, y + 13, value)
    c.setFillColor(ui_muted)
    c.setFont(FONT_REG, 8)
    c.drawString(panel_x + 24, panel_y + 22, "20층 클리어 시 다음 효과 획득")
    cut_panel(panel_x + panel_w - 132, panel_y + 12, 108, 34, ui_panel_2)
    c.setFillColor(ui_gold)
    c.setFont(FONT_BOLD, 9)
    c.drawCentredString(panel_x + panel_w - 78, panel_y + 25, "재도전")
    c.showPage()

    draw_game_base(0.72)
    panel_x, panel_y, panel_w, panel_h = 188, 56, 584, 418
    cut_panel(panel_x, panel_y, panel_w, panel_h)
    c.setFillColor(ui_panel_2)
    c.rect(panel_x + 2, panel_y + panel_h - 48, panel_w - 4, 46, fill=1, stroke=0)
    c.setFillColor(ui_ink)
    c.setFont(FONT_BOLD, 14)
    c.drawString(panel_x + 24, panel_y + panel_h - 31, "랭킹 보상")
    c.setFillColor(ui_muted)
    c.setFont(FONT_BOLD, 9)
    c.drawRightString(panel_x + panel_w - 22, panel_y + panel_h - 31, "닫기  ×")
    reward_tiers = ("Rank_1", "Rank_2", "Rank_3", "Rank_4", "Rank_All")
    tier_colors = (HexColor("#E7A342"), HexColor("#B98CF2"), HexColor("#86A7F2"), ui_muted, ui_muted)
    list_top = panel_y + panel_h - 62
    for index, (tier, tier_color) in enumerate(zip(reward_tiers, tier_colors)):
        row_y = list_top - (index + 1) * 63
        c.setFillColor(ui_panel_2 if index % 2 == 0 else ui_panel)
        c.setStrokeColor(ui_line)
        c.rect(panel_x + 18, row_y, panel_w - 52, 54, fill=1, stroke=1)
        c.setFillColor(tier_color)
        band = c.beginPath()
        band.moveTo(panel_x + 18, row_y)
        band.lineTo(panel_x + 124, row_y)
        band.lineTo(panel_x + 146, row_y + 54)
        band.lineTo(panel_x + 18, row_y + 54)
        band.close()
        c.drawPath(band, fill=1, stroke=0)
        c.setFillColor(ui_bg if index < 3 else ui_ink)
        c.setFont(FONT_BOLD, 11)
        c.drawString(panel_x + 32, row_y + 20, tier)
        for reward_index, label in enumerate(("REWARD_A × N", "REWARD_B × N")):
            box_x = panel_x + 172 + reward_index * 170
            c.setFillColor(ui_bg)
            c.setStrokeColor(ui_line)
            c.rect(box_x, row_y + 10, 154, 34, fill=1, stroke=1)
            c.setFillColor(ui_gold if reward_index == 0 else ui_cyan)
            c.circle(box_x + 18, row_y + 27, 7, fill=1, stroke=0)
            c.setFillColor(ui_ink)
            c.setFont(FONT_BOLD, 7.7)
            c.drawString(box_x + 32, row_y + 24, label)
    track_x = panel_x + panel_w - 22
    c.setFillColor(ui_line)
    c.rect(track_x, panel_y + 28, 5, panel_h - 94, fill=1, stroke=0)
    c.setFillColor(ui_gold)
    c.rect(track_x, panel_y + panel_h - 170, 5, 82, fill=1, stroke=0)
    c.setFillColor(ui_muted)
    c.setFont(FONT_REG, 7.5)
    c.drawString(panel_x + 20, panel_y + 16, "순위 구간별 보상 묶음")
    c.showPage()

    draw_header(c, "04 / DISPLAY RULES", "화면 상태와 문자열 키", "기본 화면과 두 팝업에 필요한 표시 항목만 정리합니다.", 5, total)
    draw_table(c, styles, MARGIN_X, 378,
        ["표시 항목", "사용 위치"],
        [
            ["화면 상태", "기본, 강화 효과 팝업, 랭킹 보상 팝업 전환."],
            ["선택 층", "층 선택과 상세 정보 동기화."],
            ["시즌 종료 시각", "시즌 남은 시간 계산."],
            ["강화 효과 상태", "미획득, 획득, 적용 중 단계 표시."],
            ["랭킹 보상 그룹", "순위 구간과 보상 묶음 표시."],
            ["도전 상태", "반복 전투와 다음 층 도전 버튼."],
        ], [145, 265], row_padding=4.8)
    draw_table(c, styles, MARGIN_X + 432, 378,
        ["문자열 키", "용어"],
        [
            ["ui_tower_title", "타워"],
            ["ui_tower_floor_label", "현재 층"],
            ["ui_tower_rank_info_open", "랭킹 정보"],
            ["ui_tower_rank_reward_open", "랭킹 보상"],
            ["ui_tower_shop_reward_open", "구매 보상"],
            ["ui_tower_season_remaining", "초기화까지 남은 시간"],
            ["ui_tower_repeat", "반복 전투"],
            ["ui_tower_next_attempt", "다음 층 도전"],
            ["ui_tower_effect_open", "타워 강화 효과"],
            ["ui_tower_effect_retry", "재도전"],
            ["ui_tower_effect_complete", "타워 효과 전부 획득"],
        ], [225, 211], row_padding=3.5)
    c.showPage()


def generate_one(output_path: Path, kind: str, theme: str) -> None:
    set_theme(theme)
    styles = build_styles()
    titles = {
        "battle": ("배틀 옵션", "전투 효과 데이터의 대표 항목과 처리 규칙"),
        "combat-presentation": ("캐릭터 연출", "이기어검 제자리 공격, 전투 상태와 상태이상 연출"),
        "tactical": ("전술 연구", "일일 피해 측정과 보상 정산 규칙"),
        "tower": ("타워", "층 진행, 보상, 순위와 초기화 규칙"),
        "tower-ui": ("타워 UI", "층 진행, 강화 효과와 랭킹 보상 화면 정의"),
    }
    title, subject = titles[kind]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output_path), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle(title)
    c.setAuthor("이남경")
    c.setSubject(subject)
    c.setKeywords("게임 기획, 전투 데이터, 콘텐츠 규칙")
    if kind == "battle":
        add_battle_pages(c, styles)
    elif kind == "combat-presentation":
        add_combat_presentation_pages(c, styles)
    elif kind == "tactical":
        add_tactical_pages(c, styles)
    elif kind == "tower":
        add_tower_pages(c, styles)
    elif kind == "tower-ui":
        add_tower_ui_pages(c, styles)
    else:
        raise ValueError(f"Unknown document kind: {kind}")
    c.save()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate five portfolio PDF documents in two themes.")
    parser.add_argument("output_dir", type=Path, help="Directory for the generated PDFs")
    args = parser.parse_args()
    register_fonts()
    output_dir = args.output_dir.resolve()
    for theme in ("dark", "light"):
        theme_dir = output_dir / theme
        generate_one(theme_dir / "battle-option.pdf", "battle", theme)
        generate_one(theme_dir / "combat-presentation.pdf", "combat-presentation", theme)
        generate_one(theme_dir / "tactics-research.pdf", "tactical", theme)
        generate_one(theme_dir / "tower.pdf", "tower", theme)
        generate_one(theme_dir / "tower-ui.pdf", "tower-ui", theme)


if __name__ == "__main__":
    main()
