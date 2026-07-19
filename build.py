from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "events.json").read_text(encoding="utf-8"))
EVENTS = DATA["events"]

CATEGORY_SLUGS = {
    "الرواتب": "salaries",
    "التعليم": "education",
    "المناسبات الوطنية": "national",
    "المناسبات الإسلامية": "islamic",
    "الفصول": "seasons",
    "أخرى": "other",
}

def esc(value: str) -> str:
    return (str(value).replace("\\", "\\\\").replace("\n", "\\n")
            .replace(",", "\\,").replace(";", "\\;"))

def fold(line: str, limit: int = 73) -> list[str]:
    # RFC-style folding by Unicode characters; safe and broadly compatible.
    if len(line) <= limit:
        return [line]
    out = [line[:limit]]
    rest = line[limit:]
    while rest:
        out.append(" " + rest[:limit-1])
        rest = rest[limit-1:]
    return out

def build_calendar(events, name, description):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Saudi Calendar//Saudi Calendar 3.0//AR",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{esc(name)}",
        f"X-WR-CALDESC:{esc(description)}",
        "X-WR-TIMEZONE:Asia/Riyadh",
        "REFRESH-INTERVAL;VALUE=DURATION:PT6H",
        "X-PUBLISHED-TTL:PT6H",
    ]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for e in events:
        start = e["date"].replace("-", "")
        end = e.get("endDate", "").replace("-", "")
        if not end:
            dt = datetime.strptime(e["date"], "%Y-%m-%d")
            end = (dt.replace(tzinfo=timezone.utc)).strftime("%Y%m%d")
        certainty_ar = {"confirmed": "مؤكد", "scheduled": "مجدول", "expected": "متوقع"}[e["certainty"]]
        summary = f'{e.get("emoji","")} {e["title"]}'.strip()
        description_lines = [
            e.get("description", "").strip(),
            f'التصنيف: {e["category"]}',
            f'الحالة: {certainty_ar}',
            f'المصدر المرجعي: {e.get("source","الجهة الرسمية المختصة")}',
            "تنبيه: هذا تقويم مستقل، وعند التعارض يُعتمد إعلان الجهة الرسمية المختصة.",
            "الموقع: https://saudi-calendar.saudivip0o.workers.dev",
        ]
        lines += [
            "BEGIN:VEVENT",
            f'UID:{esc(e["uid"])}',
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{start}",
            f"DTEND;VALUE=DATE:{end}",
            f"SUMMARY:{esc(summary)}",
            f'DESCRIPTION:{esc(chr(10).join(x for x in description_lines if x))}',
            f'CATEGORIES:{esc(e["category"])}',
            f'STATUS:{e.get("status","CONFIRMED")}',
            "TRANSP:TRANSPARENT",
        ]
        if e.get("alarm"):
            lines += [
                "BEGIN:VALARM",
                f'TRIGGER:{e["alarm"]}',
                "ACTION:DISPLAY",
                f"DESCRIPTION:{esc(summary)}",
                "END:VALARM",
            ]
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    folded = []
    for line in lines:
        folded.extend(fold(line))
    return "\r\n".join(folded) + "\r\n"

dist = ROOT
(dist / "saudi-calendar.ics").write_text(
    build_calendar(EVENTS, "🇸🇦 التقويم السعودي", "التقويم السعودي الشامل للمواعيد المهمة."),
    encoding="utf-8", newline=""
)

for category, slug in CATEGORY_SLUGS.items():
    subset = [e for e in EVENTS if e["category"] == category]
    if subset:
        (dist / f"{slug}.ics").write_text(
            build_calendar(subset, f"التقويم السعودي — {category}", f"مواعيد {category} من التقويم السعودي."),
            encoding="utf-8", newline=""
        )

print(f"Built {len(EVENTS)} events and {len(list(dist.glob('*.ics')))} calendar files.")
