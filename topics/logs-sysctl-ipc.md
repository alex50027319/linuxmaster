# rsyslog·로그 조회·logrotate·sysctl·IPC

## rsyslog 규칙 읽기

전통적 문법은 `facility.priority action`입니다. facility는 발생 분야, priority는 심각도, action은 저장·전송할 대상입니다. `/etc/rsyslog.conf`와 `/etc/rsyslog.d/*.conf`를 함께 확인합니다.

```text
mail.warning                     /var/log/lab-mail.log
authpriv.*                       /var/log/lab-auth.log
*.err;kern.none                   /var/log/lab-errors.log
*.emerg                          :omusrmsg:*
```

심각도는 높은 순서로 emerg(0), alert(1), crit(2), err(3), warning(4), notice(5), info(6), debug(7)입니다. `mail.warning`은 warning **이상으로 심각한** 메시지, `mail.=warning`은 warning만, `mail.!warning`은 해당 임계 범위를 제외합니다. `*`는 전체, `none`은 제외합니다. `warn`은 warning, `panic`은 emerg의 구형 별칭이며 정리에는 표준 이름을 씁니다.

| action 예 | 의미 |
|---|---|
| `/var/log/lab.log` | 파일 저장 |
| `@192.0.2.20:514` | UDP 전송 |
| `@@192.0.2.20:514` | TCP 전송 |
| `:omusrmsg:root` | 로그인한 해당 사용자 터미널에 전달 |
| `/dev/tty2` | 지정 터미널 장치 |

송신 규칙만으로 수신 서버가 생기는 것은 아닙니다. 수신 측 imudp/imtcp 모듈과 input, 방화벽도 필요합니다. 여러 규칙이 일치하면 중복 기록될 수 있습니다. `mail,cron.notice`는 두 facility에 같은 임계값을 적용하고, `mail.warning;cron.info`는 각각의 selector를 나열합니다.

VM에서 별도 설정 파일을 만든 뒤:

```bash
sudo rsyslogd -N1
sudo systemctl restart rsyslog
logger -p local0.notice 'linuxmaster lab marker'
sudo journalctl -u rsyslog --since '-5 min'
```

`local0.notice /var/log/lab-local0.log`를 설정했다면 해당 파일에서 marker를 찾아야 합니다. `-N1`은 설정 검사이며 전송·파일 기록까지 성공했다는 뜻은 아닙니다. 실습 후 추가한 설정 파일을 제거하고 다시 검사·재시작합니다.

## 로그인 기록과 시스템 로그

| 파일 / 명령 | 역할 |
|---|---|
| `/var/log/wtmp` / `last` | 로그인·로그아웃 이력 |
| `/var/log/btmp` / `lastb` | 실패한 로그인 이력 |
| `/var/log/lastlog` / `lastlog` | 사용자별 마지막 로그인 |
| `/run/utmp` / `who`, `w` | 현재 로그인 세션. 호환 경로는 환경마다 다름 |
| `/var/log/secure` | RHEL 계열 인증 관련 텍스트 로그 |
| `/var/log/messages` | 일반 시스템 텍스트 로그 |
| `dmesg` | 커널 링 버퍼 |

```bash
last -n 5
last -s -7days
sudo lastb -n 5
lastlog -u labuser
sudo tail -f /var/log/secure
sudo dmesg | tail
journalctl -b
```

`wtmp`, `btmp`, `lastlog`는 일반 텍스트가 아니므로 `cat`으로 해석하지 않습니다. 파일이 없거나 비어 있을 수 있고 로그 정책·로테이션에 따라 범위가 달라집니다. 별도 파일은 `last -f 파일`, `lastb -f 파일`로 확인합니다.

## logrotate

시스템 정책은 `/etc/logrotate.conf`, 서비스별 설정은 `/etc/logrotate.d/`를 확인합니다. 아래는 직접 만든 연습 로그용 규칙입니다.

```text
/var/log/lab-app.log {
    weekly
    rotate 4
    maxsize 20M
    missingok
    notifempty
    compress
    create 0640 root root
}
```

`weekly`는 주 단위, `rotate 4`는 보관 개수, `maxsize`는 실행 시 크기가 넘으면 시간 조건 전에도 회전할 수 있게 합니다. 매초 파일을 감시하는 설정은 아닙니다. `size`는 시간 조건과의 관계가 다르므로 `man logrotate`를 읽습니다. `create`는 새 파일의 모드·소유자·그룹입니다. btmp/wtmp의 그룹은 종종 `utmp`이므로 기존 배포판 규칙을 무조건 root:root로 바꾸지 마세요.

검사는 `sudo logrotate -d /etc/logrotate.d/lab-app`입니다. 디버그 모드는 실제 회전하지 않습니다. 강제 실행 `-f`는 **해당 연습 설정만** 대상으로 삼고 생성 파일을 확인합니다. 실제 서비스가 열린 로그 파일을 다시 여는 절차는 서비스별 `postrotate` 등도 필요합니다.

## sysctl: 실행 중인 커널 변수

```bash
sysctl net.ipv4.ip_forward
sysctl -n net.ipv4.ip_forward
cat /proc/sys/net/ipv4/ip_forward
sysctl -a 2>/dev/null | less
```

`.`으로 구분한 sysctl 키는 `/proc/sys/` 아래 경로와 대응합니다. `sysctl -w 키=값`은 현재 실행 상태 변경, `/etc/sysctl.d/90-lab.conf` 등은 영구 설정입니다. `sysctl -p 파일`은 지정 파일 적용, `sysctl --system`은 여러 설정 경로를 읽습니다. 적용 순서와 같은 키의 중복 설정도 확인해야 합니다.

```text
# 영구 설정 파일의 예. 실제 적용 전 기존 값을 기록합니다.
net.ipv4.icmp_echo_ignore_all = 1
```

위 값은 IPv4 echo 요청 응답에 영향을 주며 네트워크 전체를 끊는 방화벽 규칙과 다릅니다. 실습 후 기존 값으로 복구하고 추가 설정 파일을 제거합니다. NAT 라우팅의 IP forwarding은 방화벽 규칙과 별개입니다.

## IPC와 파일 한도

```bash
ipcs
ipcs -s
ipcs -l
ipcs -ls
cat /proc/sys/fs/file-max
cat /proc/sys/fs/file-nr
ulimit -n
```

`ipcs -s`는 System V 세마포어 목록, `-l`은 제한값, `-ls`는 세마포어 제한값입니다. 공유 메모리 `-m`, 메시지 큐 `-q`도 구분합니다. `ipcrm`은 IPC 객체를 삭제하므로 실제 사용 중인 자원을 지우지 않습니다.

`file-max`는 시스템 전체 파일 핸들 관련 한도, `file-nr`는 할당·미사용·최대값 정보입니다. 최신 커널에서 두 번째 값이 0으로 보일 수 있습니다. `ulimit -n`은 셸/프로세스의 열린 파일 디스크립터 한도라 같은 값이 아닙니다.

도움말: `man rsyslog.conf`, `man logger`, `man last`, `man lastlog`, `man logrotate`, `man sysctl`, `man ipcs`.
