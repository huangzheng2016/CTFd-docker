#!/bin/bash
sed -i 's/dynamic.localhost/$DYNAMIC_URL/g' /opt/CTFd/plugins/ctfd-whale/utils/setup.py
sed -i 's/direct.localhost/$DIRECT_URL/g' /opt/CTFd/plugins/ctfd-whale/utils/setup.py

sed -i 's/ctfd.localhost/$CTFD_URL/g' /opt/CTFd/conf/nginx/nginx.conf
sed -i 's/dynamic.localhost/$DYNAMIC_URL/g' /opt/CTFd/conf/nginx/nginx.conf
sed -i 's/direct.localhost/$DIRECT_URL/g' /opt/CTFd/conf/nginx/nginx.conf

sed -i 's/dynamic.localhost/$DYNAMIC_URL/g' /opt/CTFd/frps/frps.ini

UUID=$(cat /proc/sys/kernel/random/uuid)
sed -i 's/your_token/$UUID/g' /opt/CTFd/frps/frps.ini
sed -i 's/your_token/$UUID/g' /opt/CTFd/frpc/frpc.ini