from __future__ import annotations

import html
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date

from bs4 import BeautifulSoup


BASE = os.path.dirname(os.path.abspath(__file__))
TARGET_PEOPLE = ["박주상", "주영모", "김병걸", "김현석", "김성현", "배유민", "박장미", "김도현", "유찬", "황지환", "송유림"]


@dataclass(frozen=True)
class ProjectRule:
    name: str
    difficulty: float
    people: float
    members: str
    note: str = ""


CAREERS = {
    "박주상": (20.0, "20년", 4.6, "고난도 업무 주도, 리스크 사전 대응, 팀 내 기준 제시"),
    "김병걸": (20.0, "20년", 4.6, "안정적 수행, 문제 해결 주도, 후배 지원"),
    "주영모": (15.0, "15년", 4.3, "복잡한 업무 조율, 품질 관리, 개선 제안"),
    "김현석": (14.0, "14년", 4.3, "독립적 업무 수행, 주요 이슈 해결, 일정·품질 책임"),
    "송유림": (8.0, "8년", 4.0, "휴직 상태인 경우 평가 보류"),
    "김성현": (5.0, "5년", 3.8, "담당 업무 완결성, 성장성, 일정 준수"),
    "배유민": (3.0, "3년", 3.4, "담당 업무 완결성, 실무 숙련도, 문제 대응력"),
    "유찬": (5.0, "5년", 3.8, "담당 기능 완결성, 이슈 대응, 고객사 커뮤니케이션 능력"),
    "박장미": (1.0, "1년", 2.8, "업무 습득 속도, 기본기, 보고·공유 성실성"),
    "황지환": (1.5, "1.5년", 2.9, "기본 업무 정확도, 셋업·현장 대응 성실성, 학습 속도"),
    "김도현": (0.5, "6개월", 2.5, "적응도, 학습 태도, 지시 업무 수행 정확도"),
}


PROJECTS = {
    "TOE 1차 설비": ProjectRule("TOE 1차 설비", 3.0, 1, "배유민"),
    "TOE 2차 설비": ProjectRule("TOE 2차 설비", 4.5, 2, "김현석, 김성현"),
    "TOE CIM": ProjectRule("TOE CIM", 3.5, 1, "김성현"),
    "교육/학습": ProjectRule("교육/학습", 1.0, 1, ""),
    "ETC": ProjectRule("ETC", 2.0, 1, ""),
    "Vision UI/WPF Framework": ProjectRule("Vision UI/WPF Framework", 4.2, 1, "박주상"),
    "AR System": ProjectRule("AR System", 4.5, 2, "송유림, 박장미"),
    "MTP Cell Log": ProjectRule("MTP Cell Log", 3.2, 2, "송유림, 박장미"),
    "SDC LifeTime/MVT System": ProjectRule("SDC LifeTime/MVT System", 3.8, 1, "주영모"),
    "SEC 4종설비 1D/2D": ProjectRule("SEC 4종설비 1D/2D", 3.8, 1, "주영모"),
    "Vision 알고리즘 개발": ProjectRule("Vision 알고리즘 개발", 4.7, 1, "박주상"),
    "WHTM Loader/Unloader System": ProjectRule("WHTM Loader/Unloader System", 4.3, 2, "주영모"),
    "세미나/자료정리": ProjectRule("세미나/자료정리", 2.0, 1, ""),
    "KOPTI Sorter/Prober": ProjectRule("KOPTI Sorter/Prober", 3.8, 1, "주영모"),
    "KOPTI Micro LED 검사 설비": ProjectRule("KOPTI Micro LED 검사 설비", 4.3, 1, "박주상"),
    "LGD ICBSystem": ProjectRule("LGD ICBSystem", 3.9, 2, "주영모, 박장미"),
    "신뢰성 평가 시스템": ProjectRule("신뢰성 평가 시스템", 4.7, 3, "김병걸, 주영모, 박주상"),
    "WHTM ACAControlSystem": ProjectRule("WHTM ACAControlSystem", 4.5, 1, "주영모"),
    "Wafer Passive SPL Test System": ProjectRule("Wafer Passive SPL Test System", 2.0, 1, "배유민"),
    "Multi-Probing Tester": ProjectRule("Multi-Probing Tester", 4.5, 2, "김병걸, 배유민"),
    "CTP": ProjectRule("CTP", 2.5, 1, "박장미"),
    "SDC A2 EMR": ProjectRule("SDC A2 EMR", 3.9, 2, "유찬, 우준성"),
    "아이코디 렌즈검사기 Demo": ProjectRule("아이코디 렌즈검사기 Demo", 2.8, 1, "황지환"),
    "지오메디칼 Sealing 검사": ProjectRule("지오메디칼 Sealing 검사", 2.5, 1, "황지환"),
}


