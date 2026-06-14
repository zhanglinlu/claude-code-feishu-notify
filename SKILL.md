---
name: claude-code-feishu-notify
description: 配置 Claude Code hooks，在 Claude Code 等待权限确认时通过飞书机器人发送通知到手机。当用户想要设置 Claude Code 飞书通知、连接飞书消息、配置权限确认时收到手机推送提醒、或通过 lark-cli 集成飞书机器人消息时使用此 skill。
---

# Claude Code 飞书通知配置

配置 Claude Code hooks，当 Claude Code 需要权限确认时，通过飞书机器人向用户发送消息通知。用户在手机或手表上通过飞书 App 收到推送提醒，无需盯着终端等待。

## 架构

```
Claude Code 等待权限确认
    ↓（Notification hook 触发）
Windows: cmd.exe / macOS-Linux: /bin/sh 调用 → python feishu-notify.py
    ↓
feishu-notify.py 调用：lark-cli im +messages-send --as bot
    ↓
飞书 API → 用户飞书 App 收到机器人消息（带推送通知）
```

## 前置条件

- Python 3.6+ 已安装且 `python` 命令可用
- Node.js/npm 已安装（用于 `npx` 安装 lark-cli）
- 拥有飞书/Lark 账号，能访问 [飞书开放平台](https://open.feishu.cn/)

## 分步配置流程

### 第一步：安装 lark-cli

检查 lark-cli 是否已安装：

```bash
lark-cli --version
```

如果未找到或报错，执行安装：

```bash
npx @larksuite/cli@latest install
```

安装完成后验证：

```bash
lark-cli --version
```

### 第二步：引导用户在飞书后台创建应用

向用户展示以下操作指引，等待用户完成：

```
请前往飞书开放平台完成以下操作：

1. 打开 https://open.feishu.cn/ 并登录
2. 点击「创建应用」→ 选择「企业自建应用」
3. 进入应用后，在左侧菜单「应用能力」→「添加应用能力」→ 开启「机器人」
4. 在左侧菜单「权限管理」中，搜索并开启以下权限：
   - im:message:send_as_bot（以应用身份发送消息）
   - im:message（获取与发送单聊、群组消息）
5. 在左侧「版本管理与发布」→ 创建版本 → 申请发布
   （如果你是企业管理员，可以直接审核通过）
6. 在左侧「凭证与基础信息」中，复制 App ID 和 App Secret

完成后请把 App ID 和 App Secret 发给我。
```

**必须等用户提供 App ID 和 App Secret 后再继续。**

### 第三步：配置 lark-cli 凭证

用用户提供的凭证配置 lark-cli，将 `<APP_ID>` 和 `<APP_SECRET>` 替换为实际值：

```bash
echo "<APP_SECRET>" | lark-cli config init --app-id <APP_ID> --app-secret-stdin
```

验证配置：

```bash
lark-cli config show
```

应显示 appId 和 brand，无报错。

### 第四步：用户授权登录（OAuth）

启动设备授权流程：

```bash
lark-cli auth login --no-wait --json --domain im
```

输出中包含 `verification_url`。**将此链接展示给用户**，并告知：

```
请打开飞书 App 或浏览器，访问以下链接完成授权（10 分钟内有效）：

<verification_url>

授权完成后请告诉我。
```

**必须等用户确认授权完成后再继续。**

用之前输出中的 `device_code` 完成登录：

```bash
lark-cli auth login --device-code "<device_code>"
```

输出中会显示用户的 `openId`（格式：`ou_xxxxxxxxxxxxxxxx`）。**记录这个 openId**，后续步骤需要用到。

### 第五步：安装并配置通知脚本

确定以下路径：

- `SKILL_DIR`：本 SKILL.md 所在目录
- `SCRIPT_SRC`：`<SKILL_DIR>/scripts/feishu-notify.py`
- `INSTALL_DIR`：脚本持久化安装目录，建议 `~/.claude/scripts/`（不存在则创建）
- `SCRIPT_DST`：`<INSTALL_DIR>/feishu-notify.py`
- `LOG_FILE`：`<INSTALL_DIR>/feishu-notify.log`

各平台典型路径示例：

| 项目 | Windows | macOS |
|---|---|---|
| INSTALL_DIR | `C:\Users\<用户名>\.claude\scripts\` | `/Users/<用户名>/.claude/scripts/` |
| SCRIPT_DST | `C:\Users\<用户名>\.claude\scripts\feishu-notify.py` | `/Users/<用户名>/.claude/scripts/feishu-notify.py` |
| LOG_FILE | `C:\Users\<用户名>\.claude\scripts\feishu-notify.log` | `/Users/<用户名>/.claude/scripts/feishu-notify.log` |

查找 lark-cli 可执行文件路径：

Windows：
```powershell
where.exe lark-cli
```
使用输出中的 `.cmd` 路径，例如：`C:\Users\zll\.version-fox\cache\nodejs\current\lark-cli.cmd`

macOS/Linux：
```bash
which lark-cli
```
使用输出的路径，例如：`/usr/local/bin/lark-cli` 或 `/Users/zll/.npm-global/bin/lark-cli`

复制脚本并替换占位符：

1. 将 `SCRIPT_SRC` 复制到 `SCRIPT_DST`
2. 替换脚本中的占位符：
   - `{{USER_ID}}` → 第四步获取的用户 openId
   - `{{LARK_CLI}}` → lark-cli 可执行文件的完整路径
   - `{{LOG_FILE}}` → 日志文件路径

使用 Python 一行命令完成替换（将尖括号内容替换为实际值）：

```python
python -c "
content = open(r'<SCRIPT_SRC>').read()
content = content.replace('{{USER_ID}}', '<OPEN_ID>')
content = content.replace('{{LARK_CLI}}', r'<LARK_CLI_PATH>')
content = content.replace('{{LOG_FILE}}', r'<LOG_FILE>')
open(r'<SCRIPT_DST>', 'w').write(content)
"
```

### 第六步：配置 Claude Code Hooks

将 hooks 配置写入 `~/.claude/settings.local.json`。

**重要**：如果 `settings.local.json` 已存在，保留其原有内容，只合并 `hooks` 字段。如果文件不存在，直接创建。

需要添加/合并的 hooks 配置：

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python <SCRIPT_DST 路径>"
          }
        ]
      }
    ]
  }
}
```

**关于 `command` 字段的关键注意事项：**

- Claude Code 在 Windows 上通过 `cmd.exe` 执行 hook 命令（macOS/Linux 上是 `/bin/sh`）
- Windows 路径中用正斜杠 `/` 代替反斜杠 `\\`，避免转义问题
- 必须用 `python`（或 `python3`）前缀来调用 `.py` 脚本

各平台 `command` 示例：

Windows：
```json
"command": "python C:/Users/zll/.claude/scripts/feishu-notify.py"
```

macOS：
```json
"command": "python3 /Users/zll/.claude/scripts/feishu-notify.py"
```

> 注意：macOS 上 Python 命令通常是 `python3` 而非 `python`，请根据用户实际环境确认。

### 第七步：测试验证

直接运行脚本验证是否正常工作：

```bash
python <SCRIPT_DST>
```

然后告知用户：

```
测试消息已发送，请检查你的飞书是否收到了来自机器人的消息。
如果收到了，请重启 Claude Code 使 hooks 配置生效。
```

如果未收到消息，检查 `<LOG_FILE>` 中的错误日志进行排查。

## 故障排查

### Bot ability is not activated

飞书应用的机器人能力未开启。前往飞书开放平台 → 应用能力 → 开启机器人 → 发布新版本。

### Token 过期

用户 OAuth token 会过期（access token 约 2 小时，refresh token 约 30 天）。重新执行：

```bash
lark-cli auth login --domain im
```

### subprocess 中找不到 lark-cli

脚本使用的是 lark-cli 的绝对路径。如果 Node.js 版本管理器切换了路径，重新执行第五步更新脚本中的 `LARK_CLI` 路径。

### settings.local.json 权限被拒绝

确保 Claude Code 配置目录 `~/.claude/` 存在且可写。

### macOS 上 `python` 命令不存在

macOS 默认可能没有 `python` 命令，只有 `python3`。解决方法：
- hooks 的 `command` 中改用 `python3`
- 或安装 `python-is-python3`：`brew install python` 后用 `python3` 确认路径

## 智能手表通知提醒

如果希望在智能手表上也收到飞书消息提醒，需要确保以下权限全部开启：

1. **手机端飞书 App 的通知权限**
   - iOS：设置 → 通知 → 飞书 → 允许通知，并开启「锁定屏幕」「通知中心」「横幅」
   - Android：设置 → 应用 → 飞书 → 通知 → 全部开启

2. **手表端飞书 App 的通知权限**
   - Apple Watch：Watch App → 通知 → 飞书 → 选择「从 iPhone 镜像」或「自定」并开启
   - 其他智能手表：在手表配套 App 中找到飞书，开启消息通知转发

3. **手表与手机的蓝牙连接**
   - 确保手表与手机保持蓝牙连接，断开连接时手表无法收到通知

> 以上权限缺一不可，任何一层未开启都会导致手表无法收到提醒。

## 常见问题

**Q: 应该用哪个 hook 事件？**

用 `Notification`，它在 Claude Code 需要用户关注时触发（权限确认、任务完成等）。其他可用事件：`PreToolUse`、`PostToolUse`、`Stop`、`PermissionRequest`、`PermissionDenied`。

**Q: 脚本出错会影响 Claude Code 吗？**

不会。脚本始终以 `sys.exit(0)` 退出。错误只记录到 `feishu-notify.log`，不会阻塞 Claude Code。

**Q: Token 过期后如何刷新？**

lark-cli 会使用 refresh token（有效期约 30 天）自动刷新。如果通知停止工作，重新执行 `lark-cli auth login --domain im` 即可。

