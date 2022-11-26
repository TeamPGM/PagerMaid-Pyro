#!/bin/bash
if [[ $EUID -ne 0 ]]; then
    echo "错误：本脚本需要 root 权限执行。" 1>&2
    exit 1
fi

a=$(curl --noproxy '*' -sSL https://api.myip.com/)
b="China"
if [[ $a == *$b* ]]
then
  echo "错误：本脚本不支持境内服务器使用。" 1>&2
	exit 1
fi

check_sys() {
    if [[ -f /etc/redhat-release ]]; then
        release="centos"
    elif cat /etc/issue | grep -q -E -i "debian"; then
        release="debian"
    elif cat /etc/issue | grep -q -E -i "ubuntu"; then
        release="ubuntu"
    elif cat /etc/issue | grep -q -E -i "centos|red hat|redhat"; then
        release="centos"
    elif cat /proc/version | grep -q -E -i "debian"; then
        release="debian"
    elif cat /proc/version | grep -q -E -i "ubuntu"; then
        release="ubuntu"
    elif cat /proc/version | grep -q -E -i "centos|red hat|redhat"; then
        release="centos"
    fi
}

welcome() {
    echo "一键脚本出现任何问题请转手动搭建！ xtaolabs.com"
    echo "一键脚本出现任何问题请转手动搭建！ xtaolabs.com"
    echo "一键脚本出现任何问题请转手动搭建！ xtaolabs.com"
    echo ""
    echo ""
    echo "欢迎使用 PagerMaid-Pyro 一键安装程序。"
    echo "安装即将开始"
    echo "如果您想取消安装，"
    echo "请在 5 秒钟内按 Ctrl+C 终止此脚本。"
    echo ""
    sleep 5
}

yum_update() {
    echo "正在优化 yum . . ."
    yum install yum-utils epel-release -y >>/dev/null 2>&1
}

yum_git_check() {
    echo "正在检查 Git 安装情况 . . ."
    if command -v git >>/dev/null 2>&1; then
        echo "Git 似乎存在，安装过程继续 . . ."
    else
        echo "Git 未安装在此系统上，正在进行安装"
        yum install git -y >>/dev/null 2>&1
    fi
}

yum_python_check() {
    echo "正在检查 python 安装情况 . . ."
    if command -v python3 >>/dev/null 2>&1; then
        U_V1=$(python3 -V 2>&1 | awk '{print $2}' | awk -F '.' '{print $1}')
        U_V2=$(python3 -V 2>&1 | awk '{print $2}' | awk -F '.' '{print $2}')
        if [ $U_V1 -gt 3 ]; then
            echo 'Python 3.6+ 存在 . . .'
        elif [ $U_V2 -ge 6 ]; then
            echo 'Python 3.6+ 存在 . . .'
            PYV=$U_V1.$U_V2
            PYV=$(which python$PYV)
        else
            if command -v python3.6 >>/dev/null 2>&1; then
                echo 'Python 3.6+ 存在 . . .'
                PYV=$(which python3.6)
            else
                echo "Python3.6 未安装在此系统上，正在进行安装"
                yum install python3 -y >>/dev/null 2>&1
                update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1 >>/dev/null 2>&1
                PYV=$(which python3.6)
            fi
        fi
    else
        echo "Python3.6 未安装在此系统上，正在进行安装"
        yum install python3 -y >>/dev/null 2>&1
        update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1 >>/dev/null 2>&1
        PYV=$(which python3.6)
    fi
    if command -v pip3 >>/dev/null 2>&1; then
        echo 'pip 存在 . . .'
    else
        echo "pip3 未安装在此系统上，正在进行安装"
        yum install -y python3-pip >>/dev/null 2>&1
    fi
}

yum_screen_check() {
    echo "正在检查 Screen 安装情况 . . ."
    if command -v screen >>/dev/null 2>&1; then
        echo "Screen 似乎存在, 安装过程继续 . . ."
    else
        echo "Screen 未安装在此系统上，正在进行安装"
        yum install screen -y >>/dev/null 2>&1
    fi
}

yum_require_install() {
    echo "正在安装系统所需依赖，可能需要几分钟的时间 . . ."
    yum install python-devel python3-devel zbar zbar-devel ImageMagick wget -y >>/dev/null 2>&1
    wget -T 2 -O /etc/yum.repos.d/konimex-neofetch-epel-7.repo https://copr.fedorainfracloud.org/coprs/konimex/neofetch/repo/epel-7/konimex-neofetch-epel-7.repo >>/dev/null 2>&1
    yum groupinstall "Development Tools" -y >>/dev/null 2>&1
    yum-config-manager --add-repo https://download.opensuse.org/repositories/home:/Alexander_Pozdnyakov/CentOS_7/ >>/dev/null 2>&1
    sudo rpm --import https://build.opensuse.org/projects/home:Alexander_Pozdnyakov/public_key >>/dev/null 2>&1
    yum list updates >>/dev/null 2>&1
    yum install neofetch figlet tesseract tesseract-langpack-chi-sim tesseract-langpack-eng -y >>/dev/null 2>&1
}

apt_update() {
    echo "正在优化 apt-get . . ."
    apt-get install sudo -y >>/dev/null 2>&1
    apt-get update >>/dev/null 2>&1
}

apt_git_check() {
    echo "正在检查 Git 安装情况 . . ."
    if command -v git >>/dev/null 2>&1; then
        echo "Git 似乎存在, 安装过程继续 . . ."
    else
        echo "Git 未安装在此系统上，正在进行安装"
        apt-get install git -y >>/dev/null 2>&1
    fi
}

apt_python_check() {
    echo "正在检查 python 安装情况 . . ."
    if command -v python3 >>/dev/null 2>&1; then
        U_V1=$(python3 -V 2>&1 | awk '{print $2}' | awk -F '.' '{print $1}')
        U_V2=$(python3 -V 2>&1 | awk '{print $2}' | awk -F '.' '{print $2}')
        if [ $U_V1 -gt 3 ]; then
            echo 'Python 3.6+ 存在 . . .'
        elif [ $U_V2 -ge 6 ]; then
            echo 'Python 3.6+ 存在 . . .'
            PYV=$U_V1.$U_V2
            PYV=$(which python$PYV)
        else
            if command -v python3.6 >>/dev/null 2>&1; then
                echo 'Python 3.6+ 存在 . . .'
                PYV=$(which python3.6)
            else
                echo "Python3.6 未安装在此系统上，正在进行安装"
                add-apt-repository ppa:deadsnakes/ppa -y
                apt-get update >>/dev/null 2>&1
                apt-get install python3.6 -y >>/dev/null 2>&1
                update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1 >>/dev/null 2>&1
                PYV=$(which python3.6)
            fi
        fi
    else
        echo "Python3.6 未安装在此系统上，正在进行安装"
        add-apt-repository ppa:deadsnakes/ppa -y
        apt-get update >>/dev/null 2>&1
        apt-get install python3.6 -y >>/dev/null 2>&1
        update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1 >>/dev/null 2>&1
        PYV=$(which python3.6)
    fi
    if command -v pip3 >>/dev/null 2>&1; then
        echo 'pip 存在 . . .'
    else
        echo "pip3 未安装在此系统上，正在进行安装"
        apt-get install -y python3-pip >>/dev/null 2>&1
    fi
}

debian_python_check() {
    echo "正在检查 python 安装情况 . . ."
    if command -v python3 >>/dev/null 2>&1; then
        U_V1=$(python3 -V 2>&1 | awk '{print $2}' | awk -F '.' '{print $1}')
        U_V2=$(python3 -V 2>&1 | awk '{print $2}' | awk -F '.' '{print $2}')
        if [ $U_V1 -gt 3 ]; then
            echo 'Python 3.6+ 存在 . . .'
        elif [ $U_V2 -ge 6 ]; then
            echo 'Python 3.6+ 存在 . . .'
            PYV=$U_V1.$U_V2
            PYV=$(which python$PYV)
        else
            if command -v python3.6 >>/dev/null 2>&1; then
                echo 'Python 3.6+ 存在 . . .'
                PYV=$(which python3.6)
            else
                echo "Python3.6 未安装在此系统上，正在进行安装"
                apt-get update -y >>/dev/null 2>&1
                apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev >>/dev/null 2>&1
                wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tgz >>/dev/null 2>&1
                tar -xvf Python-3.6.5.tgz >>/dev/null 2>&1
                chmod -R +x Python-3.6.5 >>/dev/null 2>&1
                cd Python-3.6.5 >>/dev/null 2>&1
                ./configure >>/dev/null 2>&1
                make && make install >>/dev/null 2>&1
                cd .. >>/dev/null 2>&1
                rm -rf Python-3.6.5 Python-3.6.5.tar.gz >>/dev/null 2>&1
                PYV=$(which python3.6)
                update-alternatives --install /usr/bin/python3 python3 $PYV 1 >>/dev/null 2>&1
            fi
        fi
    else
        echo "Python3.6 未安装在此系统上，正在进行安装"
        apt-get update -y >>/dev/null 2>&1
        apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev >>/dev/null 2>&1
        wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tgz >>/dev/null 2>&1
        tar -xvf Python-3.6.5.tgz >>/dev/null 2>&1
        chmod -R +x Python-3.6.5 >>/dev/null 2>&1
        cd Python-3.6.5 >>/dev/null 2>&1
        ./configure >>/dev/null 2>&1
        make && make install >>/dev/null 2>&1
        cd .. >>/dev/null 2>&1
        rm -rf Python-3.6.5 Python-3.6.5.tar.gz >>/dev/null 2>&1
        PYV=$(which python3)
        update-alternatives --install /usr/bin/python3 python3 $PYV 1 >>/dev/null 2>&1
    fi
    echo "正在检查 pip3 安装情况 . . ."
    if command -v pip3 >>/dev/null 2>&1; then
        echo 'pip 存在 . . .'
    else
        echo "pip3 未安装在此系统上，正在进行安装"
        apt-get install -y python3-pip >>/dev/null 2>&1
    fi
}

apt_screen_check() {
    echo "正在检查 Screen 安装情况 . . ."
    if command -v screen >>/dev/null 2>&1; then
        echo "Screen 似乎存在, 安装过程继续 . . ."
    else
        echo "Screen 未安装在此系统上，正在进行安装"
        apt-get install screen -y >>/dev/null 2>&1
    fi
}

apt_require_install() {
    echo "正在安装系统所需依赖，可能需要几分钟的时间 . . ."
    apt-get install python3.6-dev python3-dev imagemagick software-properties-common tesseract-ocr tesseract-ocr-chi-sim libzbar-dev -y >>/dev/null 2>&1
    add-apt-repository ppa:dawidd0811/neofetch -y
    apt-get install neofetch -y >>/dev/null 2>&1
}

debian_require_install() {
    echo "正在安装系统所需依赖，可能需要几分钟的时间 . . ."
    apt-get install imagemagick software-properties-common tesseract-ocr tesseract-ocr-chi-sim libzbar-dev neofetch -y >>/dev/null 2>&1
}

download_repo() {
    echo "下载 repository 中 . . ."
    rm -rf /var/lib/pagermaid >>/dev/null 2>&1
    git clone https://github.com/TeamPGM/PagerMaid-Pyro.git /var/lib/pagermaid >>/dev/null 2>&1
    cd /var/lib/pagermaid >>/dev/null 2>&1
    echo "Hello World!" >/var/lib/pagermaid/public.lock
}

pypi_install() {
    echo "下载安装 pypi 依赖中 . . ."
    $PYV -m pip install --upgrade pip >>/dev/null 2>&1
    $PYV -m pip install -r requirements.txt >>/dev/null 2>&1
    sudo -H $PYV -m pip install --ignore-installed PyYAML >>/dev/null 2>&1
}

configure() {
    config_file=config.yml
    echo "生成配置文件中 . . ."
    cp config.gen.yml config.yml
    printf "请输入应用程序 api_id（不懂请直接回车）："
    read -r api_id <&1
    sed -i "s/ID_HERE/$api_id/" $config_file
    printf "请输入应用程序 api_hash（不懂请直接回车）："
    read -r api_hash <&1
    sed -i "s/HASH_HERE/$api_hash/" $config_file
    printf "请输入应用程序语言（默认：zh-cn）："
    read -r application_language <&1
    if [ -z "$application_language" ]; then
        echo "语言设置为 简体中文"
    else
        sed -i "s/zh-cn/$application_language/" $config_file
    fi
    printf "请输入应用程序地区（默认：China）："
    read -r application_region <&1
    if [ -z "$application_region" ]; then
        echo "地区设置为 中国"
    else
        sed -i "s/China/$application_region/" $config_file
    fi
    printf "请输入 Google TTS 语言（默认：zh-CN）："
    read -r application_tts <&1
    if [ -z "$application_tts" ]; then
        echo "tts发音语言设置为 简体中文"
    else
        sed -i "s/zh-CN/$application_tts/" $config_file
    fi
    printf "启用日志记录？ [Y/n]"
    read -r logging_confirmation <&1
    case $logging_confirmation in
    [yY][eE][sS] | [yY])
        printf "请输入您的日志记录群组/频道的 ChatID （如果要发送给 原 PagerMaid 作者 ，请按Enter）："
        read -r log_chatid <&1
        if [ -z "$log_chatid" ]; then
            echo "LOG 将发送到 原 PagerMaid 作者."
        else
            sed -i "s/503691334/$log_chatid/" $config_file
        fi
        sed -i "s/log: False/log: True/" $config_file
        ;;
    [nN][oO] | [nN])
        echo "安装过程继续 . . ."
        ;;
    *)
        echo "输入错误 . . ."
        exit 1
        ;;
    esac
}

