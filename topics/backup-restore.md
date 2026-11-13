# 백업·복원: tar / cpio / rsync / dd / dump / xfsdump

## 어떤 단위를 다루는가

| 도구 | 주된 관점 | 선택 기준 |
|---|---|---|
| tar / cpio | 파일·디렉터리 묶음 | 필요한 파일을 아카이브로 보관 |
| rsync | 파일 트리 비교·전송 | 변경분 동기화와 원격 복사 |
| dd | 입력 바이트·블록 복사 | 장치 이미지, 정확한 블록 복제 |
| dump / restore | 지원하는 파일시스템 구조 | 주로 ext 계열의 레벨 백업·복원 |
| xfsdump / xfsrestore | XFS 파일시스템 | XFS의 전체·증분 백업 |

`/dev/sdb1`이라는 같은 경로를 받아도 읽는 방식이 다릅니다. `dd`는 파일시스템을 이해하지 않고 바이트를 복사합니다. dump는 지원하는 파일시스템의 메타데이터를 이해해서 파일을 백업합니다. 장치 경로 자체가 파일시스템의 이름은 아닙니다.

## tar: 만들기·목록·풀기

홈의 연습 파일만 사용합니다.

```bash
mkdir -p ~/backup-lab/source ~/backup-lab/restored
printf 'sample data\n' > ~/backup-lab/source/a.txt
tar -czf ~/backup-lab/data.tar.gz -C ~/backup-lab source
tar -tzf ~/backup-lab/data.tar.gz
tar -xzf ~/backup-lab/data.tar.gz -C ~/backup-lab/restored
diff -r ~/backup-lab/source ~/backup-lab/restored/source
```

`c` 생성, `t` 목록, `x` 추출, `f` 아카이브 파일 지정, `v` 상세 출력입니다. `z` gzip, `j` bzip2, `J` xz입니다. 예: `tar -xjf 파일.tar.bz2`, `tar -xJf 파일.tar.xz`. `-C`는 작업 디렉터리 변경입니다. 아카이브를 먼저 목록으로 검사하고 빈 폴더에 추출합니다. 파일 권한·ACL·SELinux·확장 속성까지 보존해야 한다면 `--acls --xattrs --selinux` 등의 지원과 권한도 검토합니다.

## cpio: 파일 목록을 입력받기

```bash
cd ~/backup-lab/source
find . -print0 | cpio --null -ov -H newc > ../data.cpio
cpio -itv < ../data.cpio
cd ~/backup-lab/restored
cpio -idmv < ../data.cpio
```

위 복원은 같은 이름의 기존 파일이 없는 새 복원 폴더를 사용합니다. `-o` copy-out(생성), `-i` copy-in(추출), `-t` 목록, `-d` 필요한 디렉터리 생성, `-m` 수정 시각 보존, `-H newc` 형식 지정입니다. `-F 파일`로 리다이렉션 대신 아카이브를 지정할 수 있습니다. `find -print0`와 `cpio --null`은 공백·줄바꿈이 있는 이름을 안전하게 전달합니다. 단순 `find . -print | cpio -ov` 형태와 옵션 의미도 연결하세요.

## rsync: 끝의 슬래시

```bash
rsync -av --dry-run ~/backup-lab/source/ ~/backup-lab/synced/
rsync -av ~/backup-lab/source/ ~/backup-lab/synced/
rsync -avz -e ssh ~/backup-lab/source/ labuser@192.0.2.30:/home/labuser/backup/
```

`source/`는 디렉터리 안의 내용, `source`는 디렉터리 자체를 복사하는 차이가 있습니다. `-a`는 재귀·다수 속성을 보존하는 archive 모드, `-v`는 상세, `-z`는 전송 압축입니다. `-a`만으로 ACL·xattr·하드 링크까지 모두 보존되지는 않습니다. `--delete`는 목적지의 파일을 삭제할 수 있으므로 조건이 요구할 때만 dry-run 후 사용합니다.

## dd: 입력과 출력 반대로 쓰지 않기

장치 백업 예시 **설명용**입니다. 대상·공간·마운트 상태를 확인한 뒤 별도로 실습합니다.

```bash
# 입력: 마운트 해제된 원본 파티션 / 출력: 다른 파일시스템의 이미지
sudo dd if=/dev/sdb1 of=/backup/lab-partition.img bs=4M status=progress conv=fsync
# 복원: 데이터를 지울 빈 대상 파티션. 원본보다 작으면 안 됩니다.
sudo dd if=/backup/lab-partition.img of=/dev/sdc1 bs=4M status=progress conv=fsync
```

