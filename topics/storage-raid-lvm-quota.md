# 디스크·파티션·파일시스템·RAID·LVM·쿼터

## 먼저 구분하기

`/dev/sdb`는 디스크 장치, `/dev/sdb1`은 그 디스크의 파티션 장치입니다. **파티션 장치 자체가 파일시스템이라는 뜻은 아닙니다.** 파티션 안에 ext4·XFS·swap·RAID 구성원 등을 넣을 수 있습니다. 파일시스템을 디렉터리에 연결하는 작업이 mount입니다.

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL
sudo fdisk -l
sudo blkid
findmnt /
cat /proc/partitions
```

SATA/SCSI 계열은 sda…sdz, sdaa…처럼 이름이 늘어날 수 있습니다. NVMe는 `/dev/nvme0n1`, 파티션은 `/dev/nvme0n1p1`입니다. 이름은 연결·탐색 순서에 따라 바뀔 수 있어 영구 마운트에는 UUID를 사용합니다. 하드웨어 RAID가 논리 디스크 하나를 제공하면 물리 디스크 여러 개가 리눅스에서 장치 하나로 보일 수 있습니다. NFS/SMB NAS는 보통 디렉터리 공유로 마운트하고, iSCSI는 블록 장치를 제공한다는 차이가 있습니다.

## fdisk 방식: GPT 파티션 → ext4 → mount

**아래는 `/dev/sdb`가 비어 있는 추가 연습 디스크일 때만 실행합니다.** 시스템 디스크에서는 실행하지 않습니다. 파티션 테이블 생성·포맷은 데이터를 지웁니다.

```text
$ sudo fdisk /dev/sdb
Command (m for help): p
Command (m for help): g
Command (m for help): n
Partition number: [Enter]
First sector: [Enter]
Last sector: [Enter]
Command (m for help): p
Command (m for help): w
```

`g`는 GPT 새로 만들기, `n`은 새 파티션, `p`는 확인, `w`는 쓰기입니다. 저장하기 전 취소는 `q`입니다. MBR을 요구하는 문제라면 `o`와 primary/extended 등 MBR 조건을 따릅니다. 메뉴·기본값은 버전에 따라 다르므로 `m`을 확인합니다.

```bash
sudo partprobe /dev/sdb
lsblk -f /dev/sdb
sudo mkfs.ext4 /dev/sdb1
sudo mkdir -p /mnt/labdata
sudo mount /dev/sdb1 /mnt/labdata
findmnt /mnt/labdata
df -hT /mnt/labdata
```

`partprobe` 후 커널이 사용 중이라 갱신하지 못하면 오류를 확인하고 재부팅 여부를 판단합니다. 새 장치가 보이지 않는데 포맷부터 진행하지 마세요.

## parted 방식: 같은 목표의 별도 실습

앞 실습을 한 디스크에 아래 명령을 그대로 이어서 실행하면 다시 초기화됩니다. **스냅샷을 복원하거나 다른 빈 연습 디스크를 사용합니다.**

```text
$ sudo parted /dev/sdb
(parted) print
(parted) mklabel gpt
(parted) mkpart labdata ext4 1MiB 100%
(parted) print
(parted) quit
```

```bash
sudo partprobe /dev/sdb
sudo mkfs.ext4 /dev/sdb1
sudo mkdir -p /mnt/labdata
sudo mount /dev/sdb1 /mnt/labdata
findmnt /mnt/labdata
```

`mkpart ... ext4`의 ext4는 파티션 종류를 정하는 힌트이며 ext4 파일시스템을 만들지 않습니다. 실제 생성은 `mkfs.ext4`입니다. `mkpart ... xfs`로 만들었어도 나중에 `mkfs.ext4`를 실행할 수 있습니다. 기존 내용이 있다면 포맷 과정에서 지워지며, 이름·유형 표기와 실제 파일시스템을 `blkid`로 구분해야 합니다. `parted`는 대다수 변경을 바로 적용하므로 fdisk처럼 마지막 `w`가 필요하지 않습니다. 삭제는 `rm 번호`, 끝 위치 변경은 `resizepart 번호 끝위치`이며 파일시스템 크기는 별도로 처리해야 합니다.

## 영구 마운트·점검·swap

`sudo blkid /dev/sdb1` 결과의 실제 UUID로 `/etc/fstab`에 추가합니다.

```fstab
UUID=실제-UUID /mnt/labdata ext4 defaults 0 2
```

기존 fstab을 보관하고 `sudo findmnt --verify --verbose`로 검사합니다. 연습 파티션만 `sudo umount /mnt/labdata`, `sudo mount /mnt/labdata`로 다시 마운트한 뒤 파일이 유지되는지 확인합니다. 부팅 디스크 검사·변경을 연습에 섞지 마세요.

ext 계열 오프라인 검사는 `e2fsck /dev/sdb1` 또는 `fsck -t ext4 /dev/sdb1`, XFS는 `xfs_repair /dev/sdb1`입니다. **마운트를 해제한 파일시스템**에서 수행합니다. XFS를 `fsck.xfs`로 실제 수리한다고 생각하면 안 됩니다. XFS는 `xfs_growfs 마운트경로`로 확장하며 일반적인 축소를 지원하지 않습니다. ext4 축소는 파일시스템을 먼저 축소한 뒤 파티션을 줄이는 순서를 지켜야 합니다.

swap 파일 예제(빈 공간 512MiB 이상 필요):

```bash
sudo dd if=/dev/zero of=/swap-lab bs=1M count=512 status=progress
sudo chmod 600 /swap-lab
sudo mkswap /swap-lab
sudo swapon /swap-lab
swapon --show
free -h
```

영구 설정은 `/swap-lab none swap defaults 0 0`입니다. 정리는 `sudo swapoff /swap-lab` 후 해당 fstab 줄과 파일을 지웁니다.

## mdadm: 리눅스 소프트웨어 RAID

아래는 RAID용으로 따로 준비한 **빈 `/dev/sdc1`, `/dev/sdd1`** 예제입니다. 앞의 파일시스템 실습 파티션을 재사용하지 않습니다.

```bash
sudo mdadm --create /dev/md/lab --level=1 --raid-devices=2 /dev/sdc1 /dev/sdd1
cat /proc/mdstat
sudo mdadm --detail /dev/md/lab
sudo mkfs.xfs /dev/md/lab
sudo mkdir -p /mnt/labraid
sudo mount /dev/md/lab /mnt/labraid
findmnt /mnt/labraid
```

RAID0은 스트라이핑(최소 2개, 장애 허용 없음), RAID1은 미러, RAID5는 최소 3개·1개 장애 허용, RAID6은 최소 4개·2개 장애 허용입니다. RAID는 삭제 실수·랜섬웨어까지 복원하는 백업을 대신하지 않습니다.

구성 확인 `mdadm -D 장치`, 중지 `mdadm -S 장치`, 구성원 장애 표시 `mdadm 장치 --fail 구성원`, 제거 `--remove 구성원`, 추가 `--add 새구성원`. 장애 실습 전 별도 스냅샷을 저장합니다. 자동 조립 설정은 `mdadm --detail --scan` 결과를 검토해 `/etc/mdadm.conf`에 반영하며, 부팅 관련 배열이면 initramfs도 고려합니다.

하드웨어 RAID는 제조사 관리 화면·도구에서 구성합니다. `mdadm --create`는 리눅스 소프트웨어 RAID 명령이므로 모든 RAID 컨트롤러의 물리 디스크를 관리하는 명령이 아닙니다.

## LVM: PV → VG → LV

별도의 빈 LVM용 `/dev/sdc1`, `/dev/sdd1`을 가정합니다. RAID 실습과 동시에 같은 파티션을 쓰지 않습니다.

```bash
sudo pvcreate /dev/sdc1 /dev/sdd1
sudo vgcreate labvg /dev/sdc1 /dev/sdd1
sudo lvcreate -L 1G -n lablv labvg
sudo mkfs.xfs /dev/labvg/lablv
sudo mkdir -p /mnt/lablv
sudo mount /dev/labvg/lablv /mnt/lablv
sudo pvs
sudo vgs
sudo lvs
```

`-L`은 용량, `-l`은 extent 개수/비율, `-n`은 LV 이름입니다. PV·VG·LV 상세는 `pvdisplay`, `vgdisplay`, `lvdisplay`, 탐색은 `pvscan`, `vgscan`, `lvscan`입니다. 새 PV 추가는 `vgextend labvg /dev/새파티션`, LV 확장은 예를 들어 `lvextend -L +512M /dev/labvg/lablv` 후 `xfs_growfs /mnt/lablv`입니다. VG 여유 공간과 실제 파일시스템 확장을 모두 확인합니다.

정리 순서는 마운트 해제 → `lvremove` → `vgremove` → `pvremove`입니다. 해당 장치에 필요한 데이터가 없고 다른 LV가 없는지 확인한 뒤 수행합니다. 실습 전체 초기화에는 스냅샷 복원을 권합니다.

## ext4 쿼터와 XFS 쿼터

공통: 사용자 쿼터와 그룹 쿼터, 블록 용량과 inode(파일 수), soft 한도와 hard 한도를 구분합니다. soft 한도를 넘기면 유예 기간이 적용되며 hard 한도는 즉시 제한됩니다.

ext4의 전통적 파일 기반 쿼터 예:

1. 전용 실습 파일시스템의 fstab 옵션에 `usrquota,grpquota`를 설정하고 마운트합니다.
2. 비어 있고 사용자가 작업하지 않는 실습 파일시스템에서 `sudo quotacheck -cug /mnt/labdata`로 초기화합니다. 사용 중인 파일시스템의 검사 오류를 강제 옵션으로 넘기지 않습니다.
3. `sudo quotaon -vug /mnt/labdata`, `sudo edquota -u labuser`, `sudo repquota /mnt/labdata`로 활성화·편집·확인합니다.

XFS 예: 마운트 시 `uquota` 또는 `usrquota`로 사용자 쿼터를 활성화합니다. 처음 켤 때는 해당 파일시스템을 해제하고 다시 마운트해야 할 수 있으며 루트 파일시스템은 별도 부팅 설정이 필요합니다. XFS에 ext용 quotacheck 절차를 그대로 적용하지 않습니다.

```bash
sudo xfs_quota -x -c 'state' /mnt/lablv
sudo xfs_quota -x -c 'limit -u bsoft=200m bhard=240m labuser' /mnt/lablv
sudo xfs_quota -x -c 'limit -u isoft=1000 ihard=1200 labuser' /mnt/lablv
sudo xfs_quota -x -c 'report -uh' /mnt/lablv
```

`-x`는 관리 모드, `-c`는 실행할 명령입니다. `bsoft/bhard`는 디스크 블록 사용량, `isoft/ihard`는 inode 개수입니다. root가 아닌 해당 사용자로 파일을 만들어 실제 제한까지 확인합니다.

도움말: `man fdisk`, `man parted`, `man fstab`, `man mdadm`, `man lvm`, `man xfs_quota`, `man quotacheck`. 변경 예제 전체 자동 실행은 검증하지 않았습니다. [검증 기록](../VERIFICATION.md)을 확인하세요.