read_checknum() {
    while :; do
    read -p "请输入您的登录验证码: " checknum
    if [ "$checknum" == "" ]; then
        continue
    fi
    read -p "请再次输入您的登录验证码：" checknum2
    if [ "$checknum" != "$checknum2" ]; then
        echo "两次验证码不一致！请重新输入您的登录验证码"
        continue

    else
        screen -x -S userbot -p 0 -X stuff "$checknum"
        screen -x -S userbot -p 0 -X stuff $'\n'
        break
    fi
done
    read -p "有没有二次登录验证码？ [Y/n]" choi
    if [ "$choi" == "y" ] || [ "$choi" == "Y" ]; then
        read -p "请输入您的二次登录验证码: " twotimepwd
        screen -x -S userbot -p 0 -X stuff "$twotimepwd"
        screen -x -S userbot -p 0 -X stuff $'\n'
    fi
    
}

login_screen() {
    screen -S userbot -X quit >>/dev/null 2>&1
    screen -dmS userbot
    sleep 1
    screen -x -S userbot -p 0 -X stuff "cd /var/lib/pagermaid && $PYV -m pagermaid"
    screen -x -S userbot -p 0 -X stuff $'\n'
    sleep 3
    if [ "$(ps -def | grep [p]agermaid | grep -v grep)" == "" ]; then
        echo "PagerMaid 运行时发生错误，错误信息："
        cd /var/lib/pagermaid && $PYV -m pagermaid >err.log
        cat err.log
        screen -S userbot -X quit >>/dev/null 2>&1
        exit 1
    fi
    while :; do
        echo "一键脚本出现任何问题请转手动搭建！ xtaolabs.com"
        echo "一键脚本出现任何问题请转手动搭建！ xtaolabs.com"
        echo "一键脚本出现任何问题请转手动搭建！ xtaolabs.com"
        echo ""
        read -p "请输入您的 Telegram 手机号码（带国际区号 如 +8618888888888）: " phonenum

        if [ "$phonenum" == "" ]; then
            continue
        fi

        screen -x -S userbot -p 0 -X stuff "$phonenum"
        screen -x -S userbot -p 0 -X stuff $'\n'
        screen -x -S userbot -p 0 -X stuff "y"
        screen -x -S userbot -p 0 -X stuff $'\n'

        sleep 2
        
        if [ "$(ps -def | grep [p]agermaid | grep -v grep)" == "" ]; then
            echo "手机号输入错误！请确认您是否带了区号（中国号码为 +86 如 +8618888888888）"
            screen -x -S userbot -p 0 -X stuff "cd /var/lib/pagermaid && $PYV -m pagermaid"
            screen -x -S userbot -p 0 -X stuff $'\n'
            continue
        fi

        sleep 1
        if [ "$(ps -def | grep [p]agermaid | grep -v grep)" == "" ]; then
            echo "PagerMaid 运行时发生错误，可能是因为发送验证码失败，请检查您的 API_ID 和 API_HASH"
            exit 1
        fi

        read -p "请输入您的登录验证码: " checknum
        if [ "$checknum" == "" ]; then
            read_checknum
            break
        fi

        read -p "请再次输入您的登录验证码：" checknum2
        if [ "$checknum" != "$checknum2" ]; then
            echo "两次验证码不一致！请重新输入您的登录验证码"
            read_checknum
            break
        else
            screen -x -S userbot -p 0 -X stuff "$checknum"
            screen -x -S userbot -p 0 -X stuff $'\n'
        fi

        read -p "有没有二次登录验证码？ [Y/n]" choi
        if [ "$choi" == "y" ] || [ "$choi" == "Y" ]; then
            read -p "请输入您的二次登录验证码: " twotimepwd
            screen -x -S userbot -p 0 -X stuff "$twotimepwd"
            screen -x -S userbot -p 0 -X stuff $'\n'
            break
        else
            break
        fi
    done
    sleep 5
    screen -S userbot -X quit >>/dev/null 2>&1
}