QUAL = {
    "박주상": (0.50, 0.50, 0.20),
    "주영모": (0.45, 0.45, 0.20),
    "김병걸": (0.35, 0.30, 0.20),
    "김현석": (0.50, 0.45, 0.20),
    "김성현": (0.20, -0.10, 0.10),
    "배유민": (0.25, 0.10, 0.10),
    "박장미": (0.25, 0.00, 0.15),
    "김도현": (0.10, -0.20, 0.10),
    "유찬": (0.30, 0.20, 0.15),
    "황지환": (0.20, 0.05, 0.10),
}


def text_of(el) -> str:
    return re.sub(r"\s+", " ", el.get_text("\n", strip=True)).strip()


def find_work_rows(path: str) -> list[list[str]]:
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    best = None
    for table in soup.find_all("table"):
        t = table.get_text(" ", strip=True)
        if "프로젝트" in t and "금주" in t and "내주" in t:
            best = table
    if best is None:
        return []
    rows: list[list[str]] = []
    for tr in best.find_all("tr"):
        cells = [text_of(c) for c in tr.find_all(["th", "td"], recursive=False)]
        if len(cells) >= 3 and any(cells):
            rows.append(cells)
    if rows and "프로젝트" in rows[0][0]:
        rows = rows[1:]
    return rows


def classify(name: str, project: str, body: str) -> str:
    text = f"{project} {body}".lower()
    raw = f"{project} {body}"

    if name == "송유림":
        return "휴직"
    if any(k in raw for k in ["세미나", "세미", "자료 정리", "자료정리", "발표"]):
        return "세미나/자료정리"
    if any(k in raw for k in ["교육", "학습", "인수인계", "코드 분석"]):
        if name in ["김도현", "황지환"]:
            return "교육/학습"

    if any(k in raw for k in ["WPF Framework", "WPF", "Framework", "SmartPlatform", "Vision UI"]):
        if name == "박주상":
            return "Vision UI/WPF Framework"
    if any(k in raw for k in ["RAS Vision", "Vision Part", "Review Part", "픽셀", "Addressing", "불량 판정", "이미지 분석", "매핑"]):
        if name in ["박주상", "김도현"]:
            return "Vision 알고리즘 개발"
    if any(k in raw for k in ["검사 알고리즘", "비전 알고리즘", "알고리즘 개발"]):
        return "Vision 알고리즘 개발"
    if any(k in raw for k in ["Multi-Probing", "EPI-SE1000", "Wafer F/O", "Wafer Map", "Wafer 공용"]):
        return "Multi-Probing Tester"
    if any(k in raw for k in ["Wafer Passive", "SPL Test"]):
        return "Wafer Passive SPL Test System"
    if any(k in raw for k in ["SEC RAS", "신뢰성 평가", "신뢰성 설비", "신뢰성설비", "RAS"]):
        return "신뢰성 평가 시스템"
    if any(k in raw for k in ["TOE CIM", "CIM"]):
        if "TOE" in raw or "ToE" in raw or "toe" in text:
            return "TOE CIM"
    if "TOE" in raw or "ToE" in raw or "toe" in text:
        if any(k in raw for k in ["1호기", "1차", "1차 설비"]):
            return "TOE 1차 설비"
        if any(k in raw for k in ["2호기", "2차", "2차 설비", "신규건"]):
            return "TOE 2차 설비"
        if name in ["김현석", "김성현"]:
            return "TOE 2차 설비"
        return "ETC"
    if any(k in raw for k in ["ACAControlSystem", "G6", "EIP", "AGV"]):
        return "WHTM ACAControlSystem"
    if any(k in raw for k in ["Loader", "Unloader", "G4.5"]):
        return "WHTM Loader/Unloader System"
    if any(k in raw for k in ["AR", "AF", "ND Filter", "PKG", "TSP"]):
        return "AR System"
    if any(k in raw for k in ["ICBSystem", "LG Mobile OLED", "IVL", "PG Control", "Voltage Sweep", "MTP/IVL Test"]):
        if name == "주영모":
            return "LGD ICBSystem"
    if any(k in raw for k in ["MTP", "Cell Log"]):
        return "MTP Cell Log"
    if any(k in raw for k in ["LifeTime", "ICBSystem", "C310V2", "LG Mobile OLED"]):
        if name == "주영모":
            return "LGD ICBSystem"
    if any(k in raw for k in ["MVT", "S6 LifeTime", "SDC LifeTime"]):
        if name == "주영모":
            return "SDC LifeTime/MVT System"
    if any(k in raw for k in ["4종", "1D", "2D", "Flicker", "Image Rotate"]):
        if name == "주영모":
            return "SEC 4종설비 1D/2D"
    if any(k in raw for k in ["KOPTI Mirco LED", "KOPTI Micro LED", "Micro LED 검사", "Mirco LED 검사", "ACS 3축", "Fastech 3축"]):
        if name == "박주상":
            return "KOPTI Micro LED 검사 설비"
    if any(k in raw for k in ["KOPTI", "Sorter", "Prober"]):
        return "KOPTI Sorter/Prober"
    if any(k in raw for k in ["CTP", "점등검사"]):
        return "CTP"
    if any(k in raw for k in ["A2 EMR", "EMR"]):
        return "SDC A2 EMR"
    if any(k in raw for k in ["아이코디", "렌즈검사"]):
        return "아이코디 렌즈검사기 Demo"
    if any(k in raw for k in ["지오메디칼", "Sealing", "실링"]):
        return "지오메디칼 Sealing 검사"
    return "ETC"


