# Sendmail 메일 설정

## 경로부터 구분하기

Rocky의 기본 메일 전송기가 반드시 Sendmail인 것은 아닙니다. `rpm -q sendmail sendmail-cf postfix`, `systemctl status sendmail`로 확인하세요. Postfix의 설정 파일에 Sendmail 지시어를 넣는 방식으로 연습하지 않습니다.

| 경로 | 용도 | 바꾼 뒤 할 일 |
|---|---|---|
| `/etc/aliases` | 로컬 수신 이름의 별칭 | `newaliases` |
| `/etc/mail/virtusertable` | 가상 도메인별 수신 주소 매핑 | `makemap hash` |
| `/etc/mail/local-host-names` | 이 서버가 최종 수신할 도메인 목록 | Sendmail 설정 재적용 |
| `/etc/mail/access` | 접근·중계 정책 맵 | `makemap hash` 또는 패키지 Makefile |
| `/etc/mail/sendmail.mc` | 사람이 편집하는 m4 설정 소스 | sendmail.cf 재생성 |
| `/etc/mail/sendmail.cf` | Sendmail이 읽는 생성 설정 | 직접 편집과 생성 방식을 혼동하지 않기 |
| `~/.forward` | 개인 계정의 전달 설정 | 계정·권한 정책 확인 |

## aliases: 로컬 이름의 별칭

```text
# /etc/aliases에 넣을 연습용 항목
labhelp: labuser
labstaff: labuser, labadmin
labcourse: :include:/etc/mail/lab-members
```

```bash
sudo newaliases
```

콜론 왼쪽은 별칭, 오른쪽은 실제 수신 대상입니다. `newaliases`는 별칭 DB를 다시 만듭니다. 텍스트만 바꾸고 DB를 갱신하지 않으면 이전 정보가 사용될 수 있습니다. 별칭은 일반적으로 로컬 이름 기준이므로 도메인마다 같은 사용자명을 다른 사람에게 보내는 조건은 virtusertable과 연결됩니다.

`:include:`는 별도 파일에서 수신 대상 목록을 읽습니다. 예제라면 `/etc/mail/lab-members` 파일을 실제로 만들고 안전한 소유자·권한을 설정해야 합니다. `sendmail -bi`도 별칭 DB 재생성과 관련됩니다.

## virtusertable: 수신 주소 → 실제 대상

```text
# /etc/mail/virtusertable
help@alpha.example.test labuser
help@beta.example.test labadmin
@alpha.example.test labuser
```

```bash
sudo sh -c 'makemap hash /etc/mail/virtusertable < /etc/mail/virtusertable'
```

왼쪽은 가상 수신 주소, 오른쪽은 실제 계정/대상입니다. `@도메인`은 해당 도메인의 나머지 주소를 처리하는 포괄 규칙입니다. 실제 운영에서는 오타 주소를 전부 수신하게 되는 정책까지 고려합니다. `.db` 파일을 편집하는 것이 아니라 텍스트 맵을 바꾸고 DB를 생성합니다. 해당 기능을 쓰도록 sendmail.mc에 설정되어 있는지도 확인합니다.

`/etc/mail/local-host-names`에는 수신할 도메인을 한 줄씩 적습니다. 이것은 DNS MX 설정을 대신하지 않습니다. `FEATURE(virtusertable)` 등의 m4 기능, 수신 도메인, 맵 DB, 실제 Unix 계정이 서로 맞아야 합니다.

## access: 수신과 중계를 구분하기

access 맵의 `RELAY`, `REJECT`, `DISCARD`, `OK`는 역할이 다릅니다. 예를 들어 내부 특정 호스트에만 RELAY를 허용하는 설정과 이 서버가 최종 목적지인 메일을 받는 설정을 구분하세요. 모든 외부 주소에 RELAY를 허용하는 개방형 중계 설정으로 연습하지 않습니다.

```bash
sudo sh -c 'makemap hash /etc/mail/access < /etc/mail/access'
```

`From:blocked.example.test REJECT`는 발신 주소에 대한 거절 예, `Connect:192.0.2.99 DISCARD`는 접속 출처에 대한 처리 예입니다. REJECT는 오류 응답으로 거부, DISCARD는 수락한 것처럼 보이면서 폐기하는 정책이라 다릅니다. 사용할 태그·기능은 설치 버전의 access_db 문서를 확인합니다. 구형 기출의 sendmail.cf `Dj호스트명`은 이 서버의 공식 호스트명 설정과 관련되며 수신 도메인 전체 목록을 뜻하지 않습니다.

## 생성·조회·검증

배포판에 Makefile이 제공되면 내용을 확인한 뒤 `sudo make -C /etc/mail`로 생성할 수 있습니다. `sendmail-cf`가 필요할 수 있습니다. `m4 /etc/mail/sendmail.mc > ...`의 출력은 임시 파일로 만들고 성공 여부를 확인한 뒤 반영합니다. 리다이렉션 실패로 기존 설정을 빈 파일로 만드는 일을 피하세요.

```bash
sendmail -bp
sudo sendmail -bv labhelp
sudo sendmail -bt
sudo journalctl -u sendmail --since '-10 min'
sudo tail /var/log/maillog
```

`-bp`는 큐, `-bv`는 수신 주소 확인, `-bt`는 주소 규칙 시험 모드입니다. `-bv` 결과만으로 실제 외부 배송까지 성공했다고 판단하지 않습니다. 실제 연습은 격리된 VM 계정에만 보내고 수신 파일·로그를 함께 확인합니다. 서비스 재적용은 환경의 unit을 확인하고 `systemctl restart sendmail` 등으로 수행합니다.

실습 후 텍스트 설정을 복원하고 DB도 다시 생성합니다. `.mc`만 복원하고 `.cf`를 재생성하지 않으면 상태가 어긋납니다. 외부 인터넷 메일 전송에는 DNS·라우팅·중계 정책 등이 추가로 필요합니다.

도움말: `man aliases`, `man newaliases`, `man makemap`, `man sendmail`, 설치된 `sendmail-cf` 문서. [Sendmail 공식 사이트](https://www.sendmail.org/).
