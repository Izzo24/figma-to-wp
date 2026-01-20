#!/usr/bin/env python3
"""
Figma to WordPress 分檔工具 v4
- HTML 格式化換行
- SEO 語意標籤優化
- 按鈕 → <a href="#" class="btn">
- 標題依使用者指定 H1/H2/H3
- 移除不需要的 CSS 屬性
- 純英文 class 命名
- 合併相同 CSS
"""

import re
import os
import argparse
import json
from html.parser import HTMLParser
from collections import OrderedDict


# 要移除的 CSS 屬性
REMOVE_PROPS = [
    'font-size', 'line-height', 'font-family', 'font-weight',
    'left', 'top', 'position', 'width', 'height'
]

# Figma 命名 → 語意化命名對照
NAME_MAP = {
    'frame': 'wrap',
    'rectangle': 'box',
    'ellipse': 'circle',
    'line': 'divider',
    'group': 'group',
    'vector': 'icon',
    'text': 'text',
    'button': 'btn',
    'image': 'img',
    'svg': 'svg'
}


class FigmaAnalyzer(HTMLParser):
    """第一階段：分析 Figma 代碼，提取可能的標題"""
    
    def __init__(self):
        super().__init__()
        self.potential_titles = []
        self.current_text = ''
        self.in_button = False
        self.button_texts = []
    
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        data_layer = attrs_dict.get('data-layer', '').lower()
        class_name = attrs_dict.get('class', '').lower()
        
        # 檢測是否在按鈕內
        if 'button' in data_layer or 'btn' in data_layer or 'button' in class_name:
            self.in_button = True
    
    def handle_endtag(self, tag):
        pass
    
    def handle_data(self, data):
        text = data.strip()
        if text and len(text) > 1:
            if self.in_button:
                self.button_texts.append(text)
                self.in_button = False
            else:
                # 可能是標題的條件：不太長、不是純數字
                if len(text) < 50 and not text.isdigit():
                    self.potential_titles.append(text)
    
    def get_titles(self):
        # 過濾掉按鈕文字
        return [t for t in self.potential_titles if t not in self.button_texts]
    
    def get_buttons(self):
        return self.button_texts


