# linuxmaster

리눅스마스터 1급 실기를 **Rocky Linux 8 계열 VM에서 연습**하기 위한 한국어 참고 자료입니다.

연결한 기출 모음의 11개 회차·176문항을 주제별로 연결한 색인, 직접 작성한 개념·명령어·설정 예제, 실습 과제를 제공합니다. 원문 문제와 정답 전체를 복제한 자료나 공식 정답집이 아닙니다. 색인 등록과 실제 명령 실행 검증은 구분하며, 검증 범위는 [검증 기록](VERIFICATION.md)에 적습니다.

## 다른 컴퓨터에서 받기

다음은 Rocky Linux VM 터미널에서 실행합니다. 처음 다운로드할 때만 인터넷이 필요합니다. `wget`이 없다면 먼저 `sudo dnf install wget`을 실행합니다.

```bash
wget -O linuxmaster.tar.gz https://github.com/alex50027319/linuxmaster/archive/refs/heads/main.tar.gz
mkdir -p linuxmaster
tar -xzf linuxmaster.tar.gz --strip-components=1 -C linuxmaster
cd linuxmaster
less REFERENCE.txt
```

이미 파일이 있는 폴더에 덮어쓰기보다 새 폴더에 풀어 연습 기록을 보존하세요. 고정 버전이 필요하면 `main` 대신 GitHub의 특정 커밋에 대한 archive URL을 사용합니다. 저장소 다운로드에는 Git 설치가 필요하지 않습니다. 패키지와 `man` 문서는 별도로 준비해야 합니다.

## 바로 찾기

```bash
./scripts/search.sh squid
./scripts/search.sh '역방향'
./scripts/search.sh 2601-14
./scripts/search.sh 'make menuconfig'
grep -n 'xfs_quota' REFERENCE.txt
less topics/dns.md
```

`search.sh`는 문자열을 그대로 검색합니다. 정규식 검색이 필요하면 `grep -RniE '프록시|squid|http_access' topics/`를 사용합니다. `less`에서는 `/검색어`, 다음 결과는 `n`, 이전 결과는 `N`, 종료는 `q`입니다.

## 목차

| 자료 | 내용 |
|---|---|
| [기출 색인](coverage.md) / [CSV](coverage.csv) | 회차·문항 → 관련 주제. 같은 문항에 여러 주제가 있을 수 있음 |
| [사용자·권한](topics/users-permissions.md) | 계정, 그룹, 만료, sudo, 특수 권한, find |
| [스토리지](topics/storage-raid-lvm-quota.md) | fdisk/parted, 파일시스템, mount, swap, RAID, LVM, quota |
| [프로세스·cron](topics/processes-cron.md) | nice/renice, 종료, 개인·시스템 crontab |
| [패키지·커널](topics/packages-kernel.md) | DNF/RPM, gcc, make 목표, 모듈, 장치 정보 |
| [로그·sysctl·IPC](topics/logs-sysctl-ipc.md) | rsyslog, last/lastb, logrotate, 커널 변수 |
| [백업·복원](topics/backup-restore.md) | tar/cpio/rsync/dd/dump/xfsdump 선택과 복원 |
| [Apache](topics/apache.md) | 기본 설정, UserDir, 인증, 가상 호스트 |
| [DNS](topics/dns.md) | named.conf, 정·역방향 zone, SOA와 레코드 |
| [메일](topics/mail.md) | Sendmail 별칭, 가상 사용자, DB 갱신 |
| [Samba·NFS·FTP](topics/samba-nfs-ftp.md) | 서버 설정과 클라이언트 확인 |
| [Squid·DHCP](topics/squid-dhcp.md) | ACL, 지시어 찾기, DHCP 범위·옵션 |
| [방화벽·SSH·SELinux](topics/firewall-ssh-selinux.md) | NAT, firewalld, SSH, 구형 TCP Wrapper 구분 |
| [VM 준비](labs/00-environment.md) | 패키지, 문서, 네트워크, 스냅샷 |
| [실습 순서](labs/01-practice.md) | 자체 과제와 확인 기준, 틀린 문제 기록 |
| [DNS 실습 파일](examples/dns/) / [Squid 파일](examples/squid.conf) | 시스템 설정에 자동 적용하지 않는 예제 |
| [출처](sources.md) | 기출 원문 링크와 공식 기술 문서 |

## 사용 순서

1. VM 스냅샷을 저장하고 `bash scripts/doctor.sh`로 명령·문서 설치 여부를 확인합니다. 이 스크립트는 설치·서비스 변경·디스크 수정을 하지 않습니다.
2. 원문에서 한 문항을 풀고 `coverage.md`에서 해당 ID를 찾습니다. 예: `2601-14`.
3. 연결된 주제에서 조건 → 문법 → 옵션 의미 → 검증 순서로 복습합니다.
4. 자체 실습은 [labs](labs/01-practice.md)의 기대 결과까지 확인합니다. 문법 검사 통과와 서비스 동작 성공을 구분합니다.
5. 정리본을 닫고 다시 풀고, `templates/review.csv`에 실패 원인과 재검증 결과를 적습니다.

예제 주소 `192.0.2.0/24`, `198.51.100.0/24`는 설명용입니다. 실제 VM 네트워크와 인터페이스 이름으로 바꿔야 합니다. 디스크 예제는 데이터를 지우므로 **추가한 빈 연습 디스크**를 `lsblk`로 식별한 뒤 필요한 명령만 직접 실행합니다. 이 저장소에는 자동 포맷 스크립트가 없습니다.

## 로컬 정리본 갱신

Python 3가 있는 컴퓨터에서:

```bash
python3 scripts/build_reference.py
python3 scripts/check.py
```

Python 없이도 이미 생성된 `REFERENCE.txt`, Markdown, CSV, 검색·환경 점검 스크립트를 사용할 수 있습니다. Rocky 8.9 연습을 기준으로 작성했으며, 구형 기출의 TCP Wrapper·Apache 2.2 문법 등은 현재 버전과 구분합니다. 실제 시험 환경·제공 패키지·참고 자료 허용 여부는 해당 회차 공식 안내로 확인하세요.
