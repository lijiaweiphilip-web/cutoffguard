"""Render the current deterministic demo report as a small public PNG preview."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from cutoffguard.demo import run_demo


def _font(
    size: int, bold: bool = False
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def main() -> int:
    report = run_demo()
    image = Image.new("RGB", (1200, 760), "#f7f9fc")
    draw = ImageDraw.Draw(image)
    title = _font(34, bold=True)
    heading = _font(22, bold=True)
    body = _font(18)
    small = _font(15)
    draw.text((54, 42), "CutoffGuard", fill="#172033", font=title)
    status_color = {"pass": "#166534", "review": "#92400e", "fail": "#991b1b"}[
        report.status
    ]
    draw.rounded_rectangle(
        (55, 102, 210, 148),
        radius=20,
        fill="#fee2e2" if report.status == "fail" else "#dcfce7",
    )
    draw.text((78, 114), report.status.upper(), fill=status_color, font=heading)
    draw.rounded_rectangle(
        (54, 180, 1146, 270), radius=12, outline="#d9deea", width=2, fill="#ffffff"
    )
    draw.text(
        (78, 201), f"Cutoff: {report.cutoff.isoformat()}", fill="#172033", font=body
    )
    draw.text(
        (78, 235),
        f"Checked records: {report.checked_records}",
        fill="#172033",
        font=body,
    )
    draw.rounded_rectangle(
        (54, 298, 1146, 515), radius=12, outline="#d9deea", width=2, fill="#ffffff"
    )
    draw.text((78, 320), "Findings", fill="#172033", font=heading)
    y = 370
    for finding in report.findings:
        draw.text(
            (80, y),
            f"{finding.code}  |  {finding.record_id}  |  {finding.severity}",
            fill="#172033",
            font=body,
        )
        draw.text((80, y + 28), finding.message, fill="#475467", font=small)
        y += 62
    draw.rounded_rectangle(
        (54, 545, 1146, 690), radius=12, outline="#d9deea", width=2, fill="#ffffff"
    )
    draw.text((78, 565), "Assurance boundary", fill="#172033", font=heading)
    boundary = "Findings are limited to declared metadata and implemented checks;"
    draw.text((78, 610), boundary, fill="#475467", font=small)
    draw.text(
        (78, 637),
        "the report does not establish arbitrary hidden behavior is leakage-free.",
        fill="#475467",
        font=small,
    )
    target = Path(__file__).parents[1] / "docs" / "assets" / "report-example.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, format="PNG", optimize=True)
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
