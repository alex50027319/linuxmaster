# 출처와 자료 범위

확인일: 2026-11-14. 기술 설명과 예제는 이 저장소를 위해 직접 작성했습니다. 설치된 프로그램의 버전별 man·패키지 문서를 우선 확인하세요.

## 기출 색인의 출처

- dev-centralpark, [리눅스마스터 1급 2차 실기 기출 모음](https://dev-centralpark.tistory.com/51).
- 확인한 회차: 2601, 2502, 2501, 2402, 2401, 2201, 2102, 2101, 2003, 2002, 2001. 각 16문항으로 총 176문항입니다. 이 목록은 해당 페이지의 수록 범위이며 모든 연도·모든 회차가 있다는 뜻은 아닙니다.
- 페이지에 표시된 최근 정정일은 2026-11-02입니다. 이후 원문 수정은 이 색인에 자동 반영되지 않습니다.
- `coverage.csv`에는 회차·문항 번호·주제 연결·출처 URL만 제공합니다. 원문 문장·그림·정답표·원문 HTML은 배포하지 않습니다. 원문에 안정적인 문항별 앵커가 없어서 회차와 번호로 직접 찾습니다.
- 원문 페이지의 [CC BY-NC-ND 4.0 안내](https://creativecommons.org/licenses/by-nc-nd/4.0/deed.ko)는 원문에 적용됩니다. 이 저장소의 독자적 예제와 혼동하지 마세요. 공식 시험 답안과 블로그 해설도 구분해야 합니다.

## 기술 문서

| 주제 | 1차 문서·로컬 도움말 |
|---|---|
| GNU 도구 | [Coreutils](https://www.gnu.org/software/coreutils/manual/coreutils.html), [Findutils](https://www.gnu.org/software/findutils/manual/html_mono/find.html), [tar](https://www.gnu.org/software/tar/manual/tar.html), [cpio](https://www.gnu.org/software/cpio/manual/cpio.html), [Make](https://www.gnu.org/software/make/manual/make.html) |
| 파일시스템 | [RHEL 8 Managing file systems](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html-single/managing_file_systems/index), `man xfs_quota`, `man quotacheck`, `man fstab` |
| 파티션 | [GNU Parted](https://www.gnu.org/software/parted/manual/parted.html), `man fdisk`, `man parted` |
| RAID·LVM | `man mdadm`, `man lvm`, `man pvcreate`, `man vgcreate`, `man lvcreate` |
| 백업 | [dump/restore upstream](https://dump.sourceforge.io/), `man dump`, `man restore`, `man xfsdump`, `man xfsrestore`, `man rsync` |
| 커널 | [kernel.org](https://www.kernel.org/), [Kbuild](https://docs.kernel.org/kbuild/), 각 소스의 `make help` |
| 로그 | [rsyslog 문서](https://www.rsyslog.com/doc/), `man rsyslog.conf`, `man logrotate`, `man last`, `man ipcs` |
| Apache | [Apache 2.4 문서](https://httpd.apache.org/docs/2.4/), [인증](https://httpd.apache.org/docs/2.4/howto/auth.html) |
| DNS | [BIND 9.16 문서](https://bind9.readthedocs.io/en/v9.16.50/), `man named.conf`, `man named-checkzone` |
| Samba | [공식 매뉴얼](https://www.samba.org/samba/docs/current/man-html/), [smb.conf](https://www.samba.org/samba/docs/current/man-html/smb.conf.5.html) |
| NFS·FTP | `man exports`, `man exportfs`, `man vsftpd.conf`; 설치된 패키지의 문서 |
| 메일 | [Sendmail](https://www.sendmail.org/), `man sendmail`, `man aliases`, `man makemap`, sendmail-cf 패키지 문서 |
| Squid | [버전별 지시어](https://www.squid-cache.org/Doc/config/), [RHEL 8 Squid](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html/deploying_different_types_of_servers/configuring-the-squid-caching-proxy-server_deploying-different-types-of-servers), 설치된 squid.conf.documented |
| DHCP | [ISC dhcpd.conf](https://kb.isc.org/docs/isc-dhcp-44-manual-pages-dhcpdconf), `man dhcpd.conf`. ISC DHCP는 EOL이므로 이 자료는 기출·격리 실습 목적의 문법을 다룹니다. |
| 방화벽·SSH | [firewalld 문서](https://firewalld.org/documentation/), [OpenSSH 매뉴얼](https://www.openssh.com/manual.html), `man iptables`, `man sshd_config` |
| 구형 기능 제거 | [RHEL 8.0 릴리스 노트](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html/8.0_release_notes/rhel-8_0_0_release), TCP Wrapper 제거 항목 |
| GitHub 다운로드 | [소스 아카이브 다운로드](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives) |
| 시험 공식 안내 | [KAIT 리눅스마스터](https://www.ihd.or.kr/). 해당 회차 환경·규칙은 별도 확인 |

이 저장소의 색인은 원문 수록 문항의 **주제 분석**입니다. 문항별 모든 빈칸의 공식 채점 기준·부분 점수·대체 답안 인정 범위를 보증하지 않습니다. 예제의 사용자·주소·경로는 독립적으로 정한 값이므로 원문 조건을 그대로 대입해야 합니다.
