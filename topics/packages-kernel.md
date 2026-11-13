# DNF·RPM·gcc·커널·모듈

## DNF와 RPM의 관점

DNF는 저장소와 의존성을 고려해 패키지를 관리합니다. RPM은 설치 DB나 개별 rpm 파일을 직접 조회·조작합니다. Rocky 8의 `yum`은 DNF 기반 호환 명령이며, 문항이 특정 명령을 지정하면 그 명령의 문법으로 답합니다.

```bash
dnf search httpd
dnf info httpd
dnf list installed
dnf list available
dnf repolist --all
dnf history
dnf provides '*/named-checkzone'
sudo dnf install bind bind-utils
sudo dnf clean all
```

`info`는 설명·버전·저장소 등의 상세, `list`는 패키지 목록입니다. 설치 전 저장소 도달 여부와 패키지 이름을 확인합니다. `dnf --enablerepo=저장소ID install 패키지`는 해당 실행에서 저장소를 켜는 예입니다. 영구 활성화는 `dnf config-manager --set-enabled 저장소ID`이며 `dnf-plugins-core`가 필요할 수 있습니다. 저장소 ID는 `repolist --all`에서 확인합니다.

| 명령 | 대상과 의미 |
|---|---|
| `rpm -qa` | 설치된 패키지 전체 |
| `rpm -qi bash` | 설치 패키지 정보 |
| `rpm -ql bash` | 설치된 파일 목록 |
| `rpm -qc bash` | 설정 파일 목록 |
| `rpm -qR bash` | 필요한 의존성 |
| `rpm -qf /usr/bin/bash` | 이 파일을 제공한 설치 패키지 |
| `rpm -qip ./package.rpm` | 설치 전 rpm 파일 정보 |
| `rpm -qlp ./package.rpm` | 설치 전 rpm 파일의 파일 목록 |
| `rpm -V bash` | 설치 DB와 현재 파일 속성 비교 |

`rpm -e 패키지`는 삭제입니다. `--nodeps`는 의존성 검사를 생략하므로 학습용 옵션 식별과 실제 권장 운영 절차를 구분합니다. `dnf history undo ID`도 저장소에 필요한 구버전이 없으면 실패할 수 있습니다.

## gcc: 소스 → 오브젝트 → 실행 파일

```bash
gcc -Wall -c calc.c -o calc.o
gcc -Wall -c runner.c -o runner.o
gcc calc.o runner.o -o labcalc
./labcalc
```

`-c`는 컴파일 후 오브젝트까지 만들고 링크하지 않는 옵션, `-o`는 출력 이름입니다. `.c` 파일 여러 개를 한 명령으로 링크할 수도 있습니다. 파일 개수보다 “오브젝트만 필요한가 / 실행 파일이 필요한가”를 먼저 읽으세요. 압축 해제는 [백업 가이드](backup-restore.md)의 tar 옵션과 연결됩니다.

## make 뒤의 목표 찾기

`make`는 현재 프로젝트의 Makefile을 읽습니다. `menuconfig`, `bzImage`는 모든 프로젝트가 공통으로 제공하는 하위 명령이 아닙니다.

```bash
pwd
ls -l Makefile
make help
grep -nE '^(help|menuconfig|bzImage|modules|modules_install|clean|mrproper|distclean)[[:space:]:]' Makefile
```

위 grep은 눈에 보이는 선언을 찾는 보조 도구이며 include·패턴·변수로 생성한 모든 목표를 완전히 열거하지 못합니다. `make -n 목표`는 실행할 작업을 미리 보는 데 쓸 수 있지만 재귀 make 등이 일부 실행될 수 있어 낯선 소스를 안전하게 실행하는 장치는 아닙니다.

커널 소스가 `/usr/src/linux-4.18`에 풀려 있다는 가정:

```bash
make -C /usr/src/linux-4.18 help
uname -r
ls -ld /usr/src/* /lib/modules/"$(uname -r)"/build
```

소스 경로는 설치 상태에 따라 없을 수 있습니다. `kernel-devel`은 외부 모듈 빌드를 위한 파일을 제공하지만 일반적인 전체 커널 소스 tarball과 같지 않습니다. 배포판 실행 커널과 upstream 같은 숫자의 소스도 패치 수준이 다릅니다. 제공 경로가 있는지 직접 확인하세요.

| 커널 목표 | 의미 |
|---|---|
| `make clean` | 주로 빌드 산출물 정리, 설정은 보존 |
| `make mrproper` | 설정 `.config` 등도 정리 |
| `make distclean` | mrproper에 더해 배포 전 정리 작업 |
| `make menuconfig` | 대화형 설정. ncurses 개발 도구 등이 필요 |
| `make bzImage` | x86 커널 이미지 빌드 |
| `make modules` | 모듈 빌드 |
| `make modules_install` | 모듈 설치. 권한·대상 커널 경로 주의 |

학습 순서는 소스 확보 → 기존 설정 보관 → 필요 시 정리 → 설정 → 이미지·모듈 빌드입니다. 모든 실습에서 실제 설치·부팅 변경까지 할 필요는 없습니다. `distclean`은 저장한 설정도 지우므로 순서를 조심하세요. 커널 이미지의 `bzImage`는 bzip2 압축 파일이라는 뜻이 아닙니다.

## 모듈과 하드웨어 정보

```bash
lsmod
modinfo xfs
modprobe --showconfig | less
cat /proc/cpuinfo
cat /proc/meminfo
cat /proc/version
cat /proc/mdstat
```

`lsmod`는 적재된 모듈, `modinfo`는 모듈 정보, `insmod 파일.ko`는 파일을 직접 적재, `modprobe 모듈명`은 의존성을 고려한 적재입니다. 제거는 `rmmod 이름` 또는 `modprobe -r 이름`입니다. 여러 모듈을 적재하려면 `modprobe -a 이름1 이름2`를 사용할 수 있습니다. 스토리지·네트워크에 사용 중인 모듈을 연습 삼아 제거하지 마세요.

`depmod -a`는 `/lib/modules/커널버전/`의 의존성 DB를 갱신합니다. 관련 파일은 `modules.dep`와 `modules.dep.bin`입니다. 설정은 `/etc/modprobe.d/*.conf`이며 `alias 별칭 모듈명`, `options 모듈명 옵션=값`, `blacklist 모듈명` 등을 확인합니다. blacklist가 모든 명시적 적재까지 절대 차단하는 것은 아닙니다.

## 검증·정리

패키지는 `rpm -q 패키지`, 소유 파일은 `rpm -ql`, 소스 목표는 `make help`, 빌드 결과는 생성 파일과 반환값으로 검증합니다. 커널 설치·모듈 제거는 이 자료를 읽는 것만으로 자동 수행되지 않습니다. 설정 변경은 스냅샷으로 되돌립니다.

도움말: `man dnf`, `man rpm`, `man gcc`, `man make`, `man modprobe`, `man modinfo`. [GNU Make 매뉴얼](https://www.gnu.org/software/make/manual/make.html), [커널 빌드 문서](https://docs.kernel.org/kbuild/).
