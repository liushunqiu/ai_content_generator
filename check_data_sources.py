#!/usr/bin/env python3
"""
数据源状态检查工具
检查RSS源的可用性和内容新鲜度
"""

import feedparser
import requests
from datetime import datetime, timedelta
import json

def check_rss_source(url, name):
    """检查单个RSS源的状态"""
    print(f"\n📡 检查 {name}")
    print(f"🔗 URL: {url}")
    
    try:
        # 设置超时和用户代理
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 先检查HTTP状态
        response = requests.get(url, headers=headers, timeout=10)
        print(f"📊 HTTP状态: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
        
        # 解析RSS
        feed = feedparser.parse(url)
        
        if not hasattr(feed, 'entries') or len(feed.entries) == 0:
            print("❌ 无法获取RSS内容或内容为空")
            return False
        
        print(f"✅ 成功获取 {len(feed.entries)} 篇文章")
        
        # 检查最新文章时间
        if hasattr(feed.entries[0], 'published_parsed'):
            pub_time = datetime(*feed.entries[0].published_parsed[:6])
            days_ago = (datetime.now() - pub_time).days
            print(f"📅 最新文章: {feed.entries[0].title[:50]}...")
            print(f"🕒 发布时间: {days_ago} 天前")
            
            if days_ago > 7:
                print("⚠️ 内容可能不够新鲜")
        
        # 检查AI相关内容
        ai_keywords = [
            'ai', 'artificial intelligence', 'chatgpt', 'gpt', 'claude',
            'midjourney', 'dall-e', 'machine learning', 'ai tool'
        ]
        
        ai_count = 0
        for entry in feed.entries[:10]:
            content = f"{entry.title} {getattr(entry, 'summary', '')}".lower()
            if any(keyword in content for keyword in ai_keywords):
                ai_count += 1
        
        print(f"🤖 AI相关内容: {ai_count}/10 篇")
        
        if ai_count < 3:
            print("⚠️ AI相关内容较少")
        
        return True
        
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def check_all_sources():
    """检查所有数据源"""
    print("🔍 AI工具资讯数据源状态检查")
    print("=" * 50)
    
    # 当前使用的RSS源
    sources = [
        ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
        ("The Verge AI", "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
        ("VentureBeat AI", "https://venturebeat.com/ai/feed/"),
        ("Machine Learning Mastery", "https://machinelearningmastery.com/feed/"),
    ]
    
    # 备选RSS源
    alternative_sources = [
        ("AI News", "https://artificialintelligence-news.com/feed/"),
        ("MIT Technology Review AI", "https://www.technologyreview.com/topic/artificial-intelligence/feed/"),
        ("Towards Data Science", "https://towardsdatascience.com/feed"),
        ("AI Research", "https://www.airesearch.com/feed/"),
    ]
    
    working_sources = []
    
    print("\n📊 当前数据源检查:")
    for name, url in sources:
        if check_rss_source(url, name):
            working_sources.append((name, url))
    
    print(f"\n✅ 可用数据源: {len(working_sources)}/{len(sources)}")
    
    if len(working_sources) < 2:
        print("\n🔄 检查备选数据源:")
        for name, url in alternative_sources:
            if check_rss_source(url, name):
                working_sources.append((name, url))
                if len(working_sources) >= 3:
                    break
    
    print("\n" + "=" * 50)
    print("📋 推荐使用的数据源:")
    for i, (name, url) in enumerate(working_sources[:3], 1):
        print(f"{i}. {name}")
        print(f"   {url}")
    
    if len(working_sources) == 0:
        print("\n⚠️ 所有RSS源都无法访问")
        print("💡 建议:")
        print("1. 检查网络连接和代理设置")
        print("2. 使用精选工具库模式")
        print("3. 考虑手动更新工具信息")
    
    return working_sources

def suggest_improvements():
    """提供改进建议"""
    print("\n💡 资讯来源改进建议:")
    print("-" * 30)
    
    suggestions = [
        "1. 📚 使用精选工具库 (推荐)",
        "   - 手动筛选高质量AI工具",
        "   - 定期更新(建议每月一次)",
        "   - 确保信息准确性",
        "",
        "2. 🔄 多源结合策略",
        "   - RSS源 + 精选库 + 手动更新",
        "   - 降低对单一数据源的依赖",
        "   - 提高内容多样性",
        "",
        "3. 📱 社交媒体监控",
        "   - 关注AI工具相关Twitter账号",
        "   - 监控Product Hunt新产品",
        "   - 关注GitHub Trending",
        "",
        "4. 🤖 AI辅助内容生成",
        "   - 让AI根据当前热点生成内容",
        "   - 结合时事和趋势",
        "   - 保持内容新鲜度"
    ]
    
    for suggestion in suggestions:
        print(suggestion)

if __name__ == "__main__":
    working_sources = check_all_sources()
    suggest_improvements()
    
    print(f"\n📊 检查完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