systemctl_reload() {
    echo "正在写入系统进程守护 . . ."
    echo "[Unit]
    Description=PagerMaid-Pyro telegram utility daemon
    After=network.target
    [Install]
    WantedBy=multi-user.target
    [Service]
    Type=simple
    WorkingDirectory=/var/lib/pagermaid
    ExecStart=$PYV -m pagermaid
    Restart=always
    " >/etc/systemd/system/pagermaid.service
    chmod 755 pagermaid.service >>/dev/null 2>&1
    systemctl daemon-reload >>/dev/null 2>&1
    systemctl start pagermaid >>/dev/null 2>&1
    systemctl enable pagermaid >>/dev/null 2>&1
}

start_installation() {
    if [ "$release" = "centos" ]; then
        echo "系统检测通过。"
        welcome
        yum_update
        yum_git_check
        yum_python_check
        yum_screen_check
        yum_require_install
        download_repo
        pypi_install
        configure
        login_screen
        systemctl_reload
        echo "PagerMaid 已经安装完毕 在telegram对话框中输入 ,help 并发送查看帮助列表"
    elif [ "$release" = "ubuntu" ]; then
        echo "系统检测通过。"
        welcome
        apt_update
        apt_git_check
        apt_python_check
        apt_screen_check
        apt_require_install
        download_repo
        pypi_install
        configure
        login_screen
        systemctl_reload
        echo "PagerMaid 已经安装完毕 在telegram对话框中输入 ,help 并发送查看帮助列表"
    elif [ "$release" = "debian" ]; then
        echo "系统检测通过。"
        welcome
        apt_update
        apt_git_check
        debian_python_check
        apt_screen_check
        debian_require_install
        download_repo
        pypi_install
        configure
        login_screen
        systemctl_reload
        echo "PagerMaid 已经安装完毕 在telegram对话框中输入 ,help 并发送查看帮助列表"
    else
        echo "目前暂时不支持此系统。"
    fi
    exit 1
}

