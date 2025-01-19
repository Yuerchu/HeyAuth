# 海枫授权系统 HeyAuth
---
## 一款支持B+C端的多应用授权系统

此项目本身并非开源项目，因为在 V0.4.0 发现了严重的安全问题，故此版本及以前的版本开源。遵循 GPL V3 许可证。
如需购买后续版本，可邮件至 `admin@yuxiaoqiu.cn` . 中国大陆地区的用户还可联系微信 yuxiaoqiu2333 购买。

### 请注意，开源并不代表免费，禁止倒卖本项目，包括但不限于私下交易/闲鱼/代搭建。

仅供尝鲜，不建议在生产环境中使用，出现任何问题概不负责。

要求版本：Python3.8+ ， 推荐3.12.2

Linux 需要同时安装python3-pip

## 安装

首先安装相关依赖:
> pip3 install -r requirements.txt

然后启动:
> python3 main.py

NGINX配置建议：
```
server {
    listen 80;
    listen [::]:80;
    server_name auth.yxqi.cn;

    # Redirect all HTTP requests to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name auth.yxqi.cn;

    #SSL-START SSL相关配置，请勿删除或修改下一行带注释的404规则
    #error_page 404/404.html;
    #HTTP_TO_HTTPS_START
    if ($server_port !~ 443){
        rewrite ^(/.*)$ https://$host$1 permanent;
    }
    #HTTP_TO_HTTPS_END
    add_header Strict-Transport-Security "max-age=31536000";
    error_page 497  https://$host$request_uri;

    # Proxy pass to localhost:8080
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}
```
