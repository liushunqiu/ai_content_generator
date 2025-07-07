#!/usr/bin/env python3
"""
AI工具公众号自动化内容生成器 - GitHub Actions版
使用Google Gemini AI自动生成高质量的公众号文章
移除了本地代理配置，适用于GitHub Actions环境
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

# 加载环境变量
load_dotenv()

class AIContentWriter:
    """AI内容生成器 - GitHub Actions版"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key or self.api_key == 'your-gemini-api-key-here':
            raise ValueError("请在 GitHub Secrets 中设置正确的 GEMINI_API_KEY")

        # 初始化Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        # 企业微信配置
        self.wechat_webhook_url = os.getenv('WECHAT_WEBHOOK_URL')

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

        # 数据源配置
        self.data_sources = {
            'producthunt': {
                'url': 'https://www.producthunt.com/feed',
                'weight': 0.4,
                'description': 'Product Hunt新产品发现'
            },
            'github_trending': {
                'url': 'https://github.com/trending',
                'weight': 0.3,
                'description': 'GitHub热门项目'
            },
            'ai_news': {
                'url': 'https://feeds.feedburner.com/oreilly/radar',
                'weight': 0.3,
                'description': 'AI技术新闻'
            }
        }

        # 确保输出目录存在
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 确保日志目录存在
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)

    def log_message(self, message, level="INFO"):
        """记录日志消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        
        # 写入日志文件
        log_file = os.path.join(self.log_dir, f"content_generation_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def send_wechat_notification(self, title, content, success=True):
        """发送企业微信通知"""
        if not self.wechat_webhook_url:
            self.log_message("未配置企业微信Webhook URL，跳过通知", "WARNING")
            return

        emoji = "✅" if success else "❌"
        message = f"{emoji} {title}\n\n{content}"

        try:
            response = requests.post(
                self.wechat_webhook_url,
                json={
                    'msgtype': 'text',
                    'text': {'content': message}
                },
                timeout=10
            )

            if response.status_code == 200:
                self.log_message("企业微信通知发送成功")
            else:
                self.log_message(f"企业微信通知发送失败: {response.status_code}", "ERROR")

        except Exception as e:
            self.log_message(f"发送企业微信通知时出错: {str(e)}", "ERROR")

    def upload_file_to_wechat(self, file_path):
        """上传文件到企业微信获取media_id"""
        if not self.wechat_webhook_url:
            self.log_message("未配置企业微信Webhook URL，无法上传文件", "ERROR")
            return None

        # 从webhook URL中提取key
        try:
            key = self.wechat_webhook_url.split('key=')[1]
            upload_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={key}&type=file"

            with open(file_path, 'rb') as f:
                files = {
                    'media': (os.path.basename(file_path), f, 'application/octet-stream')
                }

                response = requests.post(upload_url, files=files, timeout=30)

                if response.status_code == 200:
                    result = response.json()
                    if result.get('errcode') == 0:
                        media_id = result.get('media_id')
                        self.log_message(f"文件上传成功，media_id: {media_id}")
                        return media_id
                    else:
                        self.log_message(f"文件上传失败: {result.get('errmsg')}", "ERROR")
                        return None
                else:
                    self.log_message(f"文件上传请求失败: {response.status_code}", "ERROR")
                    return None

        except Exception as e:
            self.log_message(f"上传文件时出错: {str(e)}", "ERROR")
            return None

    def send_file_to_wechat(self, file_path, title="AI生成内容"):
        """发送文件到企业微信群"""
        if not os.path.exists(file_path):
            self.log_message(f"文件不存在: {file_path}", "ERROR")
            return False

        # 1. 上传文件获取media_id
        media_id = self.upload_file_to_wechat(file_path)
        if not media_id:
            return False

        # 2. 发送文件消息
        try:
            response = requests.post(
                self.wechat_webhook_url,
                json={
                    'msgtype': 'file',
                    'file': {'media_id': media_id}
                },
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    self.log_message(f"文件发送成功: {os.path.basename(file_path)}")
                    return True
                else:
                    self.log_message(f"文件发送失败: {result.get('errmsg')}", "ERROR")
                    return False
            else:
                self.log_message(f"文件发送请求失败: {response.status_code}", "ERROR")
                return False

        except Exception as e:
            self.log_message(f"发送文件时出错: {str(e)}", "ERROR")
            return False

    def fetch_data_sources(self):
        """获取各种数据源的最新信息"""
        all_data = []
        
        for source_name, source_config in self.data_sources.items():
            try:
                self.log_message(f"正在获取 {source_config['description']} 数据...")
                
                if source_name == 'producthunt':
                    data = self._fetch_producthunt_data()
                elif source_name == 'github_trending':
                    data = self._fetch_github_trending()
                elif source_name == 'ai_news':
                    data = self._fetch_ai_news()
                else:
                    continue
                
                if data:
                    all_data.extend(data)
                    self.log_message(f"成功获取 {len(data)} 条 {source_config['description']} 数据")
                else:
                    self.log_message(f"未获取到 {source_config['description']} 数据", "WARNING")
                    
            except Exception as e:
                self.log_message(f"获取 {source_config['description']} 数据时出错: {str(e)}", "ERROR")
        
        return all_data

    def _fetch_producthunt_data(self):
        """获取Product Hunt数据"""
        try:
            feed = feedparser.parse('https://www.producthunt.com/feed')
            data = []
            
            for entry in feed.entries[:10]:  # 获取最新10条
                data.append({
                    'title': entry.title,
                    'description': entry.summary,
                    'link': entry.link,
                    'published': entry.published,
                    'source': 'Product Hunt'
                })
            
            return data
        except Exception as e:
            self.log_message(f"获取Product Hunt数据失败: {str(e)}", "ERROR")
            return []

    def _fetch_github_trending(self):
        """获取GitHub热门项目（模拟数据）"""
        # 由于GitHub没有直接的RSS feed，这里使用模拟数据
        # 在实际部署中，可以使用GitHub API
        return [
            {
                'title': 'AI代码助手项目',
                'description': '基于大语言模型的智能代码生成工具',
                'link': 'https://github.com/example/ai-code-assistant',
                'published': datetime.now().isoformat(),
                'source': 'GitHub Trending'
            }
        ]

    def _fetch_ai_news(self):
        """获取AI新闻"""
        try:
            feed = feedparser.parse('https://feeds.feedburner.com/oreilly/radar')
            data = []
            
            for entry in feed.entries[:5]:  # 获取最新5条
                data.append({
                    'title': entry.title,
                    'description': entry.summary,
                    'link': entry.link,
                    'published': entry.published,
                    'source': 'AI News'
                })
            
            return data
        except Exception as e:
            self.log_message(f"获取AI新闻失败: {str(e)}", "ERROR")
            return []

    def generate_content(self, content_type, data_sources):
        """使用Gemini生成内容"""
        try:
            # 构建提示词
            prompt = self._build_prompt(content_type, data_sources)
            
            self.log_message("正在使用Gemini生成内容...")
            
            # 调用Gemini API
            response = self.model.generate_content(prompt)
            
            if response.text:
                self.log_message("内容生成成功")
                return response.text
            else:
                self.log_message("Gemini返回空内容", "ERROR")
                return None
                
        except Exception as e:
            self.log_message(f"内容生成失败: {str(e)}", "ERROR")
            return None

    def _build_prompt(self, content_type, data_sources):
        """构建Gemini提示词"""
        # 数据源摘要
        data_summary = "\n".join([
            f"- {item['title']}: {item['description'][:100]}..." 
            for item in data_sources[:5]
        ])
        
        content_type_prompts = {
            "new_tool": f"""