class StyleExtractor(HTMLParser):
    """第二階段：提取 inline style 並轉換為 CSS class"""
    
    def __init__(self, section_name, headings=None):
        super().__init__()
        self.section = section_name
        self.headings = headings or {}  # {'文字': 'h2', ...}
        self.css_rules = OrderedDict()
        self.html_lines = []
        self.indent_level = 0
        self.used_names = set()
        self.element_counter = {}
        self.pending_text = None
        self.is_button = False
        self.button_class = None
    
    def _get_indent(self):
        return '    ' * self.indent_level
    
    def _semantic_name(self, raw_name, tag='div'):
        """將 Figma 命名轉為純英文語意化名稱"""
        english_only = re.sub(r'[^a-zA-Z]', '', raw_name)
        clean = english_only.lower()
        
        for figma_key, semantic in NAME_MAP.items():
            if figma_key in clean:
                clean = semantic
                break
        
        if not clean or len(clean) < 2:
            if tag == 'a':
                clean = 'link'
            elif tag == 'button':
                clean = 'btn'
            elif tag == 'img':
                clean = 'img'
            elif tag == 'svg':
                clean = 'icon'
            elif tag == 'ul' or tag == 'ol':
                clean = 'list'
            elif tag == 'li':
                clean = 'item'
            elif tag == 'p':
                clean = 'text'
            elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                clean = 'title'
            elif tag == 'span':
                clean = 'label'
            else:
                clean = 'block'
        
        clean = re.sub(r'([a-z])([A-Z])', r'\1-\2', clean).lower()
        
        if clean not in self.element_counter:
            self.element_counter[clean] = 0
        self.element_counter[clean] += 1
        
        if self.element_counter[clean] > 1:
            clean = f"{clean}-{self.element_counter[clean]}"
        
        return clean
    
    def _filter_style(self, style):
        """過濾掉不要的 CSS 屬性"""
        props = [p.strip() for p in style.split(';') if p.strip()]
        filtered = []
        
        for prop in props:
            prop_name = prop.split(':')[0].strip().lower()
            if prop_name not in REMOVE_PROPS:
                filtered.append(prop)
        
        return filtered
    
    def _is_button(self, attrs_dict):
        """判斷是否為按鈕"""
        data_layer = attrs_dict.get('data-layer', '').lower()
        class_name = attrs_dict.get('class', '').lower()
        return 'button' in data_layer or 'btn' in data_layer or 'button' in class_name
    
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        style = attrs_dict.pop('style', None)
        data_layer = attrs_dict.pop('data-layer', '')
        attrs_dict.pop('data-svg-wrapper', None)
        existing_class = attrs_dict.get('class', '')
        
        # 檢測按鈕
        if self._is_button(dict(attrs)):
            self.is_button = True
            class_name = self._semantic_name('button', 'a')
            self.button_class = f"{self.section}__{class_name}"
            
            # 儲存按鈕的 CSS
            if style:
                filtered_props = self._filter_style(style)
                if filtered_props:
                    self.css_rules[self.button_class] = filtered_props
            return  # 不輸出按鈕容器的 div
        
        # 如果在按鈕內，跳過內部結構
        if self.is_button:
            return
        
        # 語意化命名
        if data_layer:
            class_name = self._semantic_name(data_layer, tag)
        elif existing_class:
            class_name = self._semantic_name(existing_class.split()[0], tag)
        else:
            class_name = self._semantic_name(tag, tag)
        
        bem_class = f"{self.section}__{class_name}"
        
        # 過濾並儲存 CSS
        if style:
            filtered_props = self._filter_style(style)
            if filtered_props and bem_class not in self.css_rules:
                self.css_rules[bem_class] = filtered_props
        
        attrs_dict['class'] = bem_class
        
        attr_str = ' '.join(f'{k}="{v}"' for k, v in attrs_dict.items() if v)
        tag_str = f'{self._get_indent()}<{tag} {attr_str}>' if attr_str else f'{self._get_indent()}<{tag}>'
        self.html_lines.append(tag_str)
        
        self.indent_level += 1
    
    def handle_endtag(self, tag):
        if self.is_button:
            # 按鈕結束時輸出 <a> 標籤
            if self.pending_text:
                self.html_lines.append(f'{self._get_indent()}<a href="#" class="{self.button_class}">{self.pending_text}</a>')
                self.pending_text = None
            self.is_button = False
            self.button_class = None
            return
        
        self.indent_level -= 1
        self.html_lines.append(f'{self._get_indent()}</{tag}>')
    
    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        
        # 按鈕內的文字
        if self.is_button:
            self.pending_text = text
            return
        
        # 檢查是否為標題
        if text in self.headings:
            heading_tag = self.headings[text]
            class_name = self._semantic_name('title', heading_tag)
            bem_class = f"{self.section}__{class_name}"
            
            # 替換上一行的 div 為 heading
            if self.html_lines:
                last_line = self.html_lines[-1]
                if '<div' in last_line:
                    self.html_lines[-1] = last_line.replace('<div', f'<{heading_tag}').replace('class="', f'class="{bem_class} ')
                    self.html_lines.append(f'{self._get_indent()}{text}')
                    return
        
        self.html_lines.append(f'{self._get_indent()}{text}')
    
    def handle_startendtag(self, tag, attrs):
        if self.is_button:
            return
        
        attrs_dict = dict(attrs)
        attrs_dict.pop('style', None)
        attrs_dict.pop('data-layer', None)
        attrs_dict.pop('data-svg-wrapper', None)
        
        attr_str = ' '.join(f'{k}="{v}"' for k, v in attrs_dict.items() if v)
        self.html_lines.append(f'{self._get_indent()}<{tag} {attr_str} />' if attr_str else f'{self._get_indent()}<{tag} />')
    
    def get_results(self):
        return '\n'.join(self.html_lines), self.css_rules


def merge_css(css_rules: dict) -> dict:
    """合併相同的 CSS 規則"""
    props_to_classes = {}
    
    for class_name, props in css_rules.items():
        props_key = tuple(sorted(props))
        if props_key not in props_to_classes:
            props_to_classes[props_key] = []
        props_to_classes[props_key].append(class_name)
    
    merged = OrderedDict()
    for props, classes in props_to_classes.items():
        key = ',\n'.join(f'.{c}' for c in classes)
        merged[key] = list(props)
    
    return merged


