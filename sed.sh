#!/bin/bash
sed -i "s/dynamic.test.com/$DYNAMIC_URL/g" /opt/CTFd/CTFd/plugins/ctfd-whale/utils/setup.py
sed -i "s/direct.test.com/$DIRECT_URL/g" /opt/CTFd/CTFd/plugins/ctfd-whale/utils/setup.py

sed -i "s/ctfd.test.com/$CTFD_URL/g" /opt/CTFd/conf/nginx/http.conf
sed -i "s/dynamic.test.com/$DYNAMIC_URL/g" /opt/CTFd/conf/nginx/http.conf
sed -i "s/direct.test.com/$DIRECT_URL/g" /opt/CTFd/conf/nginx/http.conf

sed -i "s/dynamic.test.com/$DYNAMIC_URL/g" /opt/CTFd/frps/frps.ini

UUID=$(cat /proc/sys/kernel/random/uuid)
sed -i "s/YOUR_TOKEN/$UUID/g" /opt/CTFd/frps/frps.ini
sed -i "s/YOUR_TOKEN/$UUID/g" /opt/CTFd/frpc/frpc.ini