def adjusted(rule: ProjectRule) -> float:
    return rule.difficulty - min(0.25 * (rule.people - 1), 0.6)


def clamp(v: float, lo: float = 1.0, hi: float = 5.0) -> float:
    return max(lo, min(hi, v))


def collect():
    rows_by_member: dict[str, list[dict]] = defaultdict(list)
    date_set = set()
    for name in TARGET_PEOPLE:
        folder = os.path.join(BASE, name)
        if not os.path.isdir(folder):
            continue
        for fname in sorted(os.listdir(folder)):
            if not fname.endswith(".html"):
                continue
            report_date = fname[:-5]
            date_set.add(report_date)
            for cells in find_work_rows(os.path.join(folder, fname)):
                project = cells[0] if cells else ""
                body = cells[1] if len(cells) > 1 else ""
                next_plan = cells[3] if len(cells) > 3 else ""
                cls = classify(name, project, body)
                if cls == "휴직":
                    continue
                rule = PROJECTS.get(cls, PROJECTS["ETC"])
                rows_by_member[name].append({
                    "date": report_date,
                    "project_text": project,
                    "body": body,
                    "next_plan": next_plan,
                    "classified": cls,
                    "difficulty": rule.difficulty,
                    "people": rule.people,
                    "adjusted": adjusted(rule),
                })
    return rows_by_member, sorted(date_set)


def build_member_stats(rows_by_member):
    stats = {}
    for name in TARGET_PEOPLE:
        if name == "송유림":
            stats[name] = {"status": "보류", "rows": [], "score": None}
            continue
        rows = rows_by_member.get(name, [])
        row_count = len(rows)
        occurrence_counts = Counter(r["classified"] for r in rows)
        unique_projects = list(occurrence_counts.keys())
        project_count = len(unique_projects)
        avg = sum(adjusted(PROJECTS.get(p, PROJECTS["ETC"])) for p in unique_projects) / project_count if project_count else 0
        career = CAREERS[name]
        gap = avg - career[2]
        perf, lead, collab = QUAL.get(name, (0.0, 0.0, 0.0))
        breadth = min(max(project_count - 1, 0) * 0.05, 0.25)
        workload = min(row_count * 0.01, 0.35)
        raw_score = 3.5 + gap * 0.8 + perf + lead + collab + breadth + workload
        score = clamp(raw_score)
        stats[name] = {
            "status": "평가",
            "rows": rows,
            "counts": Counter({p: 1 for p in unique_projects}),
            "occurrence_counts": occurrence_counts,
            "avg": avg,
            "gap": gap,
            "perf": perf,
            "lead": lead,
            "collab": collab,
            "breadth": breadth,
            "workload": workload,
            "raw_score": raw_score,
            "score": round(score, 1),
            "top_projects": [p for p, _ in occurrence_counts.most_common(4)],
            "count": project_count,
            "row_count": row_count,
        }
    return stats


