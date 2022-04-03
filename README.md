# CTFd-docker
可以快速使用Docker一键配置CTFd

此版本的CTFd集合Whale插件，用以部署动态容器挑战

[CTFd-docker配置参考](https://blog.hz2016.com/2022/03/%e3%80%90ctfd%e3%80%91%e9%9d%b6%e5%9c%ba%e5%ae%89%e8%a3%85%e4%b8%8e%e9%85%8d%e7%bd%ae%ef%bc%88docker%e4%b8%80%e9%94%ae%e9%85%8d%e7%bd%ae%e7%89%88%ef%bc%89/)

## 快速安装

在Ubuntu20.04下完成过测试

```
git clone https://github.com/huangzheng2016/CTFd-docker CTFd
sudo sh CTFd/install.sh
```

虽然还是建议大家自己安装，别直接脚本，以免出现配置不正确

请在root权限下执行

```
apt-get install git docker docker-compose -y
git clone https://github.com/huangzheng2016/CTFd-docker CTFd
docker swarm init
docker node update --label-add='name=linux-1' $(docker node ls -q)
docker-compose -f CTFd/docker-compose.yml up -d
docker-compose -f CTFd/docker-compose.yml exec ctfd python manage.py set_config whale auto_connect_network
```

## 更新日志

2022.3.27
>初版提交

2022.3.28
>更新Frp服务器并重载404页面