# -*- coding: utf-8 -*-
import os

base = os.path.dirname(os.path.abspath(__file__))
old_css = 'h2{color:#003366}'
new_css = 'h2{color:#003366}\ntable tr:first-child td{background:#cce8ff;font-weight:bold;text-align:center}'

count = 0
for person in os.listdir(base):
    folder = os.path.join(base, person)
    if not os.path.isdir(folder):
        continue
    for fname in os.listdir(folder):
        if not fname.endswith('.html'):
            continue
        fpath = os.path.join(folder, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            html = f.read()
        if old_css in html and 'first-child' not in html:
            html = html.replace(old_css, new_css)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(html)
            count += 1

print(f'업데이트 완료: {count}개 파일')