def esc(v) -> str:
    return html.escape(str(v), quote=True)


def fmt(v: float) -> str:
    return f"{v:.2f}"


def project_table() -> str:
    rows = []
    for name, rule in PROJECTS.items():
        rows.append(f"<tr><td>{esc(name)}</td><td class=\"num\">{rule.difficulty:.1f}</td><td class=\"center\">{rule.people:g}명</td><td>{esc(rule.members)}</td><td class=\"num\">{adjusted(rule):.2f}</td></tr>")
    return "\n".join(rows)


def rank_rows(stats) -> str:
    ranked = sorted(
        [n for n in TARGET_PEOPLE if stats[n]["status"] == "평가"],
        key=lambda n: (-stats[n]["score"], -stats[n]["avg"], n),
    )
    rows = []
    for idx, name in enumerate(ranked, 1):
        s = stats[name]
        career = CAREERS[name]
        rows.append(
            f"<tr><td class=\"center\">{idx}</td><td>{esc(name)}</td><td class=\"center\">{career[1]}</td>"
            f"<td>{esc(', '.join(s['top_projects']) or 'ETC')}</td><td class=\"num\">{s['count']}</td>"
            f"<td class=\"num\">{s['row_count']}</td><td class=\"num\">{fmt(s['breadth'])}</td><td class=\"num\">{fmt(s['workload'])}</td>"
            f"<td class=\"num\">{fmt(s['avg'])}</td><td class=\"num\">{fmt(career[2])}</td>"
            f"<td class=\"num\">{fmt(s['gap'])}</td><td class=\"num score\">{s['score']:.1f}</td></tr>"
        )
    rows.append("<tr><td class=\"center\">-</td><td>송유림</td><td class=\"center\">8년</td><td>휴직</td><td class=\"center\">-</td><td class=\"center\">-</td><td class=\"center\">-</td><td class=\"center\">-</td><td class=\"center\">-</td><td class=\"num\">4.00</td><td class=\"center\">-</td><td class=\"center score\">보류</td></tr>")
    return "\n".join(rows)


def summary_rows(stats, latest_date: str) -> str:
    rows = []
    for name in sorted([n for n in TARGET_PEOPLE if stats[n]["status"] == "평가"], key=lambda n: (-stats[n]["score"], n)):
        s = stats[name]
        rows.append(
            f"<tr><td>{esc(name)}</td><td class=\"num score\">{s['score']:.1f}</td>"
            f"<td>{CAREERS[name][1]}차 기대 난이도 {CAREERS[name][2]:.2f} 대비 보정 평균 난이도 {s['avg']:.2f}. "
            f"주요 분류는 {esc(', '.join(s['top_projects']) or 'ETC')}이며, {esc(latest_date)} 저장분까지 반영했다.</td></tr>"
        )
    rows.append(f"<tr><td>송유림</td><td class=\"center score\">보류</td><td>휴직 상태로 개인 평가는 보류했다. {esc(latest_date)} 결재-완료함에서도 신규 주간업무보고가 확인되지 않았다.</td></tr>")
    return "\n".join(rows)


