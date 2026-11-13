# 방화벽·NAT·SSH·SELinux·구형 TCP Wrapper

## 먼저 어떤 방화벽을 쓰는지 확인

```bash
systemctl is-active firewalld
sudo firewall-cmd --get-active-zones
sudo iptables -S
sudo iptables -t nat -S
ip -br address
ip route
```

Rocky 8에서는 nftables 기반 구현을 사용할 수 있습니다. firewalld와 직접 만든 iptables 규칙을 무계획하게 섞으면 상태가 어긋납니다. 기출의 명령 문법 연습과 실제 VM 방화벽 적용 방식을 구분합니다. 아래 변경 예제는 콘솔·스냅샷이 있는 별도 네트워크 실습에서만 필요한 줄을 선택해 사용합니다. SSH로 접속한 상태에서 전체 규칙을 flush하거나 기본 정책을 DROP으로 바꾸지 않습니다.

## iptables: 표와 체인

filter 표의 INPUT은 내 호스트가 받을 패킷, OUTPUT은 내 호스트가 보낼 패킷, FORWARD는 통과하는 패킷입니다. NAT의 PREROUTING은 주로 목적지 변환, POSTROUTING은 주로 출발지 변환에 사용합니다.

```bash
sudo iptables -L -n -v --line-numbers
sudo iptables -t nat -L -n -v --line-numbers
# 별도 VM에서: 특정 클라이언트의 웹 접속 허용 예
sudo iptables -A INPUT -s 192.0.2.50 -p tcp --dport 80 -j ACCEPT
```

`-A` 뒤에 추가, `-I 체인 번호` 삽입, `-D` 삭제, `-R` 교체, `-F` 비우기, `-P` 기본 정책입니다. INPUT 뒤에 기존 거부 규칙이 먼저 있으면 추가한 허용 규칙까지 도달하지 않을 수 있습니다. `--sport`는 출발지 포트, `--dport`는 목적지 포트입니다. `-i` 입력 NIC, `-o` 출력 NIC, `-s` 출발지, `-d` 목적지입니다.

`-j LOG`는 로그를 남기지만 그 자체로 최종 허용/차단 결정을 끝내지 않습니다. `--log-prefix 'LAB '` 등으로 표식을 붙인 뒤 필요한 ACCEPT/DROP 규칙을 별도로 둡니다. 규칙 번호 삭제는 현재 표의 `--line-numbers`로 번호를 확인한 뒤 `-D 체인 번호`를 쓰며 삭제할 때마다 뒤 번호가 바뀝니다.

설정 파일 저장/복원 문법:

```bash
sudo iptables-save > ~/iptables.saved
sudo sh -c 'iptables-restore < /정확한/백업경로/iptables.saved'
```

현재 메모리 규칙을 저장하는 것과 부팅 때 자동 적용하는 것은 별개입니다. iptables-services 사용 여부와 firewalld를 확인합니다.

## NAT: 주소 변환만으로 라우팅이 완성되지 않음

가정: 내부 192.0.2.0/24, 외부 NIC `enp0s3`, 외부 고정 IP 198.51.100.10, 내부 웹 서버 192.0.2.30. 실제 NIC·주소로 바꿔야 합니다.

```bash
# 외부 주소가 변하는 환경의 출발지 변환
sudo iptables -t nat -A POSTROUTING -s 192.0.2.0/24 -o enp0s3 -j MASQUERADE
# 고정 주소라면 위 규칙 대신 SNAT를 검토
sudo iptables -t nat -A POSTROUTING -s 192.0.2.0/24 -o enp0s3 -j SNAT --to-source 198.51.100.10
# 외부 8080을 내부 웹 서버 80으로 목적지 변환
sudo iptables -t nat -A PREROUTING -i enp0s3 -p tcp --dport 8080 -j DNAT --to-destination 192.0.2.30:80
```

위 MASQUERADE와 SNAT는 대안이므로 같은 조건으로 둘 다 무조건 넣지 않습니다. `net.ipv4.ip_forward=1`, FORWARD 허용, 응답 방향의 conntrack 허용, 내부 서버의 반환 경로도 필요합니다. `-m conntrack --ctstate ESTABLISHED,RELATED`는 기존 연결·관련 트래픽을 허용하는 조건입니다. 검사 호스트에서 외부 주소에 접속하고 NAT/FORWARD 규칙 카운터와 응답을 확인해야 합니다. DNAT는 로컬에서 시작한 연결과 외부에서 들어온 연결의 경로가 다를 수 있습니다.

## firewalld: runtime / permanent / zone

