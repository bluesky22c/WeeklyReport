# -*- coding: utf-8 -*-
import os

BASE = r'D:\Temp\주간업무정리'
SKIP = set()

# ── 공통: 깊이 추적으로 첫 번째 완전한 <table> 추출 ──────────────
def extract_first_table(html_frag):
    lower = html_frag.lower()
    start = lower.find('<table')
    if start == -1:
        return None
    depth = 0
    pos = start
    while pos < len(html_frag):
        nxt_o = lower.find('<table', pos)
        nxt_c = lower.find('</table>', pos)
        if nxt_c == -1:
            break
        if nxt_o != -1 and nxt_o < nxt_c:
            depth += 1; pos = nxt_o + 6
        else:
            depth -= 1
            if depth == 0:
                return html_frag[start:nxt_c + 8]
            pos = nxt_c + 8
    return None

# ── 케이스 1: formid= 속성이 있는 파일 ────────────────────────────
def extract_by_formid(html):
    lower = html.lower()
    idx = lower.find('formid=')
    if idx == -1:
        return None
    td_start = lower.rfind('<td', 0, idx)
    if td_start == -1:
        return None
    tag_end = html.find('>', td_start)
    if tag_end == -1:
        return None
    pos = tag_end + 1
    depth = 1
    while depth > 0 and pos < len(html):
        nxt_o = lower.find('<td', pos)
        nxt_c = lower.find('</td>', pos)
        if nxt_c == -1:
            break
        if nxt_o != -1 and nxt_o < nxt_c:
            depth += 1; pos = nxt_o + 3
        else:
            depth -= 1
            if depth == 0:
                return extract_first_table(html[tag_end+1:nxt_c])
            pos = nxt_c + 5
    return None

# ── 케이스 2: 속성 제거된 파일 → colspan="3" td 에서 추출 ─────────
def extract_by_colspan3(html):
    lower = html.lower()
    # rowspan/colspan 만 남아있으므로 <td rowspan="1" colspan="3"> 패턴
    patterns = [
        '<td rowspan="1" colspan="3">',
        '<td colspan="3" rowspan="1">',
        '<td colspan="3">',
    ]
    td_start = -1
    for pat in patterns:
        idx = lower.find(pat)
        if idx != -1:
            td_start = idx
            break
    if td_start == -1:
        return None
    tag_end = html.find('>', td_start)
    if tag_end == -1:
        return None
    pos = tag_end + 1
    depth = 1
    while depth > 0 and pos < len(html):
        nxt_o = lower.find('<td', pos)
        nxt_c = lower.find('</td>', pos)
        if nxt_c == -1:
            break
        if nxt_o != -1 and nxt_o < nxt_c:
            depth += 1; pos = nxt_o + 3
        else:
            depth -= 1
            if depth == 0:
                return extract_first_table(html[tag_end+1:nxt_c])
            pos = nxt_c + 5
    return None

def has_form_header(html):
    """아직 폼 헤더가 남아있는지 확인"""
    keywords = ['작성자', '결재', '참조']
    return sum(1 for k in keywords if k in html) >= 2

def extract_work_table(html):
    if 'formid=' in html.lower():
        return extract_by_formid(html)
    else:
        return extract_by_colspan3(html)

def html_template(name, date, table_html):
    return (
        f'<!DOCTYPE html>\n<html lang="ko"><head><meta charset="UTF-8">\n'
        f'<title>{name} - 주간업무보고 ({date})</title>\n'
        '<style>\n'
        "body{font-family:'맑은 고딕',sans-serif;margin:20px;font-size:12px}\n"
        'table{border-collapse:collapse;width:100%}\n'
        'td,th{border:1px solid #999;padding:6px;vertical-align:top}\n'
        'th{background:#ddeeff;font-weight:bold}\n'
        'h2{color:#003366}\n'
        f'</style></head><body>\n'
        f'<h2>{name} - 주간업무보고서 ({date})</h2>\n'
        f'{table_html}\n</body></html>'
    )

def process_file(person, filepath, date):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    if not has_form_header(html):
        return 'skip'
    work_table = extract_work_table(html)
    if not work_table:
        return 'fail'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_template(person, date, work_table))
    return 'ok'

total_ok = total_skip = total_fail = 0
fail_list = []

for person in sorted(os.listdir(BASE)):
    if person in SKIP:
        continue
    folder = os.path.join(BASE, person)
    if not os.path.isdir(folder):
        continue
    html_files = sorted([f for f in os.listdir(folder) if f.endswith('.html')])
    if not html_files:
        continue
    p_ok = p_skip = p_fail = 0
    for fname in html_files:
        date = fname.replace('.html', '')
        result = process_file(person, os.path.join(folder, fname), date)
        if result == 'ok':
            p_ok += 1; total_ok += 1
        elif result == 'skip':
            p_skip += 1; total_skip += 1
        else:
            p_fail += 1; total_fail += 1
            fail_list.append(f'{person}/{fname}')
    print(f"{person}: 변환 {p_ok}개, 건너뜀 {p_skip}개, 실패 {p_fail}개")

print(f"\n=== 완료 === 성공:{total_ok}  건너뜀:{total_skip}  실패:{total_fail}")
for f in fail_list:
    print(f"  실패: {f}")