def detail_panels(stats, latest_date: str) -> tuple[str, str]:
    buttons = []
    panels = []
    first = True
    for name in TARGET_PEOPLE:
        tab = re.sub(r"[^a-zA-Z0-9가-힣]", "", name)
        active = " active" if first else ""
        buttons.append(f"<button class=\"tab-button member-tab-button{active}\" type=\"button\" data-member-tab=\"member-{tab}\">{esc(name)}</button>")
        first = False
        if name == "송유림":
            panels.append(f"""
      <section id=\"member-{tab}\" class=\"member-panel{active}\">
        <h3>{esc(name)} <span class=\"score\">보류</span></h3>
        <table><tbody><tr><td>평가 상태</td><td class=\"center score\">보류</td><td>휴직 상태이므로 최종 점수 산정 제외</td></tr></tbody></table>
      </section>""")
            continue
        s = stats[name]
        project_rows = "\n".join(
            f"<tr><td>{esc(p)}</td><td class=\"num\">1</td><td class=\"num\">{s['occurrence_counts'].get(p, 0)}</td><td class=\"num\">{PROJECTS.get(p, PROJECTS['ETC']).difficulty:.1f}</td><td class=\"num\">{adjusted(PROJECTS.get(p, PROJECTS['ETC'])):.2f}</td></tr>"
            for p, _ in s["occurrence_counts"].most_common()
        )
        recent = [r for r in s["rows"] if r["date"] == latest_date]
        recent_rows = "\n".join(
            f"<tr><td>{esc(r['project_text'])}</td><td>{esc(r['classified'])}</td><td>{esc(r['body'][:160])}</td></tr>"
            for r in recent[:6]
        ) or f"<tr><td colspan=\"3\" class=\"center\">{esc(latest_date)} 저장분 없음</td></tr>"
        panels.append(f"""
      <section id=\"member-{tab}\" class=\"member-panel{active}\">
        <h3>{esc(name)} <span class=\"score\">{s['score']:.1f}</span></h3>
        <table>
          <tbody>
            <tr><td>보고서 업무 행 수</td><td class=\"num\">{s['row_count']}</td><td>{esc(latest_date)} 저장분까지 누적</td></tr>
            <tr><td>동일 프로젝트 통합 수</td><td class=\"num\">{s['count']}</td><td>같은 분류 프로젝트는 1건으로 합산</td></tr>
            <tr><td>개인별 보정 평균 난이도</td><td class=\"num\">{fmt(s['avg'])}</td><td>투입인원 분산 보정 후 평균</td></tr>
            <tr><td>경력 기대 충족도</td><td class=\"num\">{fmt(s['gap'])}</td><td>{fmt(s['avg'])} - {fmt(CAREERS[name][2])}</td></tr>
            <tr><td>정성 보정</td><td class=\"num\">{fmt(s['perf'] + s['lead'] + s['collab'])}</td><td>성과/완료도 {fmt(s['perf'])}, 주도성/책임 {fmt(s['lead'])}, 협업/공유 {fmt(s['collab'])}</td></tr>
            <tr><td>프로젝트 폭 보정</td><td class=\"num\">{fmt(s['breadth'])}</td><td>min(({s['count']} - 1) × 0.05, 0.25)</td></tr>
            <tr><td>업무량 보정</td><td class=\"num\">{fmt(s['workload'])}</td><td>min({s['row_count']} × 0.01, 0.35)</td></tr>
            <tr><td>최종 계산</td><td class=\"num score\">{s['score']:.1f}</td><td>3.5 + ({fmt(s['gap'])} × 0.8) + {fmt(s['perf'])} + {fmt(s['lead'])} + {fmt(s['collab'])} + {fmt(s['breadth'])} + {fmt(s['workload'])} = {fmt(s['raw_score'])}</td></tr>
          </tbody>
        </table>
        <h4>프로젝트 분류 집계</h4>
        <table><thead><tr><th>분류 프로젝트</th><th>통합 프로젝트 수</th><th>원문 업무 행 수</th><th>난이도</th><th>보정 난이도</th></tr></thead><tbody>{project_rows}</tbody></table>
        <h4>{esc(latest_date)} 반영 항목</h4>
        <table><thead><tr><th>원문 프로젝트</th><th>평가 분류</th><th>금주실적 요약</th></tr></thead><tbody>{recent_rows}</tbody></table>
      </section>""")
    return "\n".join(buttons), "\n".join(panels)


