# 프로세스·우선순위·cron

## 실행 중인 프로세스 찾기와 종료

```bash
ps -eo pid,ppid,user,ni,pri,comm --sort=pid
pgrep -u labuser -a
pgrep -x sleep
```

`pgrep`는 PID 검색, `pkill`은 조건에 맞는 프로세스에 신호를 보냅니다. `pkill -u 사용자`는 해당 사용자의 여러 프로세스를 종료할 수 있습니다. 먼저 `pgrep`로 대상을 확인합니다. `kill -TERM PID`로 정상 종료를 요청하고, 응답하지 않는 경우에만 `kill -KILL PID`를 검토합니다. SIGKILL은 정리 작업을 할 기회를 주지 않습니다.

## nice / renice

NI 값은 일반적으로 -20부터 19까지이며 작을수록 CPU 스케줄링에서 유리합니다. CPU 사용량을 일정 비율로 고정하는 옵션은 아닙니다.

```bash
nice -n 7 sleep 300 &
lab_pid=$!
ps -o pid,ni,comm -p "$lab_pid"
renice -n 12 -p "$lab_pid"
ps -o pid,ni,comm -p "$lab_pid"
kill "$lab_pid"
```

`nice -n 7`은 새 프로세스의 nice 값을 부모 값에서 7만큼 조정합니다. 부모 NI=0이면 결과가 7입니다. `renice -n 12 -p PID`는 이미 실행 중인 프로세스의 목표 NI 값을 지정합니다. 일반 사용자는 자기 프로세스의 우선순위를 낮추는 변경(숫자 증가)은 할 수 있지만, 숫자를 다시 낮추는 작업은 권한 제한이 있습니다. root 권한이 필요한 예제와 구분합니다.

## cron 다섯 칸

```text
분 시 일 월 요일 실행명령
15 3 * * 1-5 /usr/bin/date >> /home/labuser/cron.log 2>&1
*/10 * * * * /usr/bin/date >> /home/labuser/cron.log 2>&1
```

첫 줄 예제는 평일 03:15, 두 번째는 매시 0·10·20·30·40·50분입니다. 분 0–59, 시 0–23, 일 1–31, 월 1–12, 요일 0–7(0과 7은 일요일)을 사용합니다. `1-5`는 범위, `1,3,5`는 목록, `*/10`은 간격입니다. 일반적인 cron에서 일과 요일을 모두 제한하면 두 조건 중 하나에 맞을 때 실행됩니다. `man 5 crontab`의 구현 설명을 확인하세요.

```bash
crontab -l
crontab -e
sudo crontab -u labuser -l
sudo crontab -u labuser -e
systemctl status crond
```

`crontab -r`는 해당 사용자 작업 전체 삭제이므로 먼저 `crontab -l > cron.saved`로 보관합니다. `/var/spool/cron/사용자명`을 직접 고치기보다 `crontab`을 사용합니다.

**개인 crontab**에는 사용자 칸이 없습니다. `/etc/crontab`과 `/etc/cron.d/*`의 **시스템 crontab**에는 다섯 시간 칸 다음에 실행 사용자 칸이 있습니다.

```text
# /etc/cron.d/lab-example
15 3 * * 1-5 labuser /usr/bin/date >> /home/labuser/cron.log 2>&1
```

cron은 로그인 셸과 환경이 다릅니다. 명령·파일은 절대경로를 사용하고 출력과 오류를 저장합니다. `%`는 특별한 의미가 있으므로 날짜 포맷 등에 쓸 때 crontab 문법에 맞게 이스케이프합니다. `cron.allow`, `cron.deny`는 crontab 사용 권한 제어 파일이며 파일 존재 조합에 따라 동작이 달라집니다.

## 검증·정리

1분 간격으로 자신의 연습 로그에 시각을 쓰는 작업 하나를 등록하고, 2회 이상 기록되는지 확인합니다. `journalctl -u crond`, `/var/log/cron`도 확인합니다. 끝나면 추가한 줄만 제거하고 저장했던 작업을 복원합니다. root나 다른 사용자의 작업을 통째로 삭제하지 마세요.

도움말: `man nice`, `man renice`, `man pgrep`, `man 1 crontab`, `man 5 crontab`.
