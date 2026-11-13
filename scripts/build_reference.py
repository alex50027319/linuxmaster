#!/usr/bin/env python3
"""Build portable UTF-8 text and a browsable index, with no network/dependencies."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def render():
    rows = list(csv.DictReader((ROOT / 'coverage.csv').open(encoding='utf-8', newline='')))
    index = ['# 기출 주제 색인', '',
             '11개 회차 × 16문항 = 176문항. `mapped`는 관련 주제 연결을 뜻하며 정답·실행 검증을 뜻하지 않습니다.', '',
             '원문 문제는 [출처 페이지](https://dev-centralpark.tistory.com/51)에서 회차와 번호로 찾습니다. 원문에 안정적인 문항별 앵커가 없어 같은 페이지로 연결합니다.', '',
             '| ID | 관련 주제 | 상태 |', '|---|---|---|']
    for row in rows:
        links = ', '.join('[{}]({})'.format(Path(p).stem, p) for p in row['topics'].split(';'))
        index.append('| {} | {} | {} |'.format(row['id'], links, row['status']))
    files = {ROOT / 'coverage.md': '\n'.join(index) + '\n'}
    parts = ['LINUXMASTER — 오프라인 학습 참고 자료',
             '원문 전체와 공식 정답집은 포함하지 않습니다. 검증 범위: VERIFICATION.md',
             '검색: less에서 /검색어, 다음 n, 이전 N, 종료 q.']
    paths = [ROOT / 'README.md', ROOT / 'labs/00-environment.md']
    paths += sorted((ROOT / 'topics').glob('*.md'))
    paths += [ROOT / 'labs/01-practice.md', ROOT / 'sources.md', ROOT / 'VERIFICATION.md']
    for path in paths:
        parts.extend(['\n' + '=' * 72, 'FILE: ' + path.relative_to(ROOT).as_posix(), '=' * 72,
                      path.read_text(encoding='utf-8').rstrip()])
    parts.extend(['\n' + '=' * 72, 'FILE: coverage.csv', '=' * 72,
                  (ROOT / 'coverage.csv').read_text(encoding='utf-8').rstrip()])
    files[ROOT / 'REFERENCE.txt'] = '\n'.join(parts) + '\n'
    return files


if __name__ == '__main__':
    for path, content in render().items():
        path.write_text(content, encoding='utf-8')
        print(path.name)