def render(stats, dates) -> str:
    latest_date = dates[-1]
    buttons, panels = detail_panels(stats, latest_date)
    report_count = sum(s.get("row_count", 0) for s in stats.values() if isinstance(s.get("row_count", 0), int))
    project_count = sum(s.get("count", 0) for s in stats.values() if isinstance(s.get("count", 0), int))
    return f"""<!DOCTYPE html>
<html lang=\"ko\">
<head>
  <meta charset=\"UTF-8\">
  <title>주간업무 기반 팀원 성과평가 기준 및 결과</title>
  <style>
    body{{font-family:\"맑은 고딕\",\"Malgun Gothic\",Arial,sans-serif;margin:28px;color:#222;font-size:14px;line-height:1.55;background:#f7f8fa}}
    main{{max-width:1320px;margin:0 auto;background:#fff;border:1px solid #d9dde3;padding:28px}}
    h1{{margin:0 0 8px;font-size:24px;color:#17365d}}
    h2{{margin:28px 0 10px;font-size:18px;color:#17365d;border-bottom:2px solid #c8d6ea;padding-bottom:6px}}
    h3{{margin:18px 0 8px;font-size:15px;color:#333}}
    h4{{margin:16px 0 6px;font-size:13px;color:#17365d}}
    .meta{{color:#555;margin-bottom:22px}}
    table{{border-collapse:collapse;width:100%;margin:10px 0 18px;background:#fff}}
    th,td{{border:1px solid #b8c0cc;padding:7px 8px;vertical-align:top}}
    th{{background:#e7f0fb;color:#17365d;text-align:center;font-weight:700}}
    td.num{{text-align:right;white-space:nowrap}}
    td.center{{text-align:center;white-space:nowrap}}
    .note{{background:#fff8e5;border:1px solid #ead59a;padding:10px 12px;margin:12px 0}}
    .formula{{font-family:Consolas,\"Courier New\",monospace;background:#f0f3f7;border:1px solid #cdd5df;padding:10px 12px;white-space:pre-wrap}}
    .small{{font-size:12px;color:#555}}
    .score{{font-weight:700;color:#0b4f8a}}
    .tabs{{display:flex;gap:6px;border-bottom:1px solid #b8c0cc;margin:18px 0 20px;flex-wrap:wrap}}
    .tab-button{{border:1px solid #b8c0cc;border-bottom:none;background:#eef3f8;color:#17365d;padding:9px 16px;font-weight:700;cursor:pointer}}
    .tab-button.active{{background:#17365d;color:#fff}}
    .tab-panel,.member-panel{{display:none}}
    .tab-panel.active,.member-panel.active{{display:block}}
  </style>
</head>
<body>
<main>
  <h1>주간업무 기반 팀원 성과평가 기준 및 결과</h1>
  <div class=\"meta\">
    평가 범위: {esc(dates[0])} ~ {esc(dates[-1])} 누적 주간업무보고<br>
    반영 파일: 팀원별 HTML 보고서 {len(dates)}주차, 업무 행 {report_count}건, 동일 프로젝트 통합 {project_count}건<br>
    분류 기준: 프로젝트 컬럼 제외, 금주실적 본문 기준 세부 프로젝트 분류<br>
    투입인원 기준: 사용자 확정 투입인원 및 같은 프로젝트 그룹 평균 적용<br>
    작성일: {date.today().isoformat()}
  </div>

  <div class=\"tabs\" role=\"tablist\" aria-label=\"평가 문서 탭\">
    <button class=\"tab-button top-tab active\" type=\"button\" data-tab=\"tab-summary\">Summary</button>
    <button class=\"tab-button top-tab\" type=\"button\" data-tab=\"tab-members\">팀원별 세부내역</button>
  </div>

  <section id=\"tab-summary\" class=\"tab-panel active\">
    <h2>1. 평가 원칙</h2>
    <ul>
      <li>프로젝트 컬럼 값은 평가 분류에 사용하지 않고, 금주실적 본문 내용과 세부 설비명, 시스템명, 프로그램명을 우선 반영한다.</li>
      <li>프로젝트 난이도가 높아도 투입인원이 많으면 개인별 부담과 책임이 분산된 것으로 보아 보정한다.</li>
      <li>경력은 가산점이 아니라 연차별 기대 난이도와 책임 수준을 높이는 기준으로 사용한다.</li>
      <li>{esc(latest_date)} 그룹웨어 결재-완료함에서 추출한 최신 주간업무보고까지 포함했다.</li>
      <li>송유림은 휴직 상태로 개인 평가는 보류한다.</li>
    </ul>

    <h2>2. 계산공식</h2>
    <div class=\"formula\">개인평가용 보정 난이도 = 프로젝트 난이도 - min(0.25 × (투입인원 - 1), 0.6)
개인별 보정 평균 난이도 = Σ(보정 난이도 × 해당 프로젝트 건수) / 전체 분류 건수
경력 기대 충족도 = 개인별 보정 평균 난이도 - 경력별 기대 보정 난이도
프로젝트 폭 보정 = min((통합 프로젝트 수 - 1) × 0.05, 0.25)
업무량 보정 = min(원문 업무 행 수 × 0.01, 0.35)
최종 점수 = 3.5 + (경력 기대 충족도 × 0.8) + 성과/완료도 + 주도성/책임 + 협업/공유 + 프로젝트 폭 보정 + 업무량 보정</div>

    <h2>3. 팀원 경력 및 기대 기준</h2>
    <table><thead><tr><th>팀원</th><th>경력</th><th>기대 보정 난이도</th><th>평가 시 기대 기준</th></tr></thead><tbody>
      {''.join(f'<tr><td>{esc(n)}</td><td class=\"center\">{CAREERS[n][1]}</td><td class=\"num\">{CAREERS[n][2]:.2f}</td><td>{esc(CAREERS[n][3])}</td></tr>' for n in TARGET_PEOPLE)}
    </tbody></table>

    <h2>4. 프로젝트별 투입인원, 난이도</h2>
    <table><thead><tr><th>프로젝트</th><th>난이도</th><th>확정 투입인원</th><th>투입자</th><th>개인평가용 보정 난이도</th></tr></thead><tbody>
      {project_table()}
    </tbody></table>

    <h2>5. 팀원별 평가 결과</h2>
    <table><thead><tr><th>순위</th><th>팀원</th><th>경력</th><th>주요 프로젝트</th><th>통합 프로젝트 수</th><th>원문 업무 행 수</th><th>프로젝트 폭 보정</th><th>업무량 보정</th><th>보정 평균 난이도</th><th>기대 난이도</th><th>기대 충족도</th><th>최종 점수</th></tr></thead><tbody>
      {rank_rows(stats)}
    </tbody></table>

    <h2>6. 해석 요약</h2>
    <table><thead><tr><th>팀원</th><th>최종 점수</th><th>해석 요약</th></tr></thead><tbody>
      {summary_rows(stats, latest_date)}
    </tbody></table>
  </section>

  <section id=\"tab-members\" class=\"tab-panel\">
    <h2>팀원별 세부내역</h2>
    <div class=\"note\">각 팀원 탭에는 프로젝트 분류 집계, 경력 기대 충족도, 정성 보정, {esc(latest_date)} 최신 반영 항목을 표시한다.</div>
    <div class=\"tabs member-tabs\" role=\"tablist\" aria-label=\"팀원별 세부내역 탭\">{buttons}</div>
    {panels}
  </section>
</main>
<script>
document.querySelectorAll('.top-tab').forEach(btn=>{{
  btn.addEventListener('click',()=>{{
    document.querySelectorAll('.top-tab').forEach(b=>b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p=>p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.tab).classList.add('active');
  }});
}});
document.querySelectorAll('.member-tab-button').forEach(btn=>{{
  btn.addEventListener('click',()=>{{
    document.querySelectorAll('.member-tab-button').forEach(b=>b.classList.remove('active'));
    document.querySelectorAll('.member-panel').forEach(p=>p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.memberTab).classList.add('active');
  }});
}});
</script>
</body>
</html>
"""


def main():
    rows_by_member, dates = collect()
    stats = build_member_stats(rows_by_member)
    out = render(stats, dates)
    with open(os.path.join(BASE, "evaluation_report.html"), "w", encoding="utf-8", newline="\r\n") as f:
        f.write(out)
    print(f"updated evaluation_report.html: {dates[0]} ~ {dates[-1]}, members={len(TARGET_PEOPLE)}")
    for name in TARGET_PEOPLE:
        s = stats[name]
        if s["status"] == "평가":
            print(f"{name}: score={s['score']:.1f}, avg={s['avg']:.2f}, count={s['count']}")
        else:
            print(f"{name}: 보류")


if __name__ == "__main__":
    main()
