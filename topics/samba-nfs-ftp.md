# Samba·NFS·vsftpd

## Samba: SMB 파일 공유

서버 패키지 `samba`, 클라이언트 `samba-client`, 마운트 도구 `cifs-utils`를 구분합니다. 설정은 `/etc/samba/smb.conf`입니다.

```ini
[global]
    workgroup = LABGROUP
    server string = Practice SMB server
    security = user
    map to guest = Never

[labshare]
    path = /srv/labshare
    browseable = yes
    read only = no
    valid users = labuser
    create mask = 0660
    directory mask = 0770
```

`[global]`은 전역, `[labshare]`는 공유 이름입니다. browseable은 목록 표시, read only는 쓰기 허용 여부, valid users는 접속 허용 사용자입니다. `writable = yes`는 `read only = no`와 관련된 별칭입니다. mask는 Unix 생성 권한 제한이며 기존 파일을 모두 해당 권한으로 바꾸는 지시어가 아닙니다. `hosts allow`, `hosts deny`를 쓰는 경우 IP·네트워크 조건도 확인합니다.

`comment`는 공유 설명, `netbios name`은 서버의 NetBIOS 이름입니다. 공유를 기본 읽기 전용으로 두고 `write list = labuser`로 일부 사용자에게만 쓰기를 허용하는 구성도 가능합니다. write list는 valid users·파일시스템 권한을 대신하지 않습니다.

```bash
sudo mkdir -p /srv/labshare
sudo chown labuser:labuser /srv/labshare
sudo chmod 770 /srv/labshare
sudo smbpasswd -a labuser
testparm -s
smbclient -L //192.0.2.10 -U labuser
smbclient //192.0.2.10/labshare -U labuser
```

labuser의 기본 그룹도 labuser인 예입니다. 실제 그룹은 `id labuser`로 확인합니다. Unix 계정과 Samba 암호 DB 등록이 모두 필요합니다. `testparm` 성공은 Unix 권한·방화벽·SELinux·인증 성공까지 보장하지 않습니다. `smbclient`에서 `ls`, `put`, `get`, `quit`으로 실습합니다. 서버는 보통 `smb` unit이며 NetBIOS 기능에는 `nmb`가 추가될 수 있습니다.

SMB 마운트는 `sudo mount -t cifs //192.0.2.10/labshare /mnt/labsmb -o username=labuser`처럼 수행합니다. 마운트 경로를 먼저 만들고 암호는 프롬프트로 입력합니다. 명령행에 평문 암호를 넣지 않습니다. SELinux Enforcing에서는 공유 경로의 `samba_share_t` 라벨 등도 필요하며 `semanage fcontext`와 `restorecon`을 확인합니다.

`smb`로 시작하는 설치된 명령 검색:

```bash
compgen -c | grep '^smb' | sort -u
apropos samba
rpm -ql samba-client | grep '/bin/'
```

`compgen`은 Bash 기능입니다. 명령 후보와 매뉴얼 검색, 패키지 파일 목록은 서로 다른 검색입니다.

## NFS: exports와 exportfs

설정 `/etc/exports`:

```exports
/srv/labnfs 192.0.2.0/24(rw,sync,root_squash)
```

**클라이언트와 `(옵션)` 사이에 공백을 넣지 않습니다.** `rw/ro`는 쓰기/읽기, `sync`는 동기 응답 정책, `root_squash`는 클라이언트 root를 익명 사용자로 매핑합니다. `no_root_squash`는 그 매핑을 하지 않으므로 조건을 정확히 읽습니다. `all_squash`, `anonuid`, `anongid`도 익명 매핑과 관련됩니다. 서버·클라이언트의 UID/GID 및 실제 Unix 권한도 필요합니다.

```bash
sudo exportfs -ra
sudo exportfs -v
showmount -e 192.0.2.10
sudo mkdir -p /mnt/labnfs
sudo mount -t nfs 192.0.2.10:/srv/labnfs /mnt/labnfs
findmnt /mnt/labnfs
```

서버 공유 디렉터리 생성·권한과 `nfs-server` 시작이 선행되어야 합니다. `exportfs -r`은 다시 내보내기, `-a`는 전체, `-u`는 내보내기 해제입니다. `showmount`는 mountd 기반 조회여서 NFSv4 전용 서버에서 실패해도 모든 NFS 서비스 실패를 뜻하지 않습니다. NFSv3와 v4의 포트·경로 차이도 확인합니다.

## vsftpd: 허용 정책을 두 단계로 읽기

설정 `/etc/vsftpd/vsftpd.conf`의 대표 지시어:

```ini
anonymous_enable=NO
local_enable=YES
write_enable=YES
local_umask=027
chroot_local_user=YES
userlist_enable=YES
userlist_deny=YES
userlist_file=/etc/vsftpd/user_list
xferlog_enable=YES
```

`local_enable`은 로컬 계정 로그인, `write_enable`은 쓰기 관련 명령, `anonymous_enable`은 익명 로그인입니다. `userlist_enable=YES` 상태에서 `userlist_deny=YES`이면 목록 계정을 거부하고, NO면 목록 계정만 허용합니다. PAM의 `/etc/vsftpd/ftpusers` 거부 목록은 별도로 적용될 수 있으므로 user_list 하나만 보고 판단하지 않습니다.

`chroot_local_user=YES`는 로컬 사용자의 경로를 가둡니다. `chroot_list_enable`과 목록이 함께 쓰이면 목록의 의미가 전체 기본 정책에 따라 뒤집힐 수 있습니다. 쓰기 가능한 chroot 루트를 거부하는 버전도 있어 **루트 디렉터리는 쓰기 금지, 그 아래 업로드 디렉터리만 쓰기 허용**하는 구성을 먼저 고려합니다.

익명 업로드 조건은 `anon_upload_enable`뿐 아니라 write_enable·디렉터리 권한 등이 함께 필요합니다. `anon_mkdir_write_enable`, `anon_other_write_enable`은 각각 생성·다른 변경 동작입니다. `listen`과 `listen_ipv6`를 동시에 켜면 충돌할 수 있으므로 배포판 기본값을 확인합니다. passive FTP에는 별도 포트 범위·방화벽 설정도 필요합니다.

## 검증·정리

Samba는 testparm → 인증 접속 → 파일 쓰기/읽기, NFS는 exportfs → 클라이언트 mount → 권한별 I/O, FTP는 서비스 시작 로그 → 계정 허용/거부 → 업로드/다운로드를 확인합니다. FTP는 평문 프로토콜이므로 격리된 연습 네트워크에서 사용합니다. vsftpd에는 다른 도구의 `-t` 같은 문법 검사 옵션이 당연히 있다고 가정하지 말고 설치 버전 도움말을 확인하세요.

마운트를 먼저 해제하고 추가한 공유·계정·서비스 설정을 복원합니다. 도움말: `man smb.conf`, `man smbclient`, `man testparm`, `man exports`, `man exportfs`, `man vsftpd.conf`.