def analyze_figma(figma_code: str) -> tuple:
    """第一階段：分析代碼，返回可能的標題和按鈕"""
    analyzer = FigmaAnalyzer()
    analyzer.feed(figma_code)
    return analyzer.get_titles(), analyzer.get_buttons()


def generate_php(html: str, section: str, notes: str = '') -> str:
    """生成 PHP 區塊"""
    lines = [
        f'\n<!-- ========== 區塊：{section} ========== -->'
    ]
    if notes:
        lines.append(f'<!-- 備註：{notes} -->')
    
    lines.append(f'<section class="{section}">')
    lines.append(html)
    lines.append('</section>')
    
    return '\n'.join(lines)


def generate_css(rules: dict, section: str, notes: str = '') -> str:
    """生成 CSS"""
    lines = [
        f'\n/* ========== 區塊：{section} ========== */'
    ]
    if notes:
        lines.append(f'/* 備註：{notes} */')
    lines.append('')
    
    for selector, props in rules.items():
        if not props:
            continue
        lines.append(f'{selector} {{')
        for prop in props:
            lines.append(f'    {prop};')
        lines.append('}')
        lines.append('')
    
    return '\n'.join(lines)


def process(page: str, section: str, figma_code: str, headings: dict = None, notes: str = '', base_path: str = '.'):
    """主處理函數"""
    
    extractor = StyleExtractor(section, headings)
    extractor.feed(figma_code)
    html_content, css_rules = extractor.get_results()
    
    merged_css = merge_css(css_rules)
    
    php_block = generate_php(html_content, section, notes)
    css_block = generate_css(merged_css, section, notes)
    
    php_path = os.path.join(base_path, 'pages', f'page-{page}.php')
    css_path = os.path.join(base_path, 'assets', 'css', 'pages', f'page-{page}.css')
    
    os.makedirs(os.path.dirname(php_path), exist_ok=True)
    os.makedirs(os.path.dirname(css_path), exist_ok=True)
    
    if os.path.exists(php_path):
        with open(php_path, 'a', encoding='utf-8') as f:
            f.write(php_block)
        print(f'📝 追加 PHP: {php_path}')
    else:
        with open(php_path, 'w', encoding='utf-8') as f:
            f.write(f'<?php\n/**\n * Page: {page}\n */\n?>')
            f.write(php_block)
        print(f'✅ 建立 PHP: {php_path}')
    
    if os.path.exists(css_path):
        with open(css_path, 'a', encoding='utf-8') as f:
            f.write(css_block)
        print(f'📝 追加 CSS: {css_path}')
    else:
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(f'/**\n * Page: {page}\n */\n')
            f.write(css_block)
        print(f'✅ 建立 CSS: {css_path}')
    
    return php_path, css_path


def main():
    parser = argparse.ArgumentParser(description='Figma to WordPress 分檔工具')
    parser.add_argument('--page', '-p', required=True, help='頁面名稱')
    parser.add_argument('--section', '-s', required=True, help='區塊名稱')
    parser.add_argument('--notes', '-n', default='', help='備註')
    parser.add_argument('--input', '-i', required=True, help='Figma HTML 檔案')
    parser.add_argument('--base', '-b', default='.', help='專案根目錄')
    parser.add_argument('--headings', '-H', default='{}', help='標題對照 JSON，如 {"文字":"h2"}')
    parser.add_argument('--analyze', '-a', action='store_true', help='只分析，不產生檔案')
    
    args = parser.parse_args()
    
    with open(args.input, 'r', encoding='utf-8') as f:
        figma_code = f.read()
    
    if args.analyze:
        titles, buttons = analyze_figma(figma_code)
        print("可能的標題：")
        for i, t in enumerate(titles, 1):
            print(f"  {i}. {t}")
        print("\n按鈕文字：")
        for b in buttons:
            print(f"  - {b}")
    else:
        headings = json.loads(args.headings)
        process(args.page, args.section, figma_code, headings, args.notes, args.base)


if __name__ == '__main__':
    main()