基于以下最新的AI工具信息，写一篇微信公众号文章，介绍最有潜力的新AI工具：

{data_summary}

要求：
1. 标题吸引人，包含"AI工具"关键词
2. 文章结构：开头引入 + 工具介绍 + 使用场景 + 总结推荐
3. 语言风格轻松易懂，适合普通用户
4. 字数控制在800-1200字
5. 使用wxmd格式，适配微信公众号编辑器
6. 作者署名：刘工的AI工具箱
7. 提供一个2.35:1比例的封面图生成提示词

请直接输出完整的文章内容。
""",
            "tutorial": f"""
基于以下AI工具信息，写一篇详细的使用教程：

{data_summary}

要求：
1. 选择其中最实用的工具写教程
2. 包含：工具介绍、注册步骤、基础使用、进阶技巧、注意事项
3. 步骤清晰，配有详细说明
4. 字数控制在1000-1500字
5. 使用wxmd格式
6. 作者署名：刘工的AI工具箱
7. 提供封面图生成提示词（2.35:1比例）

请直接输出完整的教程文章。
"""
        }
        
        return content_type_prompts.get(content_type, content_type_prompts["new_tool"])

    def save_content(self, content, content_type):
        """保存生成的内容"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{content_type}_{timestamp}.md"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log_message(f"内容已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            self.log_message(f"保存内容失败: {str(e)}", "ERROR")
            return None

    def run_daily_generation(self):
        """执行每日内容生成任务"""
        try:
            self.log_message("开始每日内容生成任务")
            
            # 确定今天的内容类型
            today = datetime.now().weekday()
            content_type = self.content_schedule[today]
            
            self.log_message(f"今日内容类型: {content_type}")
            
            # 获取数据源
            data_sources = self.fetch_data_sources()
            
            if not data_sources:
                self.log_message("未获取到任何数据源，使用默认内容", "WARNING")
                data_sources = [
                    {
                        'title': '默认AI工具推荐',
                        'description': '今日推荐一些实用的AI工具',
                        'source': '默认'
                    }
                ]
            
            # 生成内容
            content = self.generate_content(content_type, data_sources)
            
            if content:
                # 保存内容
                filepath = self.save_content(content, content_type)

                if filepath:
                    # 先发送文本通知
                    self.send_wechat_notification(
                        "AI内容生成成功",
                        f"今日{content_type}类型文章已生成完成\n文件: {os.path.basename(filepath)}\n\n{content[:200]}...",
                        success=True
                    )

                    # 然后发送文件
                    file_sent = self.send_file_to_wechat(filepath, f"AI生成文章-{content_type}")

                    if file_sent:
                        self.log_message("每日内容生成任务完成，文件已发送到企业微信")
                    else:
                        self.log_message("内容生成完成，但文件发送失败", "WARNING")
                else:
                    raise Exception("内容保存失败")
            else:
                raise Exception("内容生成失败")
                
        except Exception as e:
            error_msg = f"每日内容生成任务失败: {str(e)}"
            self.log_message(error_msg, "ERROR")
            
            # 发送失败通知
            self.send_wechat_notification(
                "AI内容生成失败",
                error_msg,
                success=False
            )

def main():
    """主函数 - GitHub Actions入口"""
    try:
        writer = AIContentWriter()
        writer.log_message("AI内容生成器启动 (GitHub Actions版)")
        
        # 直接运行一次生成任务
        writer.run_daily_generation()
        
        writer.log_message("AI内容生成器任务完成")
        
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
