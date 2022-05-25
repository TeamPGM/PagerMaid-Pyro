#!/usr/bin/with-contenv bash

welcome () {
    echo 
    echo "欢迎进入 PagerMaid-Pyro Docker 。"
    echo "配置即将开始"
    echo 
    sleep 2
}

configure () {
    local config_file=config.yml

    echo "生成配置文件中 . . ."
    cp config.gen.yml $config_file
    echo "api_id、api_hash 申请地址： https://my.telegram.org/"
    printf "请输入应用程序 api_id："
    read -r api_id <&1
    sed -i "s/ID_HERE/$api_id/" $config_file
    printf "请输入应用程序 api_hash："
    read -r api_hash <&1
    sed -i "s/HASH_HERE/$api_hash/" $config_file
    printf "请输入应用程序语言（默认：zh-cn）："
    read -r application_language <&1
    if [ -z "$application_language" ]
    then
        echo "语言设置为 简体中文"
    else
        sed -i "s/zh-cn/$application_language/" $config_file
    fi
    printf "请输入应用程序地区（默认：China）："
    read -r application_region <&1
    if [ -z "$application_region" ]
    then
        echo "地区设置为 中国"
    else
        sed -i "s/China/$application_region/" $config_file
    fi
    printf "请输入 Google TTS 语言（默认：zh-CN）："
    read -r application_tts <&1
    if [ -z "$application_tts" ]
    then
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
            if [ -z "$log_chatid" ]
            then
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

login () {
    echo
    echo "下面进行程序运行。"
    echo "请在账户授权完毕后，按 Ctrl + C 使 Docker 在后台模式下运行。"
    echo
    sleep 2
    echo "Hello world!" > /pagermaid/workdir/install.lock
    python -m pagermaid
    exit 0
}

main () {
    cd /pagermaid/workdir
    if [ ! -s "/pagermaid/workdir/install.lock" ]; then
        welcome
        configure
        login
    else
        if [ ! -f "/pagermaid/workdir/pagermaid.session" ]; then
            login
        fi
    fi
}

main
