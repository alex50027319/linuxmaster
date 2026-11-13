#!/usr/bin/env bash
# Read-only inventory. Missing optional tools are reported; nothing is installed.
set -eu
printf '== OS / kernel ==\n'
if [ -r /etc/os-release ]; then cat /etc/os-release; fi
uname -srmo
printf '\n== Commands (missing != automatic failure) ==\n'
for cmd in man less grep wget useradd usermod chage getent lsattr find \
    fdisk parted lsblk blkid findmnt mkfs.ext4 mkfs.xfs mkswap mdadm \
    pvcreate vgcreate lvcreate xfs_quota quotacheck crontab nice renice \
    dnf rpm gcc make lsmod modprobe sysctl ipcs rsyslogd logrotate \
    tar cpio rsync dd dump restore xfsdump xfsrestore \
    httpd htpasswd named-checkconf named-checkzone dig \
    sendmail newaliases makemap testparm smbclient exportfs vsftpd \
    squid dhcpd iptables firewall-cmd ssh-keygen getenforce nmap; do
    if command -v "$cmd" >/dev/null 2>&1; then
        printf 'OK      %-18s %s\n' "$cmd" "$(command -v "$cmd")"
    else
        printf 'MISSING %s\n' "$cmd"
    fi
done
printf '\n== Local documentation ==\n'
if command -v man >/dev/null 2>&1; then
    for page in useradd crontab smb.conf exports; do
        if man -w "$page" >/dev/null 2>&1; then
            printf 'OK      man %s\n' "$page"
        else
            printf 'MISSING man %s\n' "$page"
        fi
    done
fi
for path in /usr/share/doc/squid/squid.conf.documented /usr/src/linux-4.18/Makefile; do
    if [ -r "$path" ]; then printf 'FOUND   %s\n' "$path"; else printf 'ABSENT  %s (path varies)\n' "$path"; fi
done
printf '\n== Block devices (inspection only) ==\n'
if command -v lsblk >/dev/null 2>&1; then lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT; fi
printf '\n== Listeners (inspection only) ==\n'
if command -v ss >/dev/null 2>&1; then ss -lnt; fi
printf '\n점검 완료. MISSING은 필요한 실습 패키지를 선택할 때 참고하세요.\n'
