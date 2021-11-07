# lae-tunnel-client
Light App Engine Tunnel Client

支持平台：`Windows` `Linux` `macOS`

## 创建隧道

此操作目前不支持在程序内执行，请前往 Lae 的 `穿透隧道` 中创建隧道。

## 如何启动

请注意：或许你需要自备 frpc 程序, 你可以在 `config.yml` 修改启动命令

### Windows
1. 在 Releases 下载最新的版本.
2. (可选) 修改 `config.yml`
3. 运行 `lae-tunnel.exe`
4. (可选) 使用启动参数运行

### Linux
1. 确保安装 `Python3`
2. 在 Releases 下载最新的版本.
3. (可选) 修改 `config.yml`
4. 执行 `python lae-tunnel.py`
5. (可选) 使用启动参数运行

### macOS
同 Linux.

## 启动参数

这部分是可选的，使用参数启动，可直接启动隧道。

例如你可以在 `lae-tunnel.exe` 同目录下创建一个 bat 文件，比如 `start.cmd`

在其中填入参数，完整的参数例如 `lae-tunnel.exe --token 123456 --tunnel 3,5,#1`

其中 `token` 的值需要到 Lae 的 `用户名 / 积分` 里点击 `更新访问密钥` 后，在右下角复制获取。

其中 `tunnel` 的值为对应的隧道 ID，你需要手动启动一次 `lae-tunnel.exe` 查看隧道 ID。你也可以使用 `#` 前缀后接项目 ID，启动该项目下所有隧道，项目 ID 获取方式同隧道 ID 获取方式。
