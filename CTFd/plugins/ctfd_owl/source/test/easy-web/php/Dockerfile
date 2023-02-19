FROM php:7.3-fpm

RUN sed -i "s/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g" /etc/apt/sources.list && \
    sed -i "s/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g" /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6-dev libjpeg62-turbo-dev libpng-dev \
    libgmp-dev \
    libbz2-dev \
    libzip-dev \
    libxml2-dev \
    iputils-ping \
    libc-client-dev libkrb5-dev \
    && docker-php-ext-configure imap --with-kerberos --with-imap-ssl \
    && docker-php-ext-configure gd --with-freetype-dir=/usr/include/ --with-jpeg-dir=/usr/include/ --with-png-dir=/usr/include \
    && docker-php-ext-install -j$(nproc) gd bz2 gmp zip bcmath mysqli pdo_mysql pcntl sockets imap soap \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 

# 安装mysql相关扩展

COPY ./php.ini /usr/local/etc/php/php.ini
EXPOSE 9000
CMD ["php-fpm"]