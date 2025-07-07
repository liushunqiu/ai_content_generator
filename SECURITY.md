# 安全配置指南

## ⚠️ 重要安全提醒

在提交代码到GitHub之前，请务必确保以下安全措施：

## 🔐 敏感信息保护

### 1. API密钥保护

**绝对不要**将真实的API密钥提交到Git仓库！

#### 检查清单：
- [ ] `.env` 文件已添加到 `.gitignore`
- [ ] 所有API密钥都使用占位符（如 `your-api-key-here`）
- [ ] 真实密钥只存储在本地 `.env` 文件和GitHub Secrets中

#### 如果意外提交了API密钥：
1. **立即撤销**该API密钥
2. **生成新的**API密钥
3. **清理Git历史**（如果必要）
4. **更新**所有使用该密钥的地方

### 2. 环境变量配置

#### 本地开发：
```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，填入真实的API密钥
nano .env
```

#### GitHub Actions：
在GitHub仓库设置中配置Secrets：
- `GEMINI_API_KEY`
- `WECHAT_WEBHOOK_URL`
- 其他需要的API密钥

## 📁 文件保护

### 已忽略的文件类型：

#### 敏感配置文件：
- `.env` - 环境变量文件
- `*.env` - 所有环境变量文件
- `config.json` - 配置文件
- `secrets.json` - 密钥文件
- `api_keys.txt` - API密钥文件

#### 生成的内容：
- `output/` - 生成的文章
- `data/` - 数据文件
- `media/` - 生成的图片
- `logs/` - 日志文件
- `*.log` - 所有日志文件

#### 系统文件：
- `__pycache__/` - Python缓存
- `.DS_Store` - macOS系统文件
- `Thumbs.db` - Windows缩略图
- `.vscode/` - VSCode配置
- `.idea/` - PyCharm配置

## 🔍 提交前检查

### 使用以下命令检查将要提交的文件：

```bash
# 查看将要提交的文件
git status

# 查看具体的更改内容
git diff

# 查看暂存区的内容
git diff --cached
```

### 确保以下文件**不在**提交列表中：
- `.env`
- 任何包含真实API密钥的文件
- 生成的内容文件（output/, data/, media/, logs/）
- 个人配置文件

## 🛡️ 最佳实践

### 1. 定期检查
```bash
# 检查是否有敏感文件被跟踪
git ls-files | grep -E "\.(env|key|secret|config)$"

# 检查最近的提交
git log --oneline -10
```

### 2. 使用环境变量
```python
import os
from dotenv import load_dotenv

load_dotenv()

# 正确的方式
api_key = os.getenv('GEMINI_API_KEY')

# 错误的方式 - 不要硬编码API密钥
# api_key = "AIzaSyDsA4SFQqgsUPjIt2GTN6P0B9HV_4SbLOI"
```

### 3. 分离配置
- **开发环境**：使用 `.env` 文件
- **生产环境**：使用GitHub Secrets或环境变量
- **示例配置**：使用 `.env.example` 文件

## 🚨 应急响应

### 如果意外泄露了API密钥：

#### 立即行动：
1. **撤销密钥**：
   - Google Gemini: https://aistudio.google.com/app/apikey
   - 企业微信: 重新生成机器人

2. **生成新密钥**：
   - 创建新的API密钥
   - 更新本地 `.env` 文件
   - 更新GitHub Secrets

3. **清理历史**（如果需要）：
```bash
# 从Git历史中完全删除文件
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch .env' \
--prune-empty --tag-name-filter cat -- --all

# 强制推送（谨慎使用）
git push origin --force --all
```

## 📋 安全检查清单

提交前请确认：

- [ ] `.env` 文件不在Git跟踪中
- [ ] 所有API密钥都使用环境变量
- [ ] `.gitignore` 文件包含所有敏感文件类型
- [ ] 代码中没有硬编码的密钥或密码
- [ ] 生成的内容文件不会被提交
- [ ] 日志文件不包含敏感信息

## 🔗 相关资源

- [GitHub Secrets 文档](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Git 安全最佳实践](https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage)
- [Python dotenv 文档](https://python-dotenv.readthedocs.io/)

---

> ⚠️ **记住**：一旦API密钥泄露到公共仓库，就应该立即视为已被泄露，需要立即撤销并重新生成。
