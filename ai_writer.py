#!/usr/bin/env python3
"""
AI工具公众号自动化内容生成器 - 精简版
使用Google Gemini AI自动生成高质量的公众号文章
"""

import os
import json
import schedule
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import feedparser
from media_generator import MediaGenerator

# 设置代理（如果需要访问Google API）
os.environ['https_proxy'] = 'http://127.0.0.1:7890'
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['all_proxy'] = 'socks5://127.0.0.1:7890'

# 加载环境变量
load_dotenv()

class AIContentWriter:
    """AI内容生成器"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key or self.api_key == 'your-gemini-api-key-here':
            raise ValueError("请在 .env 文件中设置正确的 GEMINI_API_KEY")

        # 初始化Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        # 注意：移除了媒体生成器，专注于AI绘画提示词生成
        # self.media_generator = MediaGenerator()

        # 内容类型配置
        self.content_schedule = {
            0: "new_tool",      # 周一：新工具发现
            1: "tutorial",      # 周二：使用教程
            2: "case_study",    # 周三：案例分析
            3: "comparison",    # 周四：工具对比
            4: "weekly_summary", # 周五：周报汇总
            5: "qa_interactive", # 周六：互动问答
            6: "resource_list"   # 周日：资源合集
        }

        print("🤖 AI内容生成器初始化成功！")
    
    def get_today_content_type(self):
        """获取今天应该生成的内容类型"""
        today = datetime.now().weekday()
        return self.content_schedule.get(today, "new_tool")
    
    def collect_ai_tools(self):
        """收集最新的AI工具信息"""
        tools = []

        # 更新的RSS源 - 专注于AI工具和产品资讯
        rss_feeds = [
            'https://techcrunch.com/category/artificial-intelligence/feed/',  # TechCrunch AI分类
            'https://www.theverge.com/ai-artificial-intelligence/rss/index.xml',  # The Verge AI
            'https://venturebeat.com/ai/feed/',  # VentureBeat AI
            'https://feeds.feedburner.com/oreilly/radar',  # O'Reilly Radar (备用)
        ]

        print("🔍 正在收集最新AI工具资讯...")

        for feed_url in rss_feeds:
            try:
                print(f"📡 检查数据源: {feed_url.split('/')[2]}")
                feed = feedparser.parse(feed_url)

                if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                    print(f"⚠️ 数据源无响应，跳过")
                    continue

                found_tools = 0
                for entry in feed.entries[:5]:  # 每个源取5篇最新的
                    title = entry.title.lower()
                    summary = getattr(entry, 'summary', '').lower()
                    content = f"{title} {summary}"

                    # 更精确的AI工具关键词匹配
                    ai_keywords = [
                        'ai tool', 'ai app', 'chatgpt', 'gpt-4', 'claude', 'gemini',
                        'midjourney', 'dall-e', 'stable diffusion', 'ai assistant',
                        'artificial intelligence', 'machine learning tool', 'ai platform',
                        'ai startup', 'new ai', 'ai launch', 'ai release'
                    ]

                    if any(keyword in content for keyword in ai_keywords):
                        # 提取工具名称（简化版）
                        tool_name = entry.title
                        if ':' in tool_name:
                            tool_name = tool_name.split(':')[0].strip()

                        tools.append({
                            'name': tool_name,
                            'description': getattr(entry, 'summary', entry.title)[:200],
                            'url': getattr(entry, 'link', ''),
                            'source': 'rss',
                            'published': getattr(entry, 'published', ''),
                            'feed_source': feed_url.split('/')[2]
                        })
                        found_tools += 1

                        if found_tools >= 2:  # 每个源最多取2个
                            break

                print(f"✅ 找到 {found_tools} 个相关工具")

            except Exception as e:
                print(f"❌ RSS采集错误 ({feed_url.split('/')[2]}): {e}")

        # 如果没有收集到工具，使用精选的热门工具库
        if not tools:
            print("📚 使用精选工具库...")
            tools = self._get_curated_ai_tools()
        else:
            print(f"🎯 共收集到 {len(tools)} 个最新AI工具")

        return tools

    def _get_curated_ai_tools(self):
        """精选的AI工具库 - 2025年7月更新"""
        curated_tools = [
            {
                'name': 'ChatGPT',
                'description': 'OpenAI开发的强大对话式AI助手，支持GPT-4o模型，能够进行复杂对话、写作、编程、图像分析等任务',
                'url': 'https://chat.openai.com',
                'source': 'curated',
                'category': '对话AI',
                'hot_features': ['GPT-4o', '多模态', '实时对话', 'Code Interpreter'],
                'last_updated': '2025-07'
            },
            {
                'name': 'Claude',
                'description': 'Anthropic开发的AI助手，擅长长文本分析、写作和对话，支持200K上下文，注重安全性和有用性',
                'url': 'https://claude.ai',
                'source': 'curated',
                'category': '对话AI',
                'hot_features': ['200K上下文', '文档分析', '代码生成', '安全对话'],
                'last_updated': '2025-07'
            },
            {
                'name': 'Midjourney',
                'description': '顶级AI图像生成工具，V6版本画质惊艳，通过Discord使用，能创造出艺术级别的图像作品',
                'url': 'https://midjourney.com',
                'source': 'curated',
                'category': '图像生成',
                'hot_features': ['V6版本', '超高画质', '艺术风格', 'Discord集成'],
                'last_updated': '2025-07'
            },
            {
                'name': 'Suno AI',
                'description': '革命性的AI音乐生成工具，只需文字描述就能创作完整的歌曲，包括歌词、旋律和人声',
                'url': 'https://suno.ai',
                'source': 'curated',
                'category': '音频生成',
                'hot_features': ['AI作曲', '人声合成', '多种风格', '完整歌曲'],
                'last_updated': '2025-07'
            },
            {
                'name': 'Cursor',
                'description': '基于AI的代码编辑器，集成了强大的AI编程助手，比GitHub Copilot更智能的代码生成',
                'url': 'https://cursor.sh',
                'source': 'curated',
                'category': '编程工具',
                'hot_features': ['AI编程', '智能补全', '代码解释', '多语言支持'],
                'last_updated': '2025-07'
            },
            {
                'name': 'Perplexity AI',
                'description': 'AI搜索引擎，结合了搜索和对话功能，提供准确的信息和引用来源，被称为"Google杀手"',
                'url': 'https://perplexity.ai',
                'source': 'curated',
                'category': '搜索工具',
                'hot_features': ['实时搜索', '引用来源', '对话式搜索', '多模态查询'],
                'last_updated': '2025-07'
            },
            {
                'name': 'Runway ML',
                'description': '专业的AI视频生成和编辑工具，Gen-3模型能生成高质量视频，支持文字转视频',
                'url': 'https://runwayml.com',
                'source': 'curated',
                'category': '视频生成',
                'hot_features': ['Gen-3模型', '文字转视频', '视频编辑', '专业级质量'],
                'last_updated': '2025-07'
            },
            {
                'name': 'Gamma',
                'description': 'AI演示文稿生成工具，只需输入主题就能自动生成精美的PPT，支持多种模板和风格',
                'url': 'https://gamma.app',
                'source': 'curated',
                'category': '办公工具',
                'hot_features': ['自动生成PPT', '精美模板', '一键美化', '协作功能'],
                'last_updated': '2025-07'
            }
        ]

        # 随机选择一个工具，避免总是同一个
        import random
        selected_tool = random.choice(curated_tools)

        # 添加一些随机的"最新动态"让内容更新鲜
        updates = [
            "最近推出了新功能",
            "用户数量突破新高",
            "获得了新一轮融资",
            "发布了重大更新",
            "在社交媒体上引起热议",
            "被知名博主强烈推荐"
        ]

        selected_tool['recent_update'] = random.choice(updates)
        return [selected_tool]
    
    def generate_article(self, content_type, data=None):
        """根据内容类型生成文章"""
        
        if content_type == "new_tool":
            return self.generate_new_tool_article(data)
        elif content_type == "tutorial":
            return self.generate_tutorial_article(data)
        elif content_type == "weekly_summary":
            return self.generate_weekly_summary()
        else:
            return self.generate_general_article(content_type)
    
    def generate_new_tool_article(self, tool_data):
        """生成新工具介绍文章"""
        prompt = f"""
        你是一个资深的科技博主，有5年的AI工具测评经验。请为AI工具"{tool_data['name']}"写一篇微信公众号文章。

        工具信息：
        - 名称：{tool_data['name']}
        - 描述：{tool_data['description']}
        - 网址：{tool_data.get('url', '未知')}

        写作要求：
        1. 用第一人称"我"来写，就像你真的用过这个工具一样
        2. 加入一些个人使用体验，比如"我试了一下发现..."、"说实话，刚开始我也..."
        3. 用口语化的表达，避免官方介绍的语气
        4. 可以吐槽一下其他类似工具的不足，突出这个工具的优势
        5. 加入一些真实的使用场景，比如"昨天我用它帮客户..."
        6. 语言要接地气，像朋友聊天一样，多用"哈哈"、"真的"、"不过"等口语词
        7. 标题要有冲击力：🔥[工具名]太牛了！我用了一周，效率翻了3倍
        8. 结尾要真诚地推荐，并问读者的使用感受
        9. 使用标准Markdown格式：**粗体**、*斜体*、## 标题、### 小标题、- 列表等

        文章结构：
        - 开头：分享一个使用这个工具的真实场景
        - 工具介绍：用自己的话解释这个工具是干什么的
        - 使用体验：详细说说你的使用感受，包括优缺点
        - 实际案例：举1-2个具体的使用例子
        - 获取方式：告诉大家怎么用
        - 互动结尾：问问大家的想法

        字数：800-1200字，语言要自然流畅，像真人写的一样。

        格式要求：
        - 使用标准Markdown格式
        - 主标题用 #
        - 小标题用 ## 或 ###
        - 重点内容用 **粗体** 强调
        - 列表用 - 或数字编号
        - 适当使用emoji增加趣味性

        直接返回Markdown格式的文章内容，不要JSON格式。
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.8,  # 提高创造性，让文章更有人情味
                    max_output_tokens=2000,
                )
            )

            return {
                'title': f"🔥今日AI新发现：{tool_data['name']}",
                'content': response.text,
                'type': 'new_tool',
                'generated_at': datetime.now().isoformat(),
                'tool_name': tool_data['name']  # 保存工具名称用于生成提示词
            }
        except Exception as e:
            print(f"❌ 文章生成失败: {e}")
            return None
    
    def generate_tutorial_article(self, tool_data):
        """生成教程文章"""
        prompt = f"""
        你是一个有耐心的老师，专门教别人用AI工具。请为"{tool_data['name']}"写一篇超详细的使用教程。

        写作风格：
        1. 用"咱们"、"大家"这样亲切的称呼
        2. 每个步骤都要解释为什么这样做
        3. 预判新手可能遇到的问题，提前说明
        4. 用"别担心"、"很简单"、"我刚开始也是这样"等安慰性语言
        5. 加入一些小贴士和避坑指南
        6. 语言要像面对面教学一样耐心细致
        7. 使用标准Markdown格式来组织内容结构

        文章结构：
        - 开头：先安慰新手，说这个工具其实很简单
        - 准备工作：需要什么，怎么注册等
        - 详细步骤：每一步都配上"为什么"
        - 常见问题：新手容易犯的错误
        - 进阶技巧：用熟练后可以试试的高级功能
        - 鼓励结尾：鼓励大家多练习

        标题格式：📖手把手教你用{tool_data['name']}，小白也能5分钟上手！

        字数1000-1500字，要像真的在教朋友一样。

        格式要求：
        - 使用标准Markdown格式
        - 步骤用 ## 第一步、## 第二步
        - 重点用 **粗体** 强调
        - 代码或命令用 `代码` 格式
        - 列表用 - 或数字编号

        直接返回Markdown格式的文章内容。
        """
        
        try:
            response = self.model.generate_content(prompt)

            return {
                'title': f"📖保姆级教程：{tool_data['name']}使用指南",
                'content': response.text,
                'type': 'tutorial',
                'generated_at': datetime.now().isoformat(),
                'tool_name': tool_data['name']  # 保存工具名称用于生成提示词
            }
        except Exception as e:
            print(f"❌ 教程生成失败: {e}")
            return None
    
    def generate_weekly_summary(self):
        """生成周报文章"""
        prompt = """
        你是一个AI圈的资深观察者，每周都会和朋友们分享这一周的见闻。请写一篇AI工具周报。

        写作风格：
        1. 用"这周"、"我发现"、"说实话"等口语化表达
        2. 对一些事件发表个人看法，不要只是客观描述
        3. 可以吐槽一些不好的现象，表达真实想法
        4. 推荐工具时要说明为什么推荐，有什么亮点
        5. 语言要有温度，像和朋友聊天一样
        6. 使用标准Markdown格式来组织内容结构

        内容要求：
        - 开头：这周AI圈又发生了什么有趣的事
        - 行业动态：用自己的话解读，加上个人观点
        - 工具推荐：3-5个工具，每个都要说说为什么值得关注
        - 个人感悟：对AI发展的一些思考
        - 下周展望：期待什么新动向

        标题：这周AI圈又炸了！5个新工具让我眼前一亮

        字数1200-1800字，要有个人色彩和真实感受。

        格式要求：
        - 使用标准Markdown格式
        - 主标题用 #
        - 小标题用 ## 或 ###
        - 重点内容用 **粗体** 强调
        - 列表用 - 或数字编号
        - 适当使用emoji增加趣味性

        直接返回Markdown格式的文章内容。
        """

        try:
            response = self.model.generate_content(prompt)

            return {
                'title': "📊本周AI圈大事件汇总",
                'content': response.text,
                'type': 'weekly_summary',
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ 周报生成失败: {e}")
            return None
    
    def generate_general_article(self, content_type):
        """生成其他类型文章"""
        prompts = {
            'case_study': """
            你是一个喜欢分享真实故事的博主。请写一篇AI工具实际应用的案例分析。

            要求：
            1. 讲一个真实的故事，比如"我朋友小王是做设计的..."
            2. 详细描述遇到的问题和解决过程
            3. 分享使用AI工具前后的对比
            4. 语言要生动，像在讲故事
            5. 标题：真实案例：我朋友用AI工具3天完成1个月的工作
            """,

            'comparison': """
            你是一个爱较真的测评博主。请写一篇对比两个热门AI工具的文章。

            要求：
            1. 用"我亲自测试了..."的口吻
            2. 详细对比使用体验，包括优缺点
            3. 给出明确的推荐建议
            4. 可以吐槽一些不好用的地方
            5. 标题：ChatGPT vs Claude，我用了1个月，终于知道选哪个了
            """,

            'qa_interactive': """
            你是一个热心的AI工具答疑者。请写一篇AI工具问答文章。

            要求：
            1. 收集5-8个常见问题
            2. 用"经常有朋友问我..."的方式开头
            3. 每个回答都要详细实用
            4. 语言要亲切，像在帮朋友解答
            5. 标题：AI工具8大常见问题，我来一次性解答
            """,

            'resource_list': """
            你是一个喜欢分享好东西的博主。请写一篇AI工具资源合集。

            要求：
            1. 推荐8-12个实用工具
            2. 每个工具都要说明推荐理由
            3. 按使用场景分类
            4. 语言要热情，像在推荐宝藏
            5. 标题：私藏已久！12个免费AI工具，每个都是宝藏
            """
        }

        # 文章类型对应的标题和图片类型
        article_configs = {
            'case_study': {
                'title': '💡真实案例：AI工具如何改变工作效率',
                'image_type': 'features',
                'cover_style': 'warm'
            },
            'comparison': {
                'title': '⚡工具对决：深度对比分析',
                'image_type': 'comparison',
                'cover_style': 'tech'
            },
            'qa_interactive': {
                'title': '🤔AI工具常见问题解答',
                'image_type': 'features',
                'cover_style': 'warm'
            },
            'resource_list': {
                'title': '📚AI工具资源大合集',
                'image_type': 'features',
                'cover_style': 'tech'
            }
        }

        base_prompt = prompts.get(content_type, "请写一篇有趣的AI工具相关文章，语言要像朋友聊天一样自然。")
        prompt = base_prompt + """

        格式要求：
        - 使用标准Markdown格式
        - 主标题用 #
        - 小标题用 ## 或 ###
        - 重点内容用 **粗体** 强调
        - 列表用 - 或数字编号
        - 适当使用emoji增加趣味性

        字数1000-1500字，直接返回Markdown格式的文章内容。
        """

        try:
            response = self.model.generate_content(prompt)

            # 获取文章配置
            config = article_configs.get(content_type, {
                'title': f"AI工具分享 - {datetime.now().strftime('%Y-%m-%d')}",
                'image_type': 'features',
                'cover_style': 'tech'
            })

            return {
                'title': config['title'],
                'content': response.text,
                'type': content_type,
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ 文章生成失败: {e}")
            return None
    
    def daily_content_generation(self):
        """每日内容生成"""
        print(f"\n🚀 开始每日内容生成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 确定今日内容类型
        content_type = self.get_today_content_type()
        print(f"📝 今日内容类型：{content_type}")
        
        # 收集数据
        if content_type in ['new_tool', 'tutorial']:
            tools = self.collect_ai_tools()
            if tools:
                tool_data = tools[0]  # 使用第一个工具
                article = self.generate_article(content_type, tool_data)
            else:
                print("⚠️ 未收集到工具数据，生成通用文章")
                article = self.generate_general_article(content_type)
        else:
            article = self.generate_article(content_type)
        
        if article:
            self.preview_article(article)
            self.save_article(article)
            print("✅ 每日内容生成完成！")
        else:
            print("❌ 内容生成失败")
    
    def preview_article(self, article):
        """预览文章"""
        print("\n" + "="*60)
        print("📖 文章预览")
        print("="*60)
        print(f"标题: {article['title']}")
        print(f"类型: {article['type']}")
        print(f"生成时间: {article['generated_at']}")

        if 'tool_name' in article:
            print(f"工具名称: {article['tool_name']}")

        print("-"*60)
        print("正文预览:")
        content = article['content']
        preview = content[:300] + "..." if len(content) > 300 else content
        print(preview)
        print("-"*60)
        print("💡 将自动生成专业的AI绘画提示词用于封面图制作")
        print("="*60)
    
    def save_article(self, article):
        """保存文章到文件"""
        filename = f"article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join('data', filename)

        os.makedirs('data', exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"标题: {article['title']}\n")
            f.write(f"类型: {article['type']}\n")
            f.write(f"生成时间: {article['generated_at']}\n")

            if 'tool_name' in article:
                f.write(f"工具名称: {article['tool_name']}\n")

            f.write("-" * 50 + "\n")
            f.write(article['content'])

        print(f"💾 文章已保存到: {filepath}")

        # 只生成wx.md格式版本
        self._save_wxmd_version(article, filepath)



    def _save_wxmd_version(self, article, txt_filepath):
        """生成wx.md格式版本（标准Markdown）"""
        wxmd_filepath = txt_filepath.replace('.txt', '.md')

        # 生成封面图提示词
        cover_prompt = self._generate_cover_prompt(article)

        # 生成标准的Markdown内容
        markdown_content = f"""# {article['title']}

{article['content']}

---

> 📅 发布时间：{datetime.now().strftime('%Y年%m月%d日')}
> 🏷️ 标签：#AI工具 #效率提升 #科技分享
> 💬 欢迎在评论区分享你的使用体验！

---

## 🎨 专业封面图制作指南

### 📝 AI绘画提示词

**🇨🇳 中文提示词（推荐用于国产AI工具）：**
```
{cover_prompt['chinese']}
```

**🇺🇸 英文提示词（推荐用于Midjourney、DALL-E）：**
```
{cover_prompt['english']}
```

### 🛠️ 推荐AI绘画工具

| 工具名称 | 特点 | 适用场景 | 费用 |
|----------|------|----------|------|
| **Midjourney** | 质量最高，艺术感强 | 专业封面设计 | 付费 |
| **DALL-E 3** | 文字理解好，细节丰富 | 复杂场景描述 | 付费 |
| **Stable Diffusion** | 开源免费，可控性强 | 本地部署，批量生成 | 免费 |
| **文心一格** | 中文理解好，免费额度 | 中文提示词优化 | 免费+付费 |
| **通义万相** | 阿里出品，稳定可靠 | 商业用途 | 免费+付费 |

### 💡 制作技巧

**尺寸建议：**
- 微信公众号封面：900×383px 或 2.35:1 比例
- 推荐尺寸：1200×511px（高清版本）
- 最小尺寸：600×255px
- 方形图：1080×1080px（朋友圈分享）

**设计要点：**
- ✅ 主题突出，一眼就能看懂文章内容
- ✅ 色彩搭配和谐，符合品牌调性
- ✅ 文字清晰可读，不要过于复杂
- ✅ 留白适当，避免元素过于拥挤

**常用色彩搭配：**
- 科技风：蓝色 + 白色 + 橙色点缀
- 教程风：橙色 + 黄色 + 白色
- 商务风：深蓝 + 金色 + 白色
- 活泼风：多彩渐变 + 白色

### 🎯 生成步骤

1. **选择工具**：根据需求选择合适的AI绘画工具
2. **输入提示词**：复制上方提示词，可根据需要微调
3. **调整参数**：设置合适的尺寸和风格参数
4. **生成多版本**：生成3-5个版本，选择最佳效果
5. **后期优化**：如需要可用PS等工具进行微调

---

*💡 提示：好的封面图能显著提升文章点击率，建议多尝试不同风格，找到最适合你的公众号调性的设计方向。*
"""

        with open(wxmd_filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"📝 wx.md格式已保存到: {wxmd_filepath}")
        print(f"🎨 专业AI绘画提示词已包含在文件中")
        print("\n🌐 完整使用流程：")
        print("  1. 📄 内容编辑：打开 https://wx.md")
        print("  2. 📋 复制内容：将Markdown内容粘贴到左侧编辑器")
        print("  3. 🎨 制作封面：使用文件中的AI绘画提示词生成封面图")
        print("     - 推荐工具：Midjourney、DALL-E 3、文心一格")
        print("     - 尺寸：2.35:1 横版比例，推荐1200×511px")
        print("  4. 📱 发布文章：点击'复制'按钮，粘贴到微信编辑器")
        print("  5. 🖼️ 添加封面：上传生成的封面图")
        print("\n💡 提示：AI绘画提示词经过专业优化，可直接使用或根据需要微调")

    def _generate_cover_prompt(self, article):
        """生成高质量的AI绘画提示词"""
        title = article['title']
        content_type = article['type']
        tool_name = article.get('tool_name', 'AI工具')

        # 根据内容类型生成专业的提示词
        type_prompts = {
            'new_tool': {
                'scene': '科技产品发布会现场',
                'style': '现代科技风格',
                'colors': '蓝色和白色为主色调，点缀橙色',
                'elements': 'AI芯片、电路板纹理、全息投影效果',
                'mood': '创新、前沿、专业'
            },
            'tutorial': {
                'scene': '现代化学习空间或工作室',
                'style': '友好教学风格',
                'colors': '温暖的橙色和黄色，配以白色',
                'elements': '书籍、笔记本电脑、学习图标、箭头指示',
                'mood': '友好、易懂、循序渐进'
            },
            'comparison': {
                'scene': '专业评测实验室',
                'style': '对比分析风格',
                'colors': '蓝色vs红色对比色，或紫色渐变',
                'elements': 'VS标志、天平、对比图表、评分星级',
                'mood': '客观、专业、权威'
            },
            'weekly_summary': {
                'scene': '数据分析中心或新闻编辑室',
                'style': '商务报告风格',
                'colors': '深蓝色背景，金色和白色文字',
                'elements': '数据图表、时间轴、新闻图标、统计元素',
                'mood': '权威、总结性、信息丰富'
            },
            'case_study': {
                'scene': '成功企业办公环境',
                'style': '商业案例风格',
                'colors': '绿色和蓝色，象征成长和信任',
                'elements': '上升箭头、成功图标、商业图表、握手',
                'mood': '成功、可信、鼓舞人心'
            },
            'qa_interactive': {
                'scene': '友好的咨询或客服环境',
                'style': '互动问答风格',
                'colors': '温暖的橙色和蓝色',
                'elements': '问号、对话气泡、帮助图标、FAQ',
                'mood': '友好、互动、解决问题'
            },
            'resource_list': {
                'scene': '数字图书馆或工具展示厅',
                'style': '资源合集风格',
                'colors': '金色和深蓝色，突出珍贵感',
                'elements': '宝箱、收藏夹、工具图标、星星装饰',
                'mood': '珍贵、丰富、实用'
            }
        }

        prompt_config = type_prompts.get(content_type, type_prompts['new_tool'])

        # 从标题中提取关键词，去除emoji
        title_clean = title.replace('🔥', '').replace('📖', '').replace('💡', '').replace('⚡', '').replace('📊', '').replace('🤔', '').replace('📚', '').strip()

        # 生成详细的中文提示词
        chinese_prompt = f"""
主题：{title_clean}
场景：{prompt_config['scene']}
风格：{prompt_config['style']}，现代扁平化设计
色彩：{prompt_config['colors']}
元素：{prompt_config['elements']}，{tool_name}相关图标
情绪：{prompt_config['mood']}
构图：2.35:1横版比例，居中对称构图，留白平衡
质量：高分辨率，专业设计，适合微信公众号封面
文字：可包含"{tool_name}"英文标识，字体现代简洁
光效：柔和渐变，微妙阴影，增强层次感
        """.strip()

        # 生成专业的英文提示词
        english_prompt = f"""
Theme: {title_clean}
Scene: {prompt_config['scene']}
Style: {prompt_config['style']}, modern flat design
Colors: {prompt_config['colors']}
Elements: {prompt_config['elements']}, {tool_name} related icons
Mood: {prompt_config['mood']}
Composition: 2.35:1 landscape ratio, centered symmetrical layout, balanced whitespace
Quality: high resolution, professional design, suitable for WeChat article cover
Typography: may include "{tool_name}" text, modern clean font
Lighting: soft gradients, subtle shadows, enhanced depth
Additional: minimalist, clean, professional, eye-catching, social media ready
        """.strip()

        return {
            'chinese': chinese_prompt,
            'english': english_prompt,
            'tool_name': tool_name,
            'style_guide': prompt_config
        }

    
    def setup_schedule(self):
        """设置定时任务"""
        schedule.every().day.at("08:00").do(self.daily_content_generation)
        print("⏰ 定时任务设置完成：每天08:00自动生成内容")
    
    def run(self):
        """运行主程序"""
        print("🎯 AI内容生成器开始运行...")
        
        # 设置定时任务
        self.setup_schedule()
        
        # 立即执行一次（测试）
        print("🧪 立即执行一次内容生成（测试模式）")
        self.daily_content_generation()
        
        # 开始定时任务循环
        print("\n⏰ 等待定时任务执行...")
        print("💡 提示：按 Ctrl+C 可以停止程序")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            print("\n👋 程序已停止")

def main():
    """主函数"""
    try:
        writer = AIContentWriter()
        writer.run()
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("请检查 .env 文件中的 GEMINI_API_KEY 设置")
    except Exception as e:
        print(f"❌ 程序运行错误: {e}")

if __name__ == "__main__":
    main()
