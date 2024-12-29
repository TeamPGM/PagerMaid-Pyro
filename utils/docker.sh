#!/usr/bin/env bash

if [[ $EUID -ne 0 ]]
then
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

welcome () {
    echo
    echo "安装即将开始"
    echo "如果您想取消安装，"
    echo "请在 5 秒钟内按 Ctrl+C 终止此脚本。"
    echo
    sleep 5
}

docker_check () {
    echo "正在检查 Docker 安装情况 . . ."
    if command -v docker >> /dev/null 2>&1;
    then
        echo "Docker 似乎存在, 安装过程继续 . . ."
    else
        echo "Docker 未安装在此系统上"
        echo "请安装 Docker 并将自己添加到 Docker"
        echo "分组并重新运行此脚本。"
        exit 1
    fi
}

access_check () {
    echo "测试 Docker 环境 . . ."
    if [ -w /var/run/docker.sock ]
    then
        echo "该用户可以使用 Docker , 安装过程继续 . . ."
    else
        echo "该用户无权访问 Docker，或者 Docker 没有运行。 请添加自己到 Docker 分组并重新运行此脚本。"
        exit 1
    fi
}

build_docker () {
    printf "请输入 PagerMaid 容器的名称："
    read -r container_name <&1
    echo "正在拉取 Docker 镜像 . . ."
    docker rm -f "$container_name" > /dev/null 2>&1
    docker pull teampgm/pagermaid_pyro
}

need_web () {
  PGM_WEB=false
  printf "请问是否需要启用 Web 管理界面 [Y/n] ："
  read -r web <&1
  case $web in
      [yY][eE][sS] | [yY])
          echo "您已确认需要启用 Web 管理界面 . . ."
          PGM_WEB=true
          printf "请输入管理员密码（如果不需要密码请直接回车）："
          read -r admin_password <&1
          ;;
      [nN][oO] | [nN])
          ;;
      *)
          echo "输入错误，已跳过。"
          ;;
  esac
}

need_web_login () {
  PGM_WEB_LOGIN=false
  case $PGM_WEB in
      true)
        printf "请问是否需要启用通过 Web 登录？（不建议开启） [Y/n] ："
        read -r web_login <&1
        case $web_login in
            [yY][eE][sS] | [yY])
                echo "您已确认需要启用 Web 登录界面 . . ."
                PGM_WEB_LOGIN=true
                ;;
            [nN][oO] | [nN])
                ;;
            *)
                echo "输入错误，已跳过。"
                ;;
        esac
        ;;
  esac
}

start_docker () {
    echo "正在启动 Docker 容器 . . ."
    case $PGM_WEB in
        true)
            docker run -dit --restart=always --name="$container_name" --hostname="$container_name" -e WEB_ENABLE="$PGM_WEB" -e WEB_SECRET_KEY="$admin_password" -e WEB_HOST=0.0.0.0 -e WEB_PORT=3333 -e WEB_LOGIN="$PGM_WEB_LOGIN" -p 3333:3333 teampgm/pagermaid_pyro <&1
            ;;
        *)
            docker run -dit --restart=always --name="$container_name" --hostname="$container_name" teampgm/pagermaid_pyro <&1
            ;;
    esac
    echo
    echo "开始配置参数 . . ."
    echo "在登录后，请按 Ctrl + C 使容器在后台模式下重新启动。"
    sleep 3
    docker exec -it "$container_name" bash utils/docker-config.sh
    echo
    echo "Docker 重启中，如果失败，请手动重启容器。"
    echo
    docker restart "$container_name"
    echo
    echo "Docker 创建完毕。"
    echo
}

