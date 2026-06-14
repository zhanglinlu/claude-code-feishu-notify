import json, subprocess, sys
from datetime import datetime

# === 配置区域（安装时自动填充） ===
USER_ID = "{{USER_ID}}"
LARK_CLI = "{{LARK_CLI}}"
LOG_FILE = "{{LOG_FILE}}"
# ================================

hook_input = ""
try:
    hook_input = sys.stdin.read()
except:
    pass

message = "Claude Code needs your attention"
if hook_input and hook_input.strip():
    try:
        data = json.loads(hook_input)
        if data.get("message"):
            message = data["message"]
    except:
        pass

result = subprocess.run(
    [LARK_CLI, "im", "+messages-send",
     "--user-id", USER_ID,
     "--text", message,
     "--as", "bot"],
    capture_output=True, timeout=15, encoding='utf-8'
)

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(LOG_FILE, "a", encoding="utf-8") as f:
    f.write(f"[{timestamp}] msg={message} | ok={result.returncode == 0}\n")

sys.exit(0)