cleanup() {
    if [ ! -x "/var/lib/pagermaid" ]; then
        echo "目录不存在不需要卸载。"
    else
        echo "正在关闭 PagerMaid . . ."
        systemctl disable pagermaid >>/dev/null 2>&1
        systemctl stop pagermaid >>/dev/null 2>&1
        echo "正在删除 PagerMaid 文件 . . ."
        rm -rf /etc/systemd/system/pagermaid.service >>/dev/null 2>&1
        rm -rf /var/lib/pagermaid >>/dev/null 2>&1
        echo "卸载完成 . . ."
    fi
}

reinstall() {
    cleanup
    start_installation
}

cleansession() {
    if [ ! -x "/var/lib/pagermaid" ]; then
        echo "目录不存在请重新安装 PagerMaid。"
        exit 1
    fi
    echo "正在关闭 PagerMaid . . ."
    systemctl stop pagermaid >>/dev/null 2>&1
    echo "正在删除账户授权文件 . . ."
    rm -rf /var/lib/pagermaid/pagermaid.session >>/dev/null 2>&1
    echo "请进行重新登陆. . ."
    if [ "$release" = "centos" ]; then
        yum_python_check
        yum_screen_check
    elif [ "$release" = "ubuntu" ]; then
        apt_python_check
        apt_screen_check
    elif [ "$release" = "debian" ]; then
        debian_python_check
        apt_screen_check
    else
        echo "目前暂时不支持此系统。"
    fi
    login_screen
    systemctl start pagermaid >>/dev/null 2>&1
}