data_persistence () {
    echo "数据持久化可以在升级或重新部署容器时保留配置文件和插件。"
    printf "请确认是否进行数据持久化操作 [Y/n] ："
    read -r persistence <&1
    case $persistence in
        [yY][eE][sS] | [yY])
            printf "请输入将数据保留在宿主机哪个路径（绝对路径），同时请确保该路径下没有名为 data 和 plugins 的文件夹 ："
            read -r data_path <&1
            if [ -d "$data_path" ]; then
                if [[ -z $container_name ]]; then
                    printf "请输入 PagerMaid 容器的名称："
                    read -r container_name <&1
                fi
                if docker inspect "$container_name" &>/dev/null; then
                    docker cp "$container_name":/pagermaid/workdir/data "$data_path"
                    docker cp "$container_name":/pagermaid/workdir/plugins "$data_path"
                    docker stop "$container_name" &>/dev/null
                    docker rm "$container_name" &>/dev/null
                    case $PGM_WEB in
                        true)
                            docker run -dit -v "$data_path"/data:/pagermaid/workdir/data -v "$data_path"/plugins:/pagermaid/workdir/plugins --restart=always --name="$container_name" --hostname="$container_name" -e WEB_ENABLE="$PGM_WEB" -e WEB_SECRET_KEY="$admin_password" -e WEB_HOST=0.0.0.0 -e WEB_PORT=3333 -p 3333:3333 teampgm/pagermaid_pyro <&1
                            ;;
                        *)
                            docker run -dit -v "$data_path"/data:/pagermaid/workdir/data -v "$data_path"/plugins:/pagermaid/workdir/plugins --restart=always --name="$container_name" --hostname="$container_name" teampgm/pagermaid_pyro <&1
                            ;;
                    esac
                    echo
                    echo "数据持久化操作完成。"
                    echo
                else
                    echo "不存在名为 $container_name 的容器，退出。"
                fi
            else
                echo "路径 $data_path 不存在，退出。"
            fi
            ;;
        [nN][oO] | [nN])
            echo "结束。"
            ;;
        *)
            echo "输入错误 . . ."
            ;;
    esac
}

start_installation () {
    welcome
    docker_check
    access_check
    build_docker
    need_web
    need_web_login
    start_docker
    data_persistence
}

cleanup () {
    printf "请输入 PagerMaid 容器的名称："
    read -r container_name <&1
    echo "开始删除 Docker 镜像 . . ."
    if docker inspect "$container_name" &>/dev/null; then
        docker rm -f "$container_name" &>/dev/null
        echo
        shon_online
    else
        echo "不存在名为 $container_name 的容器，退出。"
        exit 1
    fi
}

stop_pager () {
    printf "请输入 PagerMaid 容器的名称："
    read -r container_name <&1
    echo "正在关闭 Docker 镜像 . . ."
    if docker inspect "$container_name" &>/dev/null; then
        docker stop "$container_name" &>/dev/null
        echo
        shon_online
    else
        echo "不存在名为 $container_name 的容器，退出。"
        exit 1
    fi
}

start_pager () {
    printf "请输入 PagerMaid 容器的名称："
    read -r container_name <&1
    echo "正在启动 Docker 容器 . . ."
    if docker inspect "$container_name" &>/dev/null; then
        docker start "$container_name" &>/dev/null
        echo
        echo "Docker 启动完毕。"
        echo
        shon_online
    else
        echo "不存在名为 $container_name 的容器，退出。"
        exit 1
    fi
}

restart_pager () {
    printf "请输入 PagerMaid 容器的名称："
    read -r container_name <&1
    echo "正在重新启动 Docker 容器 . . ."
    if docker inspect "$container_name" &>/dev/null; then
        docker restart "$container_name" &>/dev/null
        echo
        echo "Docker 重新启动完毕。"
        echo
        shon_online
    else
        echo "不存在名为 $container_name 的容器，退出。"
        exit 1
    fi
}

reinstall_pager () {
    cleanup
    build_docker
    need_web
    need_web_login
    start_docker
    data_persistence
}

shon_online () {
    echo "一键脚本出现任何问题请转手动搭建！ xtaolabs.com"
    echo "一键脚本出现任何问题请转手动搭建！ xtaolabs.com"
    echo "一键脚本出现任何问题请转手动搭建！ xtaolabs.com"
    echo ""
    echo ""
    echo "欢迎使用 PagerMaid-Pyro Docker 一键安装脚本。"
    echo
    echo "请选择您需要进行的操作:"
    echo "  1) Docker 安装 PagerMaid"
    echo "  2) Docker 卸载 PagerMaid"
    echo "  3) Docker 关闭 PagerMaid"
    echo "  4) Docker 启动 PagerMaid"
    echo "  5) Docker 重启 PagerMaid"
    echo "  6) Docker 重装 PagerMaid"
    echo "  7) PagerMaid 数据持久化"
    echo "  8) 退出脚本"
    echo
    echo "     Version：2.3.0"
    echo
    echo -n "请输入编号: "
    read -r N <&1
    case $N in
        1)
            start_installation
            ;;
        2)
            cleanup
            ;;
        3)
            stop_pager
            ;;
        4)
            start_pager
            ;;
        5)
            restart_pager
            ;;
        6)
            reinstall_pager
            ;;
        7)  
            printf "请输入 PagerMaid 容器的名称："
            read -r container_name <&1
            if docker inspect "$container_name" &>/dev/null; then
                data_persistence
            else
                echo "不存在名为 $container_name 的容器，退出。"
                exit 1
            fi
            ;;
        8)
            exit 0
            ;;
        *)
            echo "Wrong input!"
            sleep 5s
            shon_online
            ;;
    esac 
}

shon_online
