# Squid 프록시·DHCP

## 설정값을 어디서 찾는가

명령어에는 `man 명령`, 설정에는 **설정 파일 매뉴얼·패키지 문서·샘플**이 유용합니다. 설정 파일명으로 man 페이지가 반드시 제공되는 것은 아닙니다.

```bash
rpm -q squid
rpm -qc squid
rpm -qd squid
rpm -ql squid | grep -Ei 'conf|doc|example'
man -k squid
less /usr/share/doc/squid/squid.conf.documented
grep -n -A 15 '^#  TAG: http_access' /usr/share/doc/squid/squid.conf.documented
```

위 documented 경로는 Rocky 8의 Squid 패키지에서 확인한 경로이며 다른 배포판에서는 다를 수 있습니다. `man squid.conf`가 없으면 문서 파일을 찾습니다. `squid.conf.default`와 실제 사용 중인 `squid.conf`도 구분하세요. 설명이 길면 `less`에서 `/TAG: acl`처럼 찾습니다.

## Squid ACL: 이름 정의와 적용은 별개

```squid
http_port 3128
acl lab_clients src 192.0.2.0/24
acl blocked_sites dstdomain .blocked.example.test
http_access deny blocked_sites
http_access allow lab_clients
http_access deny all
```

`acl 이름 종류 값`은 조건을 정의하며, `http_access allow/deny 이름`이 접근 정책을 적용합니다. `src`는 클라이언트 IP, `dst`는 목적지 IP, `dstdomain`은 목적지 도메인, `srcdomain`은 클라이언트의 도메인 이름 판정과 관련됩니다. 출발지·목적지를 바꿔 읽지 마세요. `time`, `port`, `method` 등의 ACL도 있습니다.

접근 규칙은 위에서 아래로 검사합니다. 첫 일치 정책이 적용되므로 차단 규칙을 광범위 허용 뒤에 두면 우회될 수 있습니다. 한 `http_access` 줄의 서로 다른 ACL 이름은 대체로 AND 조건이고, 같은 ACL 목록의 여러 값은 종류에 따라 OR로 평가됩니다. 부정은 `!ACL이름`입니다.

위 짧은 예는 **ACL 개념 설명용**입니다. 실제 설치의 `Safe_ports`, `SSL_ports`, CONNECT 제한, localhost 관리자 접근 같은 기존 보호 규칙을 삭제하는 교체 파일로 사용하지 마세요. [examples/squid.conf](../examples/squid.conf)는 문법 연습용이며 마지막에 모두 거부합니다.

```bash
sudo squid -k parse
sudo squid -f "$PWD/examples/squid.conf" -k parse
```

첫 명령은 현재 기본 설정, 둘째는 지정 예제 검사입니다. `-k parse`는 설정 해석 검사이며 통신·외부 DNS·접근 정책 실제 성공 검증은 아닙니다. 서비스 적용은 기존 파일 보관 → 수정 → parse → `systemctl reload squid` 순서입니다. 테스트 주소를 실제 연습 웹 서버로 바꾼 뒤 `curl -x http://프록시IP:3128 http://연습서버/`와 `/var/log/squid/access.log`로 허용·차단을 각각 확인합니다.

그 밖에 `cache_dir`는 디스크 캐시 저장 설정, `cache_mem`은 메모리 캐시 관련 설정, `access_log`는 요청 로그, `visible_hostname`은 표시용 호스트명입니다. 모든 버전의 지시어가 같지 않으므로 `squid -v`와 버전별 문서를 함께 확인합니다.

## DHCP: 격리한 네트워크에서만 실습

다른 DHCP 서버가 있는 NAT/브리지 네트워크에 무작정 DHCP 서버를 켜면 안 됩니다. VirtualBox **내부 네트워크**에 서버·클라이언트 VM을 두고 다른 DHCP를 끈 연습 환경을 사용합니다. 서버 인터페이스에는 고정 IP가 필요합니다.

설정 `/etc/dhcp/dhcpd.conf`의 자체 예제:

```dhcpd
default-lease-time 900;
max-lease-time 7200;
option domain-name "lab.example.test";
option domain-name-servers 192.0.2.10;
subnet 192.0.2.0 netmask 255.255.255.0 {
    range 192.0.2.100 192.0.2.150;
    option routers 192.0.2.1;
    option broadcast-address 192.0.2.255;
}
host labclient {
    hardware ethernet 02:00:00:12:34:56;
    fixed-address 192.0.2.50;
}
```

lease-time은 초 단위, subnet은 네트워크 선언, range는 동적 임대 구간, routers는 기본 게이트웨이, domain-name-servers는 DNS 서버입니다. `host`는 고정 할당이고 hardware ethernet은 MAC 주소입니다. 고정 주소를 동적 풀 밖에 두어 중복을 피합니다. 서버에 직접 연결된 인터페이스와 맞는 subnet 선언이 필요합니다.

```bash
sudo dhcpd -t -cf /etc/dhcp/dhcpd.conf
sudo systemctl status dhcpd
sudo journalctl -u dhcpd --since '-10 min'
sudo less /var/lib/dhcpd/dhcpd.leases
```

문법 검사는 실제 임대 성공을 뜻하지 않습니다. 격리된 클라이언트에서 IP·게이트웨이·DNS를 임대받는지와 서버 lease를 함께 확인합니다. UDP67/68, 올바른 NIC 선택, 고정 IP를 점검합니다. 원격 접속에 쓰는 NIC를 바꾸며 연습하지 마세요.

## 정리와 도움말

Squid는 추가 ACL을 제거하고 기존 설정으로 reload합니다. DHCP 서버는 실습 종료 후 중지하고 격리 네트워크를 유지하거나 스냅샷을 복원합니다.

도움말: `man squid`, `rpm -qd squid`, `man dhcpd.conf`, `man dhcpd`. [Squid 버전별 지시어](https://www.squid-cache.org/Doc/config/), [ISC DHCP 문서](https://kb.isc.org/docs/isc-dhcp-44-manual-pages-dhcpdconf).