stop_pager() {
    echo ""
    echo "正在关闭 PagerMaid . . ."
    systemctl stop pagermaid >>/dev/null 2>&1
    echo ""
    sleep 3
    shon_online
}

start_pager() {
    echo ""
    echo "正在启动 PagerMaid . . ."
    systemctl start pagermaid >>/dev/null 2>&1
    echo ""
    sleep 3
    shon_online
}

restart_pager() {
    echo ""
    echo "正在重新启动 PagerMaid . . ."
    systemctl restart pagermaid >>/dev/null 2>&1
    echo ""
    sleep 3
    shon_online
}

install_require() {
    if [ "$release" = "centos" ]; then
        echo "系统检测通过。"
        yum_update
        yum_git_check
        yum_python_check
        yum_screen_check
        yum_require_install
        pypi_install
        systemctl_reload
        shon_online
    elif [ "$release" = "ubuntu" ]; then
        echo "系统检测通过。"
        apt_update
        apt_git_check
        apt_python_check
        apt_screen_check
        apt_require_install
        pypi_install
        systemctl_reload
        shon_online
    elif [ "$release" = "debian" ]; then
        echo "系统检测通过。"
        welcome
        apt_update
        apt_git_check
        debian_python_check
        apt_screen_check
        debian_require_install
        pypi_install
        systemctl_reload
        shon_online
    else
        echo "目前暂时不支持此系统。"
    fi
    exit 1
}

shon_online() {
    echo "一键脚本出现任何问题请转手动搭建！ xtaolabs.com"
    echo "一键脚本出现任何问题请转手动搭建！ xtaolabs.com"
    echo "一键脚本出现任何问题请转手动搭建！ xtaolabs.com"
    echo ""
    echo ""
    echo "请选择您需要进行的操作:"
    echo "  1) 安装 PagerMaid"
    echo "  2) 卸载 PagerMaid"
    echo "  3) 重新安装 PagerMaid"
    echo "  4) 重新登陆 PagerMaid"
    echo "  5) 关闭 PagerMaid"
    echo "  6) 启动 PagerMaid"
    echo "  7) 重新启动 PagerMaid"
    echo "  8) 重新安装 PagerMaid 依赖"
    echo "  9) 退出脚本"
    echo ""
    echo "     Version：1.0.1"
    echo ""
    echo -n "请输入编号: "
    read N
    case $N in
    1) start_installation ;;
    2) cleanup ;;
    3) reinstall ;;
    4) cleansession ;;
    5) stop_pager ;;
    6) start_pager ;;
    7) restart_pager ;;
    8) install_require ;;
    9) exit ;;
    *) echo "Wrong input!" ;;
    esac
}

check_sys
shon_online
