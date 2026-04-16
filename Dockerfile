FROM ubuntu:jammy
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    LANG=zh_CN.UTF-8 \
    SHELL=/bin/bash \
    PS1="\u@\h:\w \$ " \
    PAGERMAID_DIR=/pagermaid \
    DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]
WORKDIR /pagermaid/workdir
RUN source ~/.bashrc \
    ## 安装运行环境依赖，自编译建议修改为国内镜像源
#   && sed -i 's/archive.ubuntu.com/mirrors.bfsu.edu.cn/g' /etc/apt/sources.list \
#   && sed -i 's/security.ubuntu.com/mirrors.bfsu.edu.cn/g' /etc/apt/sources.list \
#   && sed -i 's/ports.ubuntu.com/mirrors.bfsu.edu.cn/g' /etc/apt/sources.list \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
        python3 \
        python3-pip \
        tesseract-ocr \
        tesseract-ocr-eng \
        tesseract-ocr-chi-sim \
        language-pack-zh-hans \
        sudo \
        git \
        openssl \
        curl \
        wget \
        neofetch \
        ffmpeg \
        fortune-mod \
        figlet \
        libmagic1 \
        libzbar0 \
        iputils-ping \
        tzdata \
    ## 安装编译依赖
    && apt-get update \
    && apt-get install --no-install-recommends -y \
        ## 这是跨平台交叉编译要用到的包，如果自行构建，有可能不需要
        build-essential \
        apt-utils \
        python3-dev \
        libxslt1-dev \
        libxml2-dev \
        libssl-dev \
        libffi-dev \
        zlib1g-dev \
        tcl8.6-dev \
        libimagequant-dev \
        libraqm-dev \
        libjpeg-dev \
        libtiff5-dev \
        libopenjp2-7-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
        pkg-config \
    ## 设置时区
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    ## python软链接
    && ln -sf /usr/bin/python3 /usr/bin/python \
    ## 升级pip
#   && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    && python -m pip install --upgrade pip \
    ## 添加用户
    && echo "pagermaid ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/pagermaid \
    && useradd pagermaid -r -m -d /pagermaid -s /bin/bash \
    && usermod -aG sudo,users pagermaid \
    ## 克隆仓库
    && git clone -b master https://github.com/TeamPGM/PagerMaid-Pyro.git /pagermaid/workdir \
    && git config --global pull.ff only \
    ## pip install
    && pip install -r requirements.txt \
    ## 卸载编译依赖，清理安装缓存
    && sudo apt-get purge --auto-remove -y \
        build-essential \
        apt-utils \
        python3-dev \
        libxslt1-dev \
        libxml2-dev \
        libssl-dev \
        libffi-dev \
        zlib1g-dev \
        tcl8.6-dev \
        libimagequant-dev \
        libraqm-dev \
        libjpeg-dev \
        libtiff5-dev \
        libopenjp2-7-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
        pkg-config \
    && apt-get clean -y \
    && rm -rf \
        ## 删除apt和pip的安装缓存
        /tmp/* \
        /var/lib/apt/lists/* \
        /var/tmp/* \
        ~/.cache
ENTRYPOINT ["sh","utils/docker-config.sh"]
