# Don't Starve Together Server
---

> 《Don't Starve》是一款充满魔法与科学的荒野生存游戏。这个世界里充满了未知生物、危险与惊喜，用你手边的任何东西来在这个世界里生存下去吧！
> 
> 《Dont't Starve Together》是《Dont't Starve》的线上多人合作版。

您可以在 DaoCloud 上使用 Docker 快速部署一个您自己的独立 Don't Starve Together 服务器，不受传统主机开关机限制。

容器启动时需要从 Steam 下载相关软件，视网络情况可能需要 5 到 10 分钟左右。

## 配置要求

### 1~2 人

- 建议 512M 内存

### 3~5 人

- 建议 1024M 内存

### 6 人或以上

- 2048M 内存或以上

## 环境变量

### `DEFAULT_SERVER_NAME` 服务器名

例：`DaoCloud's World`

### `CLUSTER_TOKEN` 创建在线服务器的 Token

例：`aHR0cHM6Ly9yZWFsaXR5MG5lLmNvbS8j`

为了运行在线服务器需要一个 `cluster_token.txt` 文件，这个文件提供了 Don't Starve Together 的所有权，并允许 Klei 公司改善那些违反了条款的服务器。

您需要通过以下方式生成 Token 文件：

运行 Don't Starve Together，点击多人游戏，按下 ~ 键打开开发者控制台，并输入：

```lua
TheNet:GenerateServerToken()
```

这条命令会生成 `server_token.txt` 文件，一般它如下位置：

```
On Windows:

/My Documents/Klei/DoNotStarveTogether/server_token.txt

On Linux:

~/.klei/DoNotStarveTogether/server_token.txt
 
On OS X:
 
~/Documents/Klei/DoNotStarveTogether/server_token.txt
```

### `SERVER_PASSWORD` 服务器的密码

例：`am9ic0BkYW9jbG91ZC5pbw==`

不填写则为开放主机，任何人都能加入您的游戏。

### 其他设置

- `DEFAULT_SERVER_DESCRIPTION` 服务器描述
- `MAX_PLAYERS` 最大玩家数
- `PVP` 是否开启 PVP（true, false）
- `GAME_MODE` 游戏模式（endless, survival, wilderness）
- `PAUSE_WHEN_ENPTY` 无人时暂停（true, false）

## 存档

您可以使用 Volume 来持久化储存您的存档，您可以将 Volume 挂载至 `/save` 目录来管理您的存档。

## 使用 Docker Compose

您也可以使用 Docker Compose 来快速在您的自由主机上部署一个 Don't Starve Together 服务器。

```yaml
dstserver: 
  image: daocloud.io/daocloud/dstserver:latest 
  environment: 
    - DEFAULT_SERVER_NAME=DaoCloud's World
    - CLUSTER_TOKEN=aHR0cHM6Ly9yZWFsaXR5MG5lLmNvbS8j
    - SERVER_PASSWORD=am9ic0BkYW9jbG91ZC5pbw==
    - DEFAULT_SERVER_DESCRIPTION=DaoCloud's World Run In Docker
    - GAME_MODE=survival
  ports: 
    - "10999:10999/udp"
  volumes:
    - /opt/dstserver:/save
  restart: always
```
