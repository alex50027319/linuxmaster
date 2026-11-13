# 사용자·그룹·파일 권한

## 조건을 명령으로 바꾸기

| 조건 | 확인할 개념 |
|---|---|
| 홈도 함께 생성 | `useradd -m` |
| 기본 그룹 / 보조 그룹 | `-g` / `-G` |
| 기존 보조 그룹을 유지하며 추가 | `usermod -aG` |
| 로그인 셸 변경 | `usermod -s` |
| 계정 사용 기한 / 암호 사용 기한 | `chage -E` / `chage -M` |
| 암호 잠금 | `passwd -l`, `usermod -L` |
| inode와 타임스탬프 | `stat` |
| 파일의 immutable 등 속성 | `lsattr`, `chattr` |

## 계정과 그룹 예제

별도 VM에서 관리자 권한으로 실행합니다. `labuser`, `labteam`은 연습용 이름입니다.

```bash
sudo groupadd labteam
sudo useradd -m -g labteam -s /bin/bash labuser
sudo passwd labuser
id labuser
getent passwd labuser
sudo usermod -aG wheel labuser
id labuser
sudo usermod -s /sbin/nologin labuser
getent passwd labuser
sudo usermod -s /bin/bash labuser
```

`-m`은 홈 디렉터리를 만들고 `/etc/skel`의 기본 파일을 복사합니다. `-d /home/practice`는 홈 경로를 지정합니다. 기존 계정의 홈 이동은 `usermod -d 새경로 -m 사용자`이며 사용 중인 세션·파일 권한을 확인해야 합니다. `usermod -G`만 쓰면 보조 그룹 목록이 교체됩니다. 변경한 그룹은 새 로그인에서 반영되는지 확인합니다.

```bash
sudo usermod -l labstudent labuser
sudo groupmod -n labclass labteam
sudo gpasswd -a labstudent labclass
sudo gpasswd -d labstudent labclass
sudo gpasswd -A labstudent labclass
```

`usermod -l`은 로그인 이름만 바꿉니다. 홈 경로·메일 스풀까지 자동으로 전부 바뀐다고 생각하면 안 됩니다. `gpasswd -A`는 그룹 관리자, `-a`는 구성원 추가입니다. 명령이 사용자를 요구하는지 그룹을 요구하는지 마지막 인수를 확인하세요.

## 잠금·만료

```bash
sudo passwd -S labstudent
sudo passwd -l labstudent
sudo passwd -u labstudent
sudo chage -M 60 -W 10 -I 7 labstudent
sudo chage -E 2027-12-31 labstudent
sudo chage -l labstudent
```

`-M`은 암호 최대 사용 일수, `-W`는 만료 경고 일수, `-I`는 **암호 만료 이후** 비활성화까지의 일수, `-E`는 계정 만료일입니다. `usermod -e`와 `-f`도 계정 만료일·암호 만료 후 유예를 다룹니다. 암호 잠금만으로 SSH 공개키 인증까지 모두 차단되는 것은 아닙니다. `passwd -d`는 암호를 지우는 동작으로 잠금과 다릅니다.

주요 파일:

| 경로 | 역할 |
|---|---|
| `/etc/passwd` | 사용자명, UID, 기본 GID, 홈, 셸 |
| `/etc/shadow` | 암호 해시와 만료 정보 |
| `/etc/group`, `/etc/gshadow` | 그룹 및 보호된 그룹 정보 |
| `/etc/default/useradd` | useradd 기본값. `useradd -D`로 조회 |
| `/etc/login.defs` | UID 범위·암호 기간 등 생성 기본값 |
| `/etc/skel` | 새 홈에 복사할 기본 파일 |

`useradd -D -b /home/lab -s /bin/bash`는 이후 생성할 계정의 기본값 변경입니다. 기존 계정은 따로 수정합니다. sudo 설정은 `sudo visudo`로 편집하고 `sudo visudo -c`로 검사합니다. 예: `labstudent ALL=(root) /usr/sbin/ip`는 지정한 실행 파일의 root 실행 권한입니다. 모든 명령 허용과 혼동하지 마세요.

## getent·lsattr와 로그인 정보

`getent`는 NSS 데이터베이스를 조회합니다. 로컬 파일뿐 아니라 NSS에 연결된 다른 사용자 정보 공급원을 조회할 수 있습니다.

```text
$ getent passwd labstudent
labstudent:x:1001:1001::/home/labuser:/bin/bash
$ lsattr memo.txt
----i----------------- memo.txt
```

위 출력은 설명용입니다. UID·홈·속성 열 수는 환경마다 다릅니다. `lsattr`의 `i`는 수정·삭제가 제한되는 immutable 속성입니다. 지원하는 파일시스템에서 `sudo chattr +i memo.txt`, 해제는 `sudo chattr -i memo.txt`입니다.

`who`는 로그인 세션 상세, `users`는 로그인 사용자명 목록, `whoami`는 현재 프로세스의 유효 사용자명입니다. `sudo whoami`는 보통 `root`이고 원래 로그인 계정과 다를 수 있습니다.

## 권한·링크·검색

```bash
mkdir -p ~/permission-lab/shared
chmod 700 ~/permission-lab
umask 027
touch ~/permission-lab/sample
stat ~/permission-lab/sample
ln ~/permission-lab/sample ~/permission-lab/hardlink
ln -s sample ~/permission-lab/softlink
ls -li ~/permission-lab
```

파일 생성 기본값은 보통 666, 디렉터리는 777에서 umask 비트를 제거합니다. `umask 027`이면 일반적으로 파일 640, 디렉터리 750입니다. 파일에 실행 권한을 자동으로 주지 않습니다. 하드 링크는 같은 파일시스템에서 inode를 공유하며, 심볼릭 링크는 경로를 가리킵니다.

```bash
sudo chgrp labclass /srv/labshare
sudo chmod 3770 /srv/labshare
find /usr/bin -type f -perm -4000 -print
find /usr/bin -type f -perm /6000 -print
```

`/srv/labshare`는 미리 만든 연습 디렉터리라고 가정합니다. 특수 권한 숫자는 SUID=4, SGID=2, Sticky=1입니다. 디렉터리 SGID는 새 파일의 그룹 상속, Sticky는 디렉터리 내 삭제·이름 변경 제한입니다. `-perm -6000`은 두 비트 모두, `-perm /6000`은 둘 중 하나 이상을 뜻합니다. 일반 권한도 함께 보세요. `s/S`, `t/T`의 대문자는 해당 실행 비트가 꺼진 상태입니다.

## 검증과 정리

`id`, `getent`, `chage -l`, `stat`, `ls -ld`, 실제 새 로그인으로 요구한 상태를 확인합니다. `userdel -r labstudent`는 연습 계정과 홈을 지우므로 필요한 파일을 먼저 보관하세요. 전역 기본값과 그룹 변경까지 되돌리기에는 VM 스냅샷 복원이 편합니다.

도움말: `man useradd`, `man usermod`, `man chage`, `man gpasswd`, `man chmod`, `man find`, `man getent`, `man lsattr`.