```bash
sudo firewall-cmd --get-default-zone
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --zone=public --list-all
sudo firewall-cmd --zone=public --add-service=http
sudo firewall-cmd --zone=public --query-service=http
sudo firewall-cmd --permanent --zone=public --add-service=http
sudo firewall-cmd --reload
sudo firewall-cmd --zone=public --list-all
```

`--permanent`만 설정하면 현재 runtime에 바로 반영되지 않습니다. reload는 permanent를 runtime에 반영하면서 기존 runtime 전용 변경을 잃을 수 있습니다. 서비스 이름 대신 포트는 `--add-port=8080/tcp`입니다. 삭제는 `--remove-service`/`--remove-port`이며 permanent도 별도로 제거해야 합니다. 실제 NIC가 다른 zone에 속하면 public에 추가해도 기대한 접속이 되지 않을 수 있습니다.

## SSH 공개키와 root 로그인 정책

```bash
ssh-keygen -t ed25519
ssh-copy-id labuser@192.0.2.10
ssh labuser@192.0.2.10
```

새 키를 생성할 때 기존 키 경로를 덮어쓰지 않습니다. `.pub`은 공개키, 확장자 없는 파일은 개인키입니다. 개인키는 서버에 배포하거나 저장소에 올리지 않습니다. 서버의 `~/.ssh/authorized_keys`, 소유자, 디렉터리700·파일600 권한, SELinux 라벨 등을 확인합니다.

```text
# /etc/ssh/sshd_config
PermitRootLogin no
```

`prohibit-password`는 root의 암호 인증을 제한하지만 공개키 인증은 허용할 수 있어 `no`와 다릅니다. 파일 수정 뒤 `sudo sshd -t`, 실제 적용 설정은 `sudo sshd -T`로 확인하고 reload합니다. Match 조건이 있으면 적용 대상에 따라 달라질 수 있습니다. 기존 세션을 유지하며 새 세션이 성공하는지 확인한 후 종료합니다.

## SELinux: 상태와 실제 차단 원인

```bash
getenforce
sestatus
ls -Zd /var/www/html
sudo ausearch -m AVC -ts recent
```

Enforcing은 정책 강제, Permissive는 거부를 기록하되 강제하지 않음, Disabled는 비활성 상태입니다. `setenforce 0/1`은 현재 실행 상태 변경이며 Disabled 상태에서 정책을 켜는 명령이 아닙니다. 영구 설정은 `/etc/selinux/config`와 부팅 절차를 확인합니다. 서비스 오류가 나면 SELinux를 끄기 전에 라벨·Boolean·AVC를 확인합니다.

`restorecon`은 기본 라벨 복원, `semanage fcontext -a -t httpd_sys_content_t '/srv/labweb(/.*)?'`는 영구 경로 라벨 정의의 예입니다. 이어서 `restorecon -Rv /srv/labweb`이 필요합니다. `semanage`는 `policycoreutils-python-utils` 패키지가 필요할 수 있습니다.

## nmap와 구형 TCP Wrapper

자신의 VM만 대상으로 `nmap -F 127.0.0.1`처럼 빠른 포트 검사를 연습합니다. 로컬 리스너는 `ss -lntup`도 함께 확인합니다. nmap의 open/closed/filtered는 서로 다르고 외부에서의 도달 가능성은 별도 검사입니다.

옛 환경의 TCP Wrapper는 `/etc/hosts.allow`를 먼저 보고, 허용되지 않으면 `/etc/hosts.deny`를 확인합니다. 예: allow의 `sshd: 192.0.2.`와 deny의 `sshd: ALL`. `daemon: client` 형식, `ALL`, `EXCEPT`가 주요 개념입니다. xinetd는 `/etc/xinetd.d/서비스`의 `disable = no`, `server`, `socket_type`, `wait` 등을 사용했습니다.

**RHEL/Rocky 8에서는 TCP Wrapper 지원이 제거된 환경이므로 hosts.allow를 만들었다고 현대 sshd 접근이 제한되는 것은 아닙니다.** 구형 기출 문법은 이론으로 분리하고 Rocky 8의 실제 제한은 firewalld·서비스 설정으로 실습합니다. `telnet`도 평문 인증이므로 실제 접속 수단으로는 SSH를 사용합니다.

정리는 추가한 규칙·서비스·SELinux 경로 정의를 정확히 제거하거나 스냅샷 복원으로 진행합니다. 도움말: `man iptables`, `man iptables-extensions`, `man firewall-cmd`, `man sshd_config`, `man ssh-keygen`, `man semanage`.
