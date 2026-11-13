# Apache HTTP Server 2.4

## 설정 위치와 핵심 지시어

Rocky 패키지 기준 `/etc/httpd/conf/httpd.conf`, `/etc/httpd/conf.d/*.conf`, `/etc/httpd/conf.modules.d/*.conf`를 확인합니다. 소스 설치는 경로가 다릅니다. `ServerRoot`는 설정·로그 등 상대경로의 기준, `DocumentRoot`는 기본 제공 콘텐츠 경로입니다.

```apache
ServerName web.example.test:80
DocumentRoot "/var/www/html"
DirectoryIndex index.html index.htm
<Directory "/var/www/html">
    Options -Indexes +FollowSymLinks
    AllowOverride None
    Require all granted
</Directory>
```

`Options Indexes`는 인덱스 파일이 없을 때 디렉터리 목록을 보여줄 수 있습니다. `FollowSymLinks`는 심볼릭 링크 처리, `AllowOverride`는 `.htaccess`에서 허용할 설정 범위를 제어합니다. `None`이면 해당 override를 허용하지 않습니다. `<Directory>`는 파일시스템 경로, `<Location>`은 URL 공간에 대한 설정이라는 차이도 읽으세요.

추가로 `Listen 8080`은 수신 포트, `ServerAdmin admin@example.test`는 관리자 연락처, `ErrorDocument 404 /errors/notfound.html`은 오류 응답 문서입니다. `Include 경로`는 다른 설정을 포함하고 `LoadModule 모듈식별자 modules/파일.so`는 모듈을 적재합니다. 예: `LoadModule userdir_module modules/mod_userdir.so`. 패키지가 이미 적재한 모듈을 중복 선언하지 않습니다.

## Basic 인증

연습용 콘텐츠 디렉터리를 만들고 비밀번호 파일을 웹 공개 경로 밖에 둡니다.

```bash
sudo mkdir -p /var/www/html/private
sudo htpasswd -c /etc/httpd/lab-users labuser
sudo chown root:apache /etc/httpd/lab-users
sudo chmod 640 /etc/httpd/lab-users
```

```apache
<Directory "/var/www/html/private">
    AuthType Basic
    AuthName "Practice area"
    AuthUserFile /etc/httpd/lab-users
    Require valid-user
</Directory>
```

`AuthName`은 인증 영역 설명, `AuthUserFile`은 해시 파일, `Require valid-user`는 등록된 사용자 허용입니다. 특정 사용자만 허용하려면 `Require user labuser`를 사용합니다. `htpasswd -c`는 새 파일 생성으로 기존 파일을 덮어쓸 수 있으므로 추가 사용자에는 `-c`를 빼세요. 실제 운영에서 Basic 인증은 HTTPS와 함께 사용합니다.

`.htaccess` 방식이라면 상위 설정에 `AllowOverride AuthConfig` 등 필요한 범위를 허용해야 합니다. 중앙 설정에 넣는 방식과 `.htaccess` 방식을 섞어 조건을 놓치지 마세요.

## UserDir

`mod_userdir`가 적재되어 있고 배포판의 `/etc/httpd/conf.d/userdir.conf`에서 해당 사용자가 허용되어야 합니다.

```apache
UserDir public_html
UserDir disabled root
<Directory "/home/*/public_html">
    AllowOverride None
    Options -Indexes
    Require all granted
</Directory>
```

배포판 기본의 `UserDir disabled`가 전체 사용자를 차단하고 있으면 설정을 조정하거나 `UserDir enabled labuser`로 조건에 맞게 허용합니다. URL은 `http://서버/~labuser/`, 실제 파일은 `/home/labuser/public_html/`입니다. 홈 상위 경로의 탐색 권한, 파일 읽기 권한, SELinux `httpd_enable_homedirs` 및 콘텐츠 라벨도 맞아야 합니다. 무조건 `chmod -R 777`로 해결하지 않습니다.

## 이름 기반 가상 호스트

```apache
<VirtualHost *:80>
    ServerName portal.example.test
    ServerAlias www.portal.example.test
    DocumentRoot /var/www/portal
    ErrorLog logs/portal_error.log
    CustomLog logs/portal_access.log combined
    <Directory "/var/www/portal">
        Require all granted
    </Directory>
</VirtualHost>
```

콘텐츠 경로를 만들고 권한을 부여한 뒤 검사합니다. Apache 2.4에서는 구형 `NameVirtualHost *:80`이 필요하지 않습니다. 2.2의 `Order`, `Allow from`, `Deny from`은 현대 `Require`와 구분해 학습합니다.

## 적용·검증·정리

```bash
sudo httpd -t
sudo httpd -S
httpd -M
sudo systemctl reload httpd
curl -I -H 'Host: portal.example.test' http://127.0.0.1/
curl -I http://127.0.0.1/private/
curl -u labuser -I http://127.0.0.1/private/
```

서비스가 꺼져 있다면 검사 후 `systemctl start httpd`가 필요합니다. `httpd -t`/`apachectl configtest`는 문법 검사, `-S`는 가상 호스트, `-M`은 모듈입니다. 인증 전 401, 올바른 인증 후 기대한 응답인지 확인합니다. 다른 VM에서는 DNS/hosts·포트·방화벽도 확인합니다. 403은 Unix 권한·Directory 인가·SELinux를 나누어 조사합니다.

소스 설치 경로에서는 `/usr/local/apache2/bin/apachectl`처럼 전체 경로가 필요할 수 있습니다. `apachectl start/stop/restart/graceful`의 차이도 확인합니다. `graceful`은 진행 중인 요청을 가능한 한 마무리하면서 설정을 다시 읽는 방식입니다. `httpd -t -D DUMP_MODULES`, `httpd -t -D DUMP_VHOSTS`도 각각 모듈·가상 호스트 확인과 연결됩니다.

실습 종료 시 추가한 conf·계정 파일·콘텐츠를 정리하고 이전 설정으로 reload하거나 스냅샷을 복원합니다. [방화벽·SELinux](firewall-ssh-selinux.md)와 함께 봅니다.

도움말: `man httpd`, `man apachectl`, `man htpasswd`, [공식 지시어 색인](https://httpd.apache.org/docs/2.4/mod/directives.html), [공식 인증 문서](https://httpd.apache.org/docs/2.4/howto/auth.html).
