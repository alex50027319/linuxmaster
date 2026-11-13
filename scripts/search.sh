#!/usr/bin/env bash
set -eu
if [ "$#" -ne 1 ] || [ -z "$1" ]; then
    printf '사용법: %s "검색할 문자열"\n' "$0" >&2
    exit 2
fi
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
status=0
grep -RniF -- "$1" "$root/topics" "$root/labs" "$root/examples" "$root/coverage.csv" "$root/README.md" || status=$?
if [ "$status" -eq 1 ]; then
    printf '일치하는 내용이 없습니다: %s\n' "$1" >&2
fi
exit "$status"
