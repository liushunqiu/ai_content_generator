# GitHub Actions 自动化部署指南

## 概述

本项目支持通过GitHub Actions实现每日自动生成AI内容，并通过企业微信群机器人推送文件。

## 部署步骤

### 1. 准备工作

#### 1.1 获取Google Gemini API密钥
1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 创建新的API密钥
3. 保存API密钥备用

#### 1.2 配置企业微信群机器人
1. 在企业微信群中添加群机器人：
   - 打开企业微信群聊
   - 点击右上角"..."
   - 选择"群机器人"
   - 点击"添加机器人"
   - 设置机器人名称和头像
   - 复制Webhook地址（格式：`https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxxxx`）

### 2. GitHub仓库配置

#### 2.1 上传代码到GitHub
```bash
# 初始化Git仓库
git init

# 添加远程仓库
git remote add origin https://github.com/你的用户名/你的仓库名.git

# 添加所有文件
git add .

# 提交代码
git commit -m "Initial commit: AI content generator"

# 推送到GitHub
git push -u origin main
```

#### 2.2 配置GitHub Secrets
在GitHub仓库中设置以下Secrets：

1. 进入仓库 → Settings → Secrets and variables → Actions
2. 点击"New repository secret"添加以下密钥：

| Secret名称 | 值 | 说明 |
|-----------|---|------|
| `GEMINI_API_KEY` | 你的Gemini API密钥 | 必需，用于AI内容生成 |
| `WECHAT_WEBHOOK_URL` | 企业微信机器人Webhook URL | 必需，用于推送消息和文件 |
| `PRODUCTHUNT_TOKEN` | Product Hunt API Token | 可选，用于获取产品数据 |
| `GITHUB_TOKEN` | GitHub Personal Access Token | 可选，用于获取GitHub数据 |

### 3. 工作流配置

#### 3.1 自动运行时间
默认配置为每天北京时间上午9点运行（UTC时间1点）。

如需修改时间，编辑 `.github/workflows/daily-content-generation.yml` 文件中的cron表达式：
```yaml
schedule:
  # 每天北京时间上午9点运行 (UTC时间1点)
  - cron: '0 1 * * *'
```

#### 3.2 手动触发
除了定时运行，还可以手动触发工作流：
1. 进入仓库 → Actions
2. 选择"Daily AI Content Generation"工作流
3. 点击"Run workflow"

### 4. 功能说明

#### 4.1 内容生成规则
系统根据星期几自动选择内容类型：
- 周一：新工具发现
- 周二：使用教程
- 周三：案例分析
- 周四：工具对比
- 周五：周报汇总
- 周六：互动问答
- 周日：资源合集

#### 4.2 推送功能
1. **文本通知**：生成完成后发送包含文章摘要的文本消息
2. **文件推送**：将完整的Markdown文章文件直接推送到企业微信群

#### 4.3 文件存储
- 生成的文章保存在 `output/` 目录
- 日志文件保存在 `logs/` 目录
- GitHub Actions会自动保存这些文件作为构建产物（保留30天）

### 5. 监控和调试

#### 5.1 查看运行日志
1. 进入仓库 → Actions
2. 点击具体的工作流运行记录
3. 查看详细的执行日志

#### 5.2 常见问题

**问题1：API密钥错误**
- 检查GitHub Secrets中的`GEMINI_API_KEY`是否正确
- 确认API密钥有效且有足够的配额

**问题2：企业微信推送失败**
- 检查`WECHAT_WEBHOOK_URL`是否正确
- 确认机器人在目标群中且有发送权限
- 检查文件大小是否超过20MB限制

**问题3：工作流不运行**
- 确认仓库是公开的，或者有GitHub Actions的使用权限
- 检查cron表达式是否正确
- 确认工作流文件路径正确（`.github/workflows/`）

**问题4：Actions版本弃用警告**
- 我们已经更新到最新版本：
  - `actions/upload-artifact@v4`
  - `actions/setup-python@v5`
  - `actions/cache@v4`
- 如果仍有警告，请检查GitHub Actions文档获取最新版本

#### 5.3 失败通知
如果任务执行失败，系统会自动发送失败通知到企业微信群。

### 6. 本地测试

如需在本地测试（保留代理配置）：
```bash
python ai_writer.py  # 使用原版本（包含代理配置）
```

GitHub Actions环境：
```bash
python ai_writer_github.py  # 使用GitHub版本（无代理配置）
```

### 7. 自定义配置

#### 7.1 修改内容类型
编辑 `ai_writer_github.py` 中的 `content_schedule` 字典来自定义每日内容类型。

#### 7.2 添加数据源
在 `data_sources` 字典中添加新的RSS源或API接口。

#### 7.3 调整生成频率
修改 `.github/workflows/daily-content-generation.yml` 中的cron表达式。

## 注意事项

1. **代理配置**：GitHub Actions环境不需要代理，已在`ai_writer_github.py`中移除
2. **文件大小限制**：企业微信文件上传限制为20MB
3. **API配额**：注意Gemini API的使用配额限制
4. **时区**：cron表达式使用UTC时间，需要转换为本地时间

## 支持

如有问题，请查看：
1. GitHub Actions运行日志
2. 企业微信群中的错误通知
3. 项目Issues页面
