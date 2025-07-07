#!/usr/bin/env python3
"""
图片和媒体生成模块
为公众号文章生成封面图、配图等
"""

import os
import requests
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime
import random

class MediaGenerator:
    """媒体内容生成器"""
    
    def __init__(self):
        self.output_dir = "media"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 设置中文字体
        self.setup_fonts()
        
        # 公众号常用尺寸
        self.cover_size = (900, 500)  # 封面图尺寸
        self.content_size = (800, 600)  # 内容配图尺寸
        
        print("🎨 媒体生成器初始化成功！")
    
    def setup_fonts(self):
        """设置字体"""
        try:
            # 尝试使用系统中文字体
            font_paths = [
                '/System/Library/Fonts/PingFang.ttc',  # macOS
                '/System/Library/Fonts/Helvetica.ttc',  # macOS备用
                'C:/Windows/Fonts/msyh.ttc',  # Windows
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'  # Linux
            ]
            
            self.title_font = None
            self.content_font = None
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        self.title_font = ImageFont.truetype(font_path, 48)
                        self.content_font = ImageFont.truetype(font_path, 24)
                        break
                    except:
                        continue
            
            # 如果没有找到字体，使用默认字体
            if not self.title_font:
                self.title_font = ImageFont.load_default()
                self.content_font = ImageFont.load_default()
                
        except Exception as e:
            print(f"字体设置警告: {e}")
            self.title_font = ImageFont.load_default()
            self.content_font = ImageFont.load_default()
    
    def generate_cover_image(self, title, tool_name="", style="tech"):
        """生成封面图"""
        # 创建画布
        img = Image.new('RGB', self.cover_size, color='white')
        draw = ImageDraw.Draw(img)
        
        # 背景渐变色
        if style == "tech":
            colors = [(64, 123, 255), (112, 161, 255)]  # 科技蓝
        elif style == "warm":
            colors = [(255, 154, 0), (255, 206, 84)]   # 温暖橙
        else:
            colors = [(138, 43, 226), (186, 85, 211)]  # 紫色
        
        # 绘制渐变背景
        self._draw_gradient(draw, self.cover_size, colors)
        
        # 添加装饰元素
        self._add_decorative_elements(draw, self.cover_size)
        
        # 添加标题
        self._add_title_text(draw, title, self.cover_size)
        
        # 添加工具名称标签
        if tool_name:
            self._add_tool_label(draw, tool_name, self.cover_size)
        
        # 添加日期
        date_str = datetime.now().strftime("%Y.%m.%d")
        self._add_date(draw, date_str, self.cover_size)
        
        # 保存图片
        filename = f"cover_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath, 'PNG', quality=95)
        
        print(f"🖼️ 封面图已生成: {filepath}")
        return filepath
    
    def generate_content_image(self, content_type, data=None):
        """生成内容配图"""
        if content_type == "comparison":
            return self._generate_comparison_chart(data)
        elif content_type == "tutorial":
            return self._generate_step_diagram(data)
        elif content_type == "stats":
            return self._generate_stats_chart(data)
        else:
            return self._generate_feature_showcase(data)
    
    def _draw_gradient(self, draw, size, colors):
        """绘制渐变背景"""
        width, height = size
        start_color = colors[0]
        end_color = colors[1]
        
        for y in range(height):
            # 计算当前行的颜色
            ratio = y / height
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    def _add_decorative_elements(self, draw, size):
        """添加装饰元素"""
        width, height = size
        
        # 添加一些圆形装饰
        for _ in range(5):
            x = random.randint(0, width)
            y = random.randint(0, height)
            radius = random.randint(20, 80)
            alpha = random.randint(10, 30)
            
            # 创建半透明圆形
            circle_img = Image.new('RGBA', (radius*2, radius*2), (255, 255, 255, alpha))
            circle_draw = ImageDraw.Draw(circle_img)
            circle_draw.ellipse([0, 0, radius*2, radius*2], fill=(255, 255, 255, alpha))
    
    def _add_title_text(self, draw, title, size):
        """添加标题文字"""
        width, height = size
        
        # 处理长标题，自动换行
        max_width = width - 100
        lines = self._wrap_text(title, self.title_font, max_width)
        
        # 计算总高度
        line_height = 60
        total_height = len(lines) * line_height
        start_y = (height - total_height) // 2
        
        # 绘制每一行
        for i, line in enumerate(lines):
            # 计算文字位置（居中）
            bbox = draw.textbbox((0, 0), line, font=self.title_font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = start_y + i * line_height
            
            # 添加文字阴影
            draw.text((x+2, y+2), line, font=self.title_font, fill=(0, 0, 0, 128))
            # 添加主文字
            draw.text((x, y), line, font=self.title_font, fill='white')
    
    def _add_tool_label(self, draw, tool_name, size):
        """添加工具名称标签"""
        width, height = size
        
        # 创建标签背景
        label_width = 200
        label_height = 40
        x = width - label_width - 20
        y = 20
        
        # 绘制圆角矩形背景
        draw.rounded_rectangle([x, y, x + label_width, y + label_height], 
                             radius=20, fill=(255, 255, 255, 200))
        
        # 添加工具名称
        bbox = draw.textbbox((0, 0), tool_name, font=self.content_font)
        text_width = bbox[2] - bbox[0]
        text_x = x + (label_width - text_width) // 2
        text_y = y + 8
        
        draw.text((text_x, text_y), tool_name, font=self.content_font, fill='black')
    
    def _add_date(self, draw, date_str, size):
        """添加日期"""
        width, height = size
        
        # 在右下角添加日期
        bbox = draw.textbbox((0, 0), date_str, font=self.content_font)
        text_width = bbox[2] - bbox[0]
        x = width - text_width - 20
        y = height - 40
        
        draw.text((x, y), date_str, font=self.content_font, fill='white')
    
    def _wrap_text(self, text, font, max_width):
        """文字自动换行"""
        lines = []
        words = text.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _generate_comparison_chart(self, data):
        """生成对比图表"""
        # 使用matplotlib生成对比图
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 示例数据
        tools = ['工具A', '工具B']
        features = ['易用性', '功能性', '价格', '支持']
        scores_a = [8, 9, 6, 7]
        scores_b = [7, 8, 9, 8]
        
        x = range(len(features))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], scores_a, width, label=tools[0], color='#4A90E2')
        ax.bar([i + width/2 for i in x], scores_b, width, label=tools[1], color='#F5A623')
        
        ax.set_xlabel('评估维度')
        ax.set_ylabel('评分')
        ax.set_title('AI工具对比分析')
        ax.set_xticks(x)
        ax.set_xticklabels(features)
        ax.legend()
        ax.set_ylim(0, 10)
        
        # 保存图片
        filename = f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 对比图表已生成: {filepath}")
        return filepath
    
    def _generate_step_diagram(self, data):
        """生成步骤图"""
        # 创建步骤流程图
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        steps = ["注册账号", "安装工具", "配置设置", "开始使用"]
        step_height = 100
        step_width = 600
        start_y = 50
        
        for i, step in enumerate(steps):
            y = start_y + i * (step_height + 20)
            
            # 绘制步骤框
            draw.rounded_rectangle([100, y, 100 + step_width, y + step_height], 
                                 radius=10, fill='#E3F2FD', outline='#2196F3', width=2)
            
            # 添加步骤编号
            circle_x = 50
            circle_y = y + step_height // 2 - 20
            draw.ellipse([circle_x, circle_y, circle_x + 40, circle_y + 40], 
                        fill='#2196F3')
            draw.text((circle_x + 15, circle_y + 10), str(i + 1), 
                     font=self.content_font, fill='white')
            
            # 添加步骤文字
            text_x = 120
            text_y = y + step_height // 2 - 10
            draw.text((text_x, text_y), step, font=self.title_font, fill='black')
            
            # 添加箭头（除了最后一步）
            if i < len(steps) - 1:
                arrow_y = y + step_height + 10
                draw.polygon([(400, arrow_y), (390, arrow_y - 10), (410, arrow_y - 10)], 
                           fill='#666666')
        
        # 保存图片
        filename = f"steps_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath, 'PNG', quality=95)
        
        print(f"📋 步骤图已生成: {filepath}")
        return filepath
    
    def _generate_stats_chart(self, data):
        """生成统计图表"""
        # 使用matplotlib生成统计图
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

        # 左侧：工具类型分布饼图
        categories = ['对话AI', '图像生成', '文档处理', '代码助手', '其他']
        sizes = [35, 25, 20, 15, 5]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']

        ax1.pie(sizes, labels=categories, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('本周热门AI工具类型分布', fontsize=14, fontweight='bold')

        # 右侧：工具热度排行柱状图
        tools = ['ChatGPT', 'Midjourney', 'Claude', 'Notion AI', 'GitHub Copilot']
        popularity = [95, 88, 82, 76, 71]

        bars = ax2.bar(tools, popularity, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
        ax2.set_title('本周AI工具热度排行', fontsize=14, fontweight='bold')
        ax2.set_ylabel('热度指数')
        ax2.set_ylim(0, 100)

        # 在柱状图上添加数值
        for bar, value in zip(bars, popularity):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{value}', ha='center', va='bottom')

        # 旋转x轴标签
        ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()

        # 保存图片
        filename = f"stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"📈 统计图表已生成: {filepath}")
        return filepath

    def _generate_feature_showcase(self, data):
        """生成功能展示图"""
        img = Image.new('RGB', (800, 600), color='#F8F9FA')
        draw = ImageDraw.Draw(img)

        # 标题
        title = "核心功能一览"
        bbox = draw.textbbox((0, 0), title, font=self.title_font)
        title_width = bbox[2] - bbox[0]
        draw.text(((800 - title_width) // 2, 30), title, font=self.title_font, fill='black')

        # 功能列表
        features = [
            "🤖 智能对话", "📝 文档处理", "🎨 创意生成",
            "📊 数据分析", "🔍 信息搜索", "⚡ 快速响应"
        ]

        # 3x2网格布局
        cols = 3
        rows = 2
        cell_width = 200
        cell_height = 150
        start_x = (800 - cols * cell_width) // 2
        start_y = 120

        for i, feature in enumerate(features):
            row = i // cols
            col = i % cols

            x = start_x + col * cell_width + 10
            y = start_y + row * cell_height + 10

            # 绘制功能卡片
            draw.rounded_rectangle([x, y, x + cell_width - 20, y + cell_height - 20],
                                 radius=15, fill='white', outline='#E0E0E0', width=1)

            # 添加功能文字
            text_lines = feature.split(' ')
            for j, line in enumerate(text_lines):
                text_y = y + 40 + j * 30
                bbox = draw.textbbox((0, 0), line, font=self.content_font)
                text_width = bbox[2] - bbox[0]
                text_x = x + (cell_width - 20 - text_width) // 2
                draw.text((text_x, text_y), line, font=self.content_font, fill='black')

        # 保存图片
        filename = f"features_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath, 'PNG', quality=95)

        print(f"✨ 功能展示图已生成: {filepath}")
        return filepath

def test_media_generator():
    """测试媒体生成功能"""
    generator = MediaGenerator()

    print("🧪 开始测试媒体生成功能...")

    # 生成封面图
    print("1. 生成封面图...")
    cover = generator.generate_cover_image(
        "🔥Notion AI太牛了！我用了一周，效率翻了3倍",
        "Notion AI",
        "tech"
    )

    # 生成对比图
    print("2. 生成对比图...")
    comparison = generator.generate_content_image("comparison")

    # 生成步骤图
    print("3. 生成步骤图...")
    steps = generator.generate_content_image("tutorial")

    # 生成功能图
    print("4. 生成功能展示图...")
    features = generator.generate_content_image("features")

    # 生成统计图
    print("5. 生成统计图表...")
    stats = generator.generate_content_image("stats")

    print("🎉 所有图片生成完成！")
    print(f"生成的文件:")
    print(f"  - 封面图: {cover}")
    print(f"  - 对比图: {comparison}")
    print(f"  - 步骤图: {steps}")
    print(f"  - 功能图: {features}")
    print(f"  - 统计图: {stats}")

    return [cover, comparison, steps, features, stats]

if __name__ == "__main__":
    test_media_generator()
