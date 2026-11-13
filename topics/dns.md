# BIND DNS: named.conf와 정·역방향 zone

## 조건을 네 가지로 나누기

1. 어느 영역을 관리하는가: `example.test` 또는 `2.0.192.in-addr.arpa`.
2. 어느 파일을 읽는가: named.conf의 `zone`과 `file`.
3. 어떤 정보를 답하는가: A, AAAA, NS, MX, CNAME, PTR.
4. 적용 후 무엇으로 확인하는가: named-checkconf → named-checkzone → dig.

`/etc/named.conf`는 서버 설정, `/var/named/` 아래 zone 파일은 도메인 데이터입니다. `options { directory "/var/named"; };`이면 `file "example.test.zone";`은 그 디렉터리를 기준으로 해석됩니다. chroot를 사용하는 패키지는 보이는 경로와 실제 루트가 다를 수 있습니다.

## named.conf 영역 선언

```bind
zone "example.test" IN {
    type master;
    file "example.test.zone";
    allow-update { none; };
};
zone "2.0.192.in-addr.arpa" IN {
    type master;
    file "192.0.2.rev";
    allow-update { none; };
};
```

Rocky 8 계열 BIND에서 흔한 `master` 문법을 사용합니다. 최신 문서는 `primary`라는 용어도 사용합니다. 중괄호와 문장 끝 세미콜론을 확인하세요. `allow-query`는 질의 허용, `allow-transfer`는 zone 전송 허용, `allow-update`는 동적 갱신 허용으로 역할이 다릅니다. 실습 서버를 인터넷에 무제한 재귀 DNS로 열지 않습니다.

전달·접근 관련 구문도 별도로 읽습니다.

```bind
acl labnet { 127.0.0.1; 192.0.2.0/24; };
options {
    directory "/var/named";
    listen-on port 53 { 127.0.0.1; 192.0.2.10; };
    allow-query { labnet; };
    recursion yes;
    allow-recursion { labnet; };
    forwarders { 192.0.2.53; };
    forward first;
    allow-transfer { none; };
};
```

이 options는 구조 설명용이며 실제 서버의 기존 options 블록과 합쳐야 합니다. listen-on 주소는 서버에 존재해야 하고 forwarder는 실제 동작하는 연습용 DNS여야 합니다. `forward first`는 전달 질의 실패 때 자체 재귀를 시도할 수 있고 `forward only`는 지정 전달 서버에 의존합니다. `recursion no`는 재귀 서비스를 끄며 보유한 권한 zone 질의 자체를 끈다는 뜻은 아닙니다. 전역 옵션과 zone별 옵션의 적용 범위도 구분합니다.

## 정방향 예제

실제 파일은 [examples/dns/example.test.zone](../examples/dns/example.test.zone)에 있습니다.

```dns
$TTL 1h
@ IN SOA ns1.example.test. hostmaster.example.test. (
    2026111401 ; serial
    1h         ; refresh
    15m        ; retry
    1w         ; expire
    5m )       ; negative caching TTL
  IN NS ns1.example.test.
  IN MX 10 mail.example.test.
ns1  IN A 192.0.2.10
mail IN A 192.0.2.20
web  IN A 192.0.2.30
www  IN CNAME web.example.test.
```

`@`는 현재 origin(여기서는 example.test), `$TTL`은 레코드 TTL 기본값입니다. 소유자 칸을 생략하면 앞 레코드의 소유자를 이어받으므로 NS·MX는 zone apex에 속합니다. 들여쓰기는 의미가 있습니다.

SOA의 첫 이름은 주 네임서버, 두 번째는 관리 이메일을 DNS 이름 형식으로 나타낸 값입니다. `hostmaster.example.test.`는 보통 `hostmaster@example.test`를 뜻합니다. serial은 갱신할 때 증가시키는 버전이고 날짜 모양이 필수는 아닙니다. refresh는 보조 서버의 갱신 확인 간격, retry는 실패 후 재시도, expire는 갱신하지 못한 데이터의 유효 한계입니다. SOA 마지막 필드는 현대 DNS에서 negative caching TTL 결정에 사용되며 모든 레코드의 기본 TTL과 같다고 외우지 않습니다.

**끝의 점**은 절대 이름을 뜻합니다. `web`은 `web.example.test.`로 보완되지만, 점 없는 `web.example.test`는 잘못하면 `web.example.test.example.test.`가 됩니다. MX의 숫자는 작을수록 우선입니다. MX 대상에는 일반적으로 직접 A/AAAA가 있는 호스트 이름을 쓰고 IP 주소를 바로 넣지 않습니다. CNAME 이름에는 다른 일반 데이터 레코드를 함께 두지 않습니다.

## 역방향 예제

`192.0.2.0/24`의 zone은 옥텟 순서를 뒤집은 `2.0.192.in-addr.arpa`입니다.

```dns
$TTL 1h
@ IN SOA ns1.example.test. hostmaster.example.test. (
    2026111401 1h 15m 1w 5m )
  IN NS ns1.example.test.
10 IN PTR ns1.example.test.
20 IN PTR mail.example.test.
30 IN PTR web.example.test.
```

정방향 A 레코드가 있다고 PTR이 자동 생성되지는 않습니다. `/24`가 아닌 위임은 별도 기법이 필요할 수 있으므로 무조건 마지막 옥텟 하나만 쓰는 규칙으로 일반화하지 않습니다.

## 시스템에 적용하지 않고 문법 연습

저장소 최상위에서:

```bash
named-checkzone example.test examples/dns/example.test.zone
named-checkzone 2.0.192.in-addr.arpa examples/dns/192.0.2.rev
named-checkconf examples/dns/named-check.conf
```

이것은 제공 예제의 구문 검사입니다. 실제 DNS 서버를 변경하거나 실행하지 않습니다. 의도적으로 `www` 대상의 끝 점을 지우고 검사 결과·질의 결과 차이를 비교하되, 검사기가 모든 논리 오류를 잡는다고 기대하면 안 됩니다.

## VM 서비스에 적용하는 별도 단계

`bind bind-utils`를 설치하고 기존 설정을 보관합니다. 예제 zone을 `/var/named/`에 배치하고 `root:named`, 읽기 권한과 SELinux 라벨(`restorecon`)을 확인합니다. 기존 named.conf의 options와 접근 범위를 유지하며 zone 선언만 추가합니다.

```bash
sudo named-checkconf
sudo named-checkconf -z
sudo named-checkzone example.test /var/named/example.test.zone
sudo systemctl reload named
dig @127.0.0.1 web.example.test A
dig @127.0.0.1 example.test MX
dig @127.0.0.1 -x 192.0.2.30
```

서비스가 꺼졌다면 검사 후 start합니다. `dig`에서 `status: NOERROR`, ANSWER 값, 권한 서버의 `aa` 플래그를 확인합니다. `NXDOMAIN`은 이름 부재, `NOERROR`이면서 답이 비어 있는 경우는 해당 타입 부재일 수 있습니다. 외부 VM 질의에는 listen-on·allow-query·UDP/TCP53 방화벽·네트워크가 모두 맞아야 합니다.

실습 후 추가한 zone·설정만 제거하고 reload하거나 스냅샷을 복원합니다. 이 가이드는 독자적인 예제로 개념을 설명하며 각 기출의 실제 도메인·주소·빈칸은 원문 조건에 대입해야 합니다.

도움말: `man named.conf`, `man named-checkconf`, `man named-checkzone`, `man dig`, [BIND 문서](https://bind9.readthedocs.io/en/v9.16.50/).
