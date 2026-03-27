可以，**如果你已经接入了 MagicSkills CLI，优先直接用 `magicskills scanskill` 或 `magicskills scanskills`**。只有当你想手工排查 AI-Infra-Guard 的底层接口时，再按后面的 `curl` 流程逐步调用。

## 推荐：直接用 CLI 扫描

先准备 AIG 和模型配置：

```bash
export MAGICSKILLS_AIG_BASE_URL=http://localhost:8088
export MAGICSKILLS_AIG_MODEL=qwen3-max
export MAGICSKILLS_AIG_API_KEY="$OPENAI_API_KEY"
export MAGICSKILLS_AIG_MODEL_BASE_URL="$OPENAI_BASE_URL"
```

扫描单个 skill：

```bash
magicskills scanskill /root/test-skill
```

扫描一个命名 skills 集合：

```bash
magicskills scanskills haystack_agent2_skills
```

### CLI 输出模式

- 默认输出：
  - `scanskill`：只显示 `Skill Summary` 和 `Skill Results`
  - `scanskills`：只显示 `Skills Summary` 和 `Skills Results`
- `--details`：
  - 在默认摘要后，继续打印格式化的详细内容
  - 不会打印原始 JSON
- `--save-raw`：
  - 保存与 `--details` 一致的格式化详细文本
  - 如果不传路径，默认保存在当前工作目录
  - 默认扩展名是 `.txt`
  - 参数名为了兼容性保留为 `--save-raw`，但现在保存的不再是 JSON，而是格式化文本报告

示例：

```bash
magicskills scanskill /root/test-skill --details
magicskills scanskill /root/test-skill --save-raw
magicskills scanskills haystack_agent2_skills --details
magicskills scanskills haystack_agent2_skills --save-raw ./reports/haystack-agent2-skills.txt
```

## 手工调用 AIG 接口

如果你现在不想写 Python 调用代码，只想纯手工完成一次 skill 扫描，就按下面这个顺序做就行。

你现在已经把 AI-Infra-Guard 服务启动了，而且 `docker ps` 里看到 `ai-infra-guard-webserver` 是 `healthy`，说明后端已经能接请求了。接下来你手工做的事情，本质上就是把代码里的 4 个步骤自己用命令执行一遍：**准备 skill 目录、压缩、上传、创建扫描任务、查状态、取结果**。

第一步，先准备一个合法的 skill 目录。
这个目录至少要是个文件夹，而且里面要有 `SKILL.md`。因为你前面的 `scanskill` 逻辑就是这么校验的：目录存在、是目录、并且包含 `SKILL.md`。如果你只是想测试，可以自己先造一个最小 skill：

```bash
mkdir -p /root/test-skill
cat > /root/test-skill/SKILL.md <<'EOF'
---
name: test-skill
description: a simple test skill
---

This is a test skill.
EOF
```

第二步，把这个目录打成 zip。
因为 AIG 的上传接口收的是文件，不是直接收目录。

```bash
cd /root
zip -r test-skill.zip test-skill
```

打完以后，你本地会有一个 `/root/test-skill.zip`。

第三步，手工上传 zip。
上传接口是：

```bash
http://localhost:8088/api/v1/app/taskapi/upload
```

命令这样跑：

```bash
curl -X POST http://localhost:8088/api/v1/app/taskapi/upload -F "file=@/root/test-skill.zip"
```

这一步成功后，它会返回一段 JSON。你最需要看的字段是：

```json
data.fileUrl
```

你把这个值记下来。后面创建扫描任务时要用它。
举个例子，它可能像这样：

```json
{
  "status": 0,
  "data": {
    "fileUrl": "http://localhost:8088/uploads/xxxx.zip"
  }
}
```

第四步，手工创建扫描任务。
这一步就是告诉 AIG：“刚才那个 zip，不只是上传保存，现在正式拿去扫。”

你需要准备几个值：

第一是 `fileUrl`，也就是刚才上传返回的地址。
第二是模型配置，也就是：

* `model`
* `token`
* `base_url`（如果你的模型服务需要）

然后执行：

```bash
curl -X POST http://localhost:8088/api/v1/app/taskapi/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "type": "mcp_scan",
    "content": {
      "prompt": "扫描这个 agent skill 是否安全，重点关注恶意命令执行、数据泄露、提示注入、越权访问、供应链风险",
      "model": {
        "model": "gpt-4",
        "token": "你的API_KEY",
        "base_url": "https://api.openai.com/v1"
      },
      "thread": 4,
      "language": "zh",
      "attachments": "这里替换成刚才的fileUrl"
    }
  }'
```

这一步返回后，你最需要看的字段是：

```json
data.session_id
```

这个 `session_id` 就是这次扫描任务的编号。

第五步，查任务状态。
创建任务以后不是马上就出结果，所以你要轮询状态接口：

```bash
curl http://localhost:8088/api/v1/app/taskapi/status/你的session_id
```

如果还没完成，你就隔几秒再查一次。
你主要看返回里的 `data.status`。
如果变成完成状态，就进入下一步；如果失败，就看 `data.log`。

第六步，取最终结果。
等任务完成后，调用结果接口：

```bash
curl http://localhost:8088/api/v1/app/taskapi/result/你的session_id
```

这一步返回的就是完整扫描结果。
你可以先直接看原始 JSON，也可以后面自己再从里面挑你关心的字段，比如风险等级、发现项数量、原因说明。

如果你想更省事一点，我建议你第一次手工测试时，直接就按这个最短流程走：

先造一个最小 skill 目录，
再 zip，
再上传，
再创建任务，
再查状态，
最后取结果。

也就是说，**纯手工版其实只需要 4 个核心接口动作**：

1. `upload`
2. `tasks`
3. `status/{session_id}`
4. `result/{session_id}`

如果你现在已经有自己的 skill 目录了，我可以直接把上面那几条命令替换成你的实际路径，给你拼成一套能直接复制执行的版本。
