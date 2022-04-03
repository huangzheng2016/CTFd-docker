#!/bin/sh
apt-get install docker docker-compose -y
docker swarm init
docker node update --label-add='name=linux-1' $(docker node ls -q)
docker-compose -f CTFd/docker-compose.yml up -d
docker-compose -f CTFd/docker-compose.yml exec ctfd python manage.py set_config whale auto_connect_network
