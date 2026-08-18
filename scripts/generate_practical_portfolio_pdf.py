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
    for row in rows:
        cells: list[Paragraph] = []
        for index, value in enumerate(row):
            style = styles["table_key"] if first_col_key and index == 0 else styles["table_body"]
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

    draw_header(c, "04 / CHECKS", "데이터와 런타임을 대조할 항목", "정의된 규칙과 구현을 함께 확인해야 하는 부분입니다.", 5, total)
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
    total = 4
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
    draw_note(c, styles, MARGIN_X, y - 16, CONTENT_W, "정산식", "남은 지급 가능 횟수 = 일일 상한 - 누적 지급. 실제 지급은 이번 배수와 남은 횟수 중 작은 값입니다.")
    draw_table(c, styles, MARGIN_X, y - 88,
        ["누적 지급", "일일 상한", "이번 배수", "실제 지급", "제외"],
        [["8회", "10회", "4회", "2회", "2회"]], [170, 170, 170, 170, 168], first_col_key=False, row_padding=8)
    c.showPage()

    draw_header(c, "03 / DAILY RESET", "일일 초기화와 처리 위치", "스테이지와 보상 상태를 교체하고 전투 시작 시점의 일일 상태로 정산합니다.", 4, total)
    draw_table(c, styles, MARGIN_X, 378,
        ["시점", "처리"],
        [
            ["일일 초기화", "모든 이용자에게 같은 스테이지를 배정하고 보상 상태를 초기화."],
            ["다음 선정", "직전 일자와 같은 스테이지는 연속 배정하지 않음."],
            ["초기화 직전 진입", "종료 시각이 아니라 전투 시작 시점의 일일 상태로 정산."],
        ], [170, 678], row_padding=6.5)
    draw_cards(c, styles, [
        ("클라이언트", "결과 산출", "종료 조건 처리, 누적 피해량 계산, 결과 등급 산출과 전송."),
        ("서버", "상태와 지급", "일일 스테이지 선정, 최고 기록·누적 지급 갱신, 보상 지급."),
        ("확인", "결과 검증", "피해량과 등급의 재계산 또는 전투 기록 대조 여부는 확인되지 않음."),
    ], MARGIN_X, 256, CONTENT_W, columns=3, row_height=116)
    draw_bullets(c, styles, [
        "완료 요청 재전송 시 중복 지급 차단.",
        "최고 기록 갱신 후 누적 지급량 차감.",
        "후보 스테이지가 하나뿐일 때의 선정 규칙.",
    ], MARGIN_X, 113, CONTENT_W)
    c.showPage()


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
            ["편성 제한 목록", "formation_rules", "object[]", "속성과 희귀도 제한을 복수 적용."],
            ["보상 참조값", "first_clear_reward_id<br/>repeat_reward_id", "integer", "최초 보상과 반복 보상을 구분."],
            ["달성 단계별 효과", "mission_effect_id<br/>mission_effect_value", "integer · float", "달성 단계에 대응하는 효과 한 건과 적용값 지정."],
            ["이용자 식별값", "player_uuid", "UUID", "순위 기록과 클리어 편성의 소유자 식별."],
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
        ("표시", "순위 행", "player_uuid, 소속 태그, 도달 층, 턴 수, 클리어 편성."),
    ], MARGIN_X, 246, CONTENT_W, columns=3, row_height=94)
    c.showPage()

    draw_header(c, "04 / RESULT CHECKS", "이상 결과와 추가 확인 항목", "진행 연결과 전투 결과를 확인하고 설정 변경 시 검증 조건을 다시 봅니다.", 5, total)
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
    if not SQUAD_IMAGE.exists():
        raise FileNotFoundError(f"Missing tower UI squad image: {SQUAD_IMAGE}")
    squad_image = ImageReader(str(SQUAD_IMAGE))
    add_cover(
        c,
        "타워 UI",
        "층 진행, 강화 효과와 랭킹 보상 화면 정의",
    )

    draw_header(c, "01 / MAIN SCREEN", "층 진행과 보상 진입", "층 이동, 시즌 상태와 세부 정보 진입 동작을 기본 화면에 배치합니다.", 2, total)
    frame_x, frame_y, frame_w, frame_h = MARGIN_X, 60, CONTENT_W, 320
    c.setFillColor(SURFACE)
    c.setStrokeColor(BORDER)
    c.rect(frame_x, frame_y, frame_w, frame_h, fill=1, stroke=1)
    c.setFillColor(PALE)
    c.rect(frame_x, frame_y + frame_h - 38, frame_w, 38, fill=1, stroke=0)
    c.setFont(FONT_BOLD, 11)
    c.setFillColor(INK)
    c.drawString(frame_x + 14, frame_y + frame_h - 24, "타워")
    c.setFont(FONT_REG, 8.5)
    c.setFillColor(MUTED)
    c.drawRightString(frame_x + frame_w - 14, frame_y + frame_h - 24, "ENTRY ×N  ·  RESOURCE —")

    rail_w = 66
    c.setFillColor(PALE)
    c.rect(frame_x, frame_y, rail_w, frame_h - 38, fill=1, stroke=0)
    rail_items = [
        ("5층", "READY"),
        ("4층", "READY"),
        ("3층", "NOW"),
        ("2층", "CLEAR"),
        ("1층", "CLEAR"),
    ]
    for index, (floor_label, state_label) in enumerate(rail_items):
        active = state_label == "NOW"
        clear = state_label == "CLEAR"
        center_x = frame_x + rail_w / 2
        center_y = frame_y + 238 - index * 46
        c.setFillColor(BLUE if active else SURFACE)
        c.setStrokeColor(BLUE if active or clear else BORDER)
        c.circle(center_x, center_y, 19, fill=1, stroke=1)
        c.setFillColor(BG if active else (BLUE if clear else INK))
        c.setFont(FONT_BOLD, 7.5)
        c.drawCentredString(center_x, center_y + 2, floor_label)
        c.setFont(FONT_REG, 5.4)
        c.drawCentredString(center_x, center_y - 8, state_label)

    main_x = frame_x + rail_w
    main_w = frame_w - rail_w
    tool_y = frame_y + frame_h - 100
    c.setFillColor(PALE)
    c.rect(main_x, tool_y, main_w, 62, fill=1, stroke=0)
    draw_portrait(c, squad_image, 2, main_x + 12, tool_y + 8, 46)
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 9)
    c.drawString(main_x + 68, tool_y + 36, "랭킹 정보")
    c.setFillColor(MUTED)
    c.setFont(FONT_REG, 7.5)
    c.drawString(main_x + 68, tool_y + 20, "RANK INFO")
    draw_ui_label(c, "랭킹 보상", main_x + 225, tool_y + 9, 112)
    draw_ui_label(c, "구매 보상", main_x + 347, tool_y + 9, 112)

    effect_x = main_x + 16
    effect_y = frame_y + 83
    effect_w = 350
    c.setFillColor(PALE)
    c.rect(effect_x, effect_y, effect_w, 120, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 9)
    c.drawString(effect_x + 14, effect_y + 96, "타워 강화 효과")
    node_floors = ("1층", "2층", "3층", "4층")
    for index, label in enumerate(("★", "☆", "☆", "☆")):
        node_x = effect_x + 50 + index * 82
        c.setStrokeColor(BLUE if index == 0 else BORDER)
        c.setFillColor(BLUE if index == 0 else SURFACE)
        c.circle(node_x, effect_y + 53, 27, fill=1, stroke=1)
        c.setFillColor(BG if index == 0 else MUTED)
        c.setFont(FONT_BOLD, 13)
        c.drawCentredString(node_x, effect_y + 55, label)
        c.setFont(FONT_REG, 6.8)
        c.drawCentredString(node_x, effect_y + 40, node_floors[index])

    panel_x = effect_x + effect_w + 16
    panel_w = frame_x + frame_w - panel_x - 16
    c.setFillColor(PALE)
    c.rect(panel_x, effect_y, panel_w, 120, fill=1, stroke=0)
    c.setFillColor(MUTED)
    c.setFont(FONT_REG, 8)
    c.drawString(panel_x + 14, effect_y + 94, "시즌 획득 한도")
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 15)
    c.drawString(panel_x + 14, effect_y + 68, "REWARD_STATUS")
    c.setFillColor(SURFACE)
    c.rect(panel_x + 14, effect_y + 47, panel_w - 28, 7, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.rect(panel_x + 14, effect_y + 47, (panel_w - 28) * 0.62, 7, fill=1, stroke=0)
    c.setFillColor(MUTED)
    c.setFont(FONT_REG, 7.5)
    c.drawString(panel_x + 14, effect_y + 25, "현재 층  3층")
    c.drawRightString(panel_x + panel_w - 14, effect_y + 25, "REWARD_SET")
    c.setFillColor(MUTED)
    c.setFont(FONT_REG, 7.5)
    c.drawString(main_x + 16, frame_y + 49, "SEASON_REMAINING")
    draw_ui_label(c, "반복 전투", frame_x + frame_w - 286, frame_y + 22, 128)
    draw_ui_label(c, "다음 층 도전", frame_x + frame_w - 148, frame_y + 22, 128, active=True)
    c.showPage()

    draw_header(c, "02 / EFFECT POPUP", "타워 강화 효과", "효과 단계, 적용 내용, 획득 조건과 달성 상태를 표시합니다.", 3, total)
    panel_x, panel_y, panel_w, panel_h = 132, 62, 696, 318
    c.setFillColor(SURFACE)
    c.setStrokeColor(BORDER)
    c.rect(panel_x, panel_y, panel_w, panel_h, fill=1, stroke=1)
    c.setFillColor(PALE)
    c.rect(panel_x, panel_y + panel_h - 38, panel_w, 38, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 11)
    c.drawString(panel_x + 14, panel_y + panel_h - 24, "타워 강화 효과")
    c.setFillColor(MUTED)
    c.setFont(FONT_REG, 8)
    c.drawRightString(panel_x + panel_w - 14, panel_y + panel_h - 24, "CLOSE")
    c.setFillColor(SURFACE)
    c.setStrokeColor(BLUE)
    c.rect(panel_x + 18, panel_y + 207, 74, 58, fill=1, stroke=1)
    c.setFillColor(BLUE)
    c.setFont(FONT_BOLD, 22)
    c.drawCentredString(panel_x + 55, panel_y + 228, "★")
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 12)
    c.drawString(panel_x + 108, panel_y + 244, "EFFECT_NAME")
    c.setFillColor(MUTED)
    c.setFont(FONT_REG, 8)
    c.drawString(panel_x + 108, panel_y + 222, "EFFECT_DESCRIPTION")
    draw_table(c, styles, panel_x + 18, panel_y + 190,
        ["단계", "효과", "획득 조건", "상태"],
        [
            ["★", "EFFECT_VALUE_A", "1층", "ACTIVE"],
            ["★★", "EFFECT_VALUE_B", "2층", "NOT_ACQUIRED"],
            ["★★★", "EFFECT_VALUE_C", "3층", "NOT_ACQUIRED"],
        ], [72, 216, 188, 184], row_padding=5.5)
    c.setFillColor(MUTED)
    c.setFont(FONT_REG, 8)
    c.drawString(panel_x + 18, panel_y + 26, "미완료 단계: 재도전  ·  완료 단계: 전체 획득")
    draw_ui_label(c, "재도전", panel_x + panel_w - 134, panel_y + 14, 116, active=True)
    c.showPage()

    draw_header(c, "03 / RANK REWARD", "랭킹 보상", "순위 구간과 구간별 보상 묶음을 팝업으로 표시합니다.", 4, total)
    panel_x, panel_y, panel_w, panel_h = 152, 58, 656, 324
    c.setFillColor(SURFACE)
    c.setStrokeColor(BORDER)
    c.rect(panel_x, panel_y, panel_w, panel_h, fill=1, stroke=1)
    c.setFillColor(PALE)
    c.rect(panel_x, panel_y + panel_h - 38, panel_w, 38, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 11)
    c.drawString(panel_x + 14, panel_y + panel_h - 24, "랭킹 보상")
    c.setFillColor(MUTED)
    c.setFont(FONT_REG, 8)
    c.drawRightString(panel_x + panel_w - 14, panel_y + panel_h - 24, "CLOSE")
    reward_tiers = ("RANK_TOP", "RANK_HIGH", "RANK_MID", "RANK_BASE", "RANK_ALL")
    for index, tier in enumerate(reward_tiers):
        row_y = panel_y + panel_h - 88 - index * 51
        c.setFillColor(PALE if index % 2 == 0 else SURFACE)
        c.rect(panel_x + 14, row_y - 28, panel_w - 28, 42, fill=1, stroke=0)
        c.setFillColor(BLUE if index < 2 else INK)
        c.setFont(FONT_BOLD, 10)
        c.drawString(panel_x + 28, row_y - 6, tier)
        for reward_index, label in enumerate(("REWARD_A × N", "REWARD_B × N")):
            box_x = panel_x + 230 + reward_index * 166
            c.setStrokeColor(BORDER)
            c.setFillColor(SURFACE)
            c.rect(box_x, row_y - 21, 148, 28, fill=1, stroke=1)
            c.setFillColor(MUTED)
            c.setFont(FONT_REG, 7.5)
            c.drawCentredString(box_x + 74, row_y - 10, label)
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
    parser = argparse.ArgumentParser(description="Generate four portfolio PDF documents in two themes.")
    parser.add_argument("output_dir", type=Path, help="Directory for the generated PDFs")
    args = parser.parse_args()
    register_fonts()
    output_dir = args.output_dir.resolve()
    for theme in ("dark", "light"):
        theme_dir = output_dir / theme
        generate_one(theme_dir / "battle-option.pdf", "battle", theme)
        generate_one(theme_dir / "tactics-research.pdf", "tactical", theme)
        generate_one(theme_dir / "tower.pdf", "tower", theme)
        generate_one(theme_dir / "tower-ui.pdf", "tower-ui", theme)


if __name__ == "__main__":
    main()
