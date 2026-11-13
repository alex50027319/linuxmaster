# 검증 기록

## 용어

- `mapped`: 문항 ID를 관련 학습 주제와 연결함. 정답 검증·실행 완료를 뜻하지 않습니다.
- 구문 검사: 파일을 프로그램이 해석하는지 확인함. 실제 서비스·통신 성공과 다릅니다.
- 동작 검사: 격리된 환경에서 기대한 결과를 실제로 확인함. 아래에 기록한 범위만 해당합니다.

## 현재 상태

작성일: 2026-11-14. 배포 전 수행한 검사와 한계는 여기에 기록합니다.

- 176문항은 주제 색인으로 등록하며 원문 정답표는 배포하지 않습니다.
- 디스크 포맷, RAID/LVM 생성, 서비스 전체 설정, 모든 문항의 재현은 일괄 검증 대상으로 삼지 않았습니다.
## 2026-11-14 실행 결과

환경: Rocky Linux 8.9 x86_64 VM, 커널 `4.18.0-513.5.1.el8_9.x86_64`, BIND 9.11.36, Squid 4.15, GNU coreutils 8.30, cpio 2.12, rsync 3.1.3. VM 안의 임시 디렉터리에서 검사했고 시스템 설정·서비스·실제 디스크는 변경하지 않았습니다.

| 검사 | 결과와 범위 |
|---|---|
| `scripts/check.py` | PASS. 176개 ID의 누락·중복, 12개 주제, 로컬 링크, 생성 파일 일치, 셸 문법 확인. macOS Python 3.9와 Rocky의 platform-python 3.6에서 통과 |
| 검색 도구 | PASS. 공백 있는 저장 경로, 한글, 문항 ID, 옵션처럼 시작하는 문자열, 검색 실패·인수 오류 처리. 문자열을 셸 코드로 실행하지 않는지 확인 |
| `doctor.sh` | PASS. 일반 사용자로 실행해 설치 명령·문서·장치·리스너 점검 완료. 누락 패키지도 정상 보고 |
| DNS 예제 | PASS. `named-checkconf -z`, 정방향·역방향 `named-checkzone` 모두 성공. 실제 DNS 서비스 질의는 이 검사에서 수행하지 않음 |
| Squid 예제 | PASS. `squid -f 예제 -k parse` 성공. 일반 사용자라 기본 cache.log 쓰기 권한 경고가 있었지만 parse 반환값은 0. 프록시 통신은 수행하지 않음 |
| tar·cpio·rsync | PASS. 공백 있는 파일명 포함 트리를 각각 새 폴더로 복원/복사하고 `diff -r` 일치 |
| dd 일반 파일 변환 | PASS. `conv=ucase`로 ASCII ALPHA 결과 확인. 블록 장치 이미지 복원은 수행하지 않음 |
| nice·renice | PASS. 연습 sleep PID의 NI=7 → 12 변화와 종료 확인 |
| 커널 make 도움말 | PASS. upstream Linux 4.18 소스에서 menuconfig·modules_install·bzImage 목표 표시. 실제 커널 빌드·설치·부팅은 수행하지 않음 |
| dump 매뉴얼 | Rocky 설치 버전에서 부분 파일·디렉터리 입력의 제한(레벨0, -u 불가, 동일 파일시스템)을 확인. dump/restore 실제 복원은 미실행 |

## 공개 배포 검사

- GitHub 저장소의 visibility가 `PUBLIC`, 기본 브랜치가 `main`인지 확인했습니다.
- 최초 게시 커밋 `c242b16`에서 GitHub Actions의 `Check study reference` 검사가 성공했습니다.
- Rocky 8.9 VM에 `wget` 1.19.5와 의존 패키지 libmetalink를 설치한 뒤, 인증 없이 공개 `main.tar.gz`를 실제 다운로드했습니다.
- README의 `tar --strip-components=1` 절차로 새 임시 폴더에 풀고, 내려받은 파일에서 `scripts/check.py`·문항 ID 검색·한글 검색을 통과했습니다. 생성된 `REFERENCE.txt`도 확인했습니다.
- 다운로드 검증의 임시 폴더는 제거했습니다. 위 wget 설치 외에는 서비스 설정·실제 디스크를 바꾸지 않았습니다.

## 검증하지 않은 범위

모든 문항의 빈칸 정답, 대체 답안 인정 여부, 전체 서비스 통신, 실제 디스크 포맷·RAID/LVM·쿼터·파일시스템 백업 복원은 미검증입니다. 색인 `mapped`는 이 한계를 숨기는 완료 표식이 아닙니다.

## 다시 검사하기

```bash
python3 scripts/check.py
bash scripts/doctor.sh
named-checkconf -z examples/dns/named-check.conf
named-checkzone example.test examples/dns/example.test.zone
named-checkzone 2.0.192.in-addr.arpa examples/dns/192.0.2.rev
sudo squid -f "$PWD/examples/squid.conf" -k parse
```

`doctor.sh`는 누락 도구를 보고하는 읽기 전용 점검입니다. 서비스 설치 여부에 따라 일부 검사는 실행할 수 없습니다. 설치되어 있지 않은 도구의 동작을 검증했다고 기록하지 않습니다.