`if` input, `of` output, `bs` 한 번에 읽고 쓸 단위, `count` 블록 개수입니다. 디스크 전체 `/dev/sdb`를 이미지로 만들면 파티션 테이블도 포함하지만 파티션 `/dev/sdb1` 이미지는 일반적으로 포함하지 않습니다. 사용 중인 파일시스템을 dd로 복사하면 일관성이 깨질 수 있으므로 해제하거나 적절한 스냅샷을 사용합니다. 백업 파일은 원본 파티션 안에 만들지 않습니다. 복제하면 UUID도 같아질 수 있어 동시에 연결할 때 주의합니다.

dd는 일반 파일도 입력으로 받습니다. ASCII 대소문자 변환 예:

```bash
printf 'alpha\n' > ~/backup-lab/lower.txt
dd if=~/backup-lab/lower.txt of=~/backup-lab/upper.txt conv=ucase status=none
cat ~/backup-lab/upper.txt
```

소문자 변환은 `conv=lcase`입니다. 유니코드 일반 변환기로 생각하지 마세요.

## dump / restore

먼저 `findmnt -T /mnt/labext`, `lsblk -f`로 파일시스템 종류를 확인합니다. **XFS에는 xfsdump를 사용합니다.** 다음은 ext 계열의 전용 실습 파일시스템과 외부 백업 저장소가 준비되었다는 가정입니다.

```bash
sudo dump -0u -f /backup/labext.full.dump /dev/sdb1
sudo restore -t -f /backup/labext.full.dump
mkdir -p ~/restore-ext
cd ~/restore-ext
sudo restore -r -f /backup/labext.full.dump
```

`-0`은 전체 백업 레벨, `-u`는 성공 시 dumpdates 갱신, `-f`는 출력 파일/장치입니다. 레벨 1–9는 더 낮은 레벨의 최근 백업 이후 변경분을 다룹니다. `restore -r`는 전체 파일시스템 복원용, `-x`는 선택 추출, `-i`는 대화형, `-t`는 목록입니다. 증분 복원은 전체 백업과 필요한 증분을 올바른 순서로 적용해야 합니다.

dump는 구현에 따라 파일시스템의 마운트 경로나 그 안의 파일·디렉터리를 입력받는 **부분 백업**도 지원합니다. 따라서 “파일 입력은 절대 불가능”이라고 외우지 않습니다. Rocky 8.9에서 확인한 dump 매뉴얼은 부분 백업에 **레벨0만 허용, -u 불가, 동일 파일시스템의 파일만 사용**이라는 제한을 명시합니다. tar처럼 서로 다른 파일시스템 파일들을 자유롭게 한데 묶는 도구로 이해하면 안 됩니다. 일관된 백업에는 파일시스템 정지·해제·스냅샷 정책도 필요합니다.

## xfsdump / xfsrestore

XFS가 `/mnt/labxfs`에 마운트되어 있고 `/backup`이 별도 저장소일 때:

```bash
sudo xfsdump -l 0 -L lab-full -M file -f /backup/labxfs.full.xdump /mnt/labxfs
sudo xfsdump -l 1 -L lab-inc -M file -f /backup/labxfs.inc.xdump /mnt/labxfs
mkdir -p ~/restore-xfs
sudo xfsrestore -f /backup/labxfs.full.xdump ~/restore-xfs
sudo xfsrestore -f /backup/labxfs.inc.xdump ~/restore-xfs
```

`-l`은 레벨, `-L`은 세션 라벨, `-M`은 미디어 라벨, `-f`는 백업 파일입니다. xfsrestore의 `-t`는 내용 조회, `-i`는 대화형 복원에 사용합니다. 특정 파일·하위 트리는 `xfsdump -s`의 경로 규칙과 제한을 확인합니다. 증분은 기반 전체 백업이 없으면 독립적인 완전 복원이 되지 않습니다. 열린 파일의 응용프로그램 상태까지 자동 보장하지 않으므로 DB 등은 별도 일관성 절차가 필요합니다.

## 검증과 정리

아카이브 목록 확인 → **새 경로로 복원** → `diff`, `sha256sum`, 권한·소유자 비교 순서로 확인합니다. 백업 명령의 성공 메시지만 보고 끝내지 않습니다. 홈의 `backup-lab`과 복원 폴더를 정리하고, 블록 장치 실습은 스냅샷으로 되돌립니다.

도움말: `man tar`, `man cpio`, `man rsync`, `man dd`, `man dump`, `man restore`, `man xfsdump`, `man xfsrestore`.
