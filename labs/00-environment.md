# VM 준비와 오프라인 문서 확보

## VM 구성

Rocky Linux 8.9 x86_64를 연습 기준으로 사용합니다. 다른 버전에서도 대부분의 개념은 같지만 지시어·기본값·패키지 가용성은 다를 수 있습니다. 설치 매체·저장소는 공식 경로를 사용하세요. 8.9처럼 과거 minor 버전을 고정하려면 일반 mirror 대신 해당 vault 구성을 검토해야 하며, `dnf update`로 버전이 바뀔 수 있습니다.

권장 연습 구성은 RAM 4GiB 이상, 시스템 디스크 30GiB 이상, 스토리지 실습용 빈 디스크 2–4개입니다. RAID6까지 직접 만들려면 최소 4개 구성원 디스크가 필요합니다. 스토리지 연습을 위해 시스템 디스크를 재분할하지 않습니다.

VirtualBox는 호스트 CPU와 가상화 지원에 맞는 게스트를 사용해야 합니다. Apple Silicon에서 x86_64 Rocky를 연습하려면 UTM/QEMU의 에뮬레이션 같은 별도 경로가 필요할 수 있습니다. 현재 VM의 실제 버전·장치는 다음으로 기록합니다.

```bash
cat /etc/rocky-release
uname -m
uname -r
lsblk -f
ip -br address
ip route
```

패키지 설치와 자료 다운로드에는 NAT NIC를 쓰고, DHCP·라우터 실습에는 별도의 내부 네트워크 NIC를 사용합니다. VM 여러 대가 필요한 과제는 서버·클라이언트를 같은 내부 네트워크에 두고 IP 충돌을 피합니다. 각 실습 전 전원을 안전하게 종료하고 스냅샷을 저장합니다. 스냅샷 자체도 호스트 고장에 대비한 백업을 완전히 대신하지는 않습니다.

## 기본 명령과 문서

아래 명령은 필요에 따라 **직접 선택해 설치**합니다. 저장소 가용성을 먼저 `dnf repolist`, `dnf info 패키지명`으로 확인합니다. 모든 패키지가 기본 설치되어 있다고 가정하지 않습니다.

```bash
sudo dnf install man-db man-pages less vim-enhanced wget bash-completion
sudo dnf install parted e2fsprogs xfsprogs mdadm lvm2 quota dump xfsdump
sudo dnf install tar cpio rsync cronie gcc make
sudo dnf install bind bind-utils httpd httpd-tools
sudo dnf install samba samba-client cifs-utils nfs-utils vsftpd
sudo dnf install squid dhcp-server sendmail sendmail-cf
sudo dnf install policycoreutils-python-utils nmap
```

별도 실습에 따라 firewalld·iptables 관련 패키지가 필요할 수 있습니다. 서로 다른 방화벽 관리 서비스를 무작정 동시에 켜지 않습니다. 패키지를 설치하는 것과 서비스를 시작·활성화하는 것은 다른 작업입니다. 시험용 명령 연습을 위해 오래된 서비스 전부를 인터넷에 공개할 필요도 없습니다.

```bash
man 8 useradd
man 5 crontab
man -k samba
apropos quota
rpm -qd squid
rpm -qc httpd
rpm -ql bind | less
```

`man`이 실패하는 이유는 프로그램 미설치, 해당 페이지 미포함, MANPATH·locale 문제 등입니다. `command -v 명령`, `man -w 페이지`, `rpm -q 패키지`로 나누어 확인합니다. `help`는 Bash 내장 명령용이고 `명령 --help`는 프로그램별 기능입니다. `sudo mandb`는 검색 DB 갱신이며 없는 문서 패키지를 설치하는 명령은 아닙니다.

## 커널 소스가 없는 경우

`/usr/src`가 비어 있어도 일반 Linux 명령 연습에는 문제가 없습니다. 커널 make 목표를 연습할 때는 공식 소스 tarball이나 배포판 소스를 별도 디렉터리에 풀고 `make help`를 읽습니다. [kernel.org](https://www.kernel.org/)에서 원하는 버전과 검증 자료를 확인합니다. 임의 다운로드를 root로 풀거나 실행하지 않습니다. 전체 컴파일에는 추가 의존성과 시간·공간이 필요합니다. `kernel-devel`과 전체 upstream 커널 소스는 구분하세요.

## 처음 실행할 점검

```bash
bash scripts/doctor.sh
```

이 결과는 설치 여부를 보여주는 목록입니다. MISSING이 많아도 읽기·검색은 할 수 있고, 모두 OK여도 설정·서비스까지 성공했다는 의미는 아닙니다. 개인 PC의 진단 출력에는 사용자·경로 정보가 있을 수 있으므로 자신의 기록으로 보관합니다. 자격 증명, 개인키, VM 이미지, 실제 운영 설정은 공개 저장소에 넣지 않습니다.

## 학습 기록

`templates/review.csv`를 개인 연습 폴더에 복사합니다. `question_id`는 색인의 ID, `error_reason`에는 “출발지/목적지를 반대로 읽음”, “파일 갱신 후 DB 재생성 누락”처럼 구체적인 원인을 적습니다. 자료만 읽는 회차와 자료를 닫고 재현하는 회차를 구분하세요.
