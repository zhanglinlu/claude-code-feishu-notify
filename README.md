# Claude Code 飞书通知

当 Claude Code 在终端等待权限确认时，通过飞书机器人向你的手机和智能手表发送推送通知。

再也不用盯着终端等了。

## 工作原理

```
Claude Code 等待权限确认
    ↓
Notification Hook 触发
    ↓
Python 脚本调用 lark-cli
    ↓
飞书 API → 手机/手表收到机器人消息推送
```

## 使用方式

本仓库是一个 AI Agent Skill，可以直接交给 Claude、Codex 等 AI 工具使用。

### 快速开始

将以下内容发送给 AI 助手：

```
请帮我配置 Claude Code 的飞书通知功能。
仓库地址：https://github.com/zhanglinlu/claude-code-feishu-notify
请先克隆仓库，然后按照 SKILL.md 中的步骤帮我完成配置。
```

AI 助手会引导你完成以下流程：

1. 安装飞书 CLI 工具（lark-cli）
2. 在飞书开放平台创建应用并开启机器人能力
3. 配置应用凭证并完成 OAuth 授权
4. 自动安装通知脚本并写入 Claude Code hooks 配置
5. 发送测试消息验证配置

### 手动安装

如果你更习惯手动操作，可以参考 [SKILL.md](SKILL.md) 中的分步指南。

## 功能特性

- 飞书机器人消息推送，手机和手表都能收到通知
- 支持 Windows 和 macOS
- 脚本出错不影响 Claude Code 正常运行
- 所有错误记录到日志文件，方便排查
- Token 自动刷新，约 30 天内无需重新授权

## 前置条件

- Python 3.6+
- Node.js / npm（用于安装 lark-cli）
- 飞书账号，能访问[飞书开放平台](https://open.feishu.cn/)

## 智能手表支持

配置好以下权限即可在手表上收到通知：

- **iOS**：设置 → 通知 → 飞书 → 开启全部通知选项
- **Apple Watch**：Watch App → 通知 → 飞书 → 从 iPhone 镜像
- **Android**：设置 → 应用 → 飞书 → 通知 → 全部开启

详见 [SKILL.md](SKILL.md) 中的智能手表通知提醒章节。

## 文件结构

```
.
├── SKILL.md                    # AI Agent 配置指南（核心文件）
├── agents/
│   └── openai.yaml             # UI 元数据
├── scripts/
│   └── feishu-notify.py        # 飞书通知脚本模板
└── LICENSE
```

## 许可证

MIT License
