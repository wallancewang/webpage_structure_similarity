import bs4
import logging
import cssutils
import requests
from src.dom_tree.html_tree import TreeNode
from src.config.config_loader import HtmlCfg
from src.util.log_util import create_logger

logger = create_logger(__name__)


class DomProcessor:
    '''
    封装dom tree预处理相关的方法
    '''

    def __init__(self, raw_html, html_cfg: HtmlCfg):
        self.css_parser = cssutils.CSSParser(loglevel=logging.CRITICAL)
        self.cfg = html_cfg
        self.dom = bs4.BeautifulSoup(raw_html, 'lxml')

    def filter_dom(self):
        # 根据配置将指定的结点类型过滤
        for tag in self.cfg.filter_tags:
            elements = self.dom.find_all(tag)
            for ele in elements:
                ele.extract()

    def process_css(self):
        # 处理源码中的css
        selector_dict = self.get_css_selectors()
        if self.cfg.include_css:
            # 需要根据css selector选择对应dom结点添加属性
            logger.debug('begin to select css in dom tree')
            self.assign_selector_to_nodes(selector_dict)
            logger.debug('select css in dom tree done')
        self.css_dict = selector_dict

    @staticmethod
    def get_css_from_remote_url(css_link):
        # 从远端下载css
        try:
            css_text = requests.get(css_link, timeout=1).text
        except:
            css_text = ''
        return css_text

    def get_css_selectors(self):
        selector_dict = {}

        def process_css_text(css_text):
            # 利用css_utils解析css源码
            stylesheet = self.css_parser.parseString(css_text)
            for rule in stylesheet:
                if rule.type == rule.STYLE_RULE:
                    selector = rule.selectorText
                    prop_info = {}
                    for property in rule.style:
                        prop_info[property.name] = property.value
                    selector_dict[selector] = prop_info

        for tag in self.cfg.css_tags:
            for style_node in self.dom.find_all(tag):
                process_css_text(style_node.text)
                style_node.extract()
        if self.cfg.remote_css:
            # 从远端下载css
            for link in self.dom.find_all('link'):
                href = link.attrs.get('href', '')
                rel = link.attrs.get('rel', '')
                if href and 'stylesheet' in rel:
                    css_text = DomProcessor.get_css_from_remote_url(href)
                    if css_text:
                        process_css_text(css_text)
        return selector_dict

    def assign_selector_to_nodes(self, selector_dict):
        # 使用bs4基于selector找到修饰的dom，把css属性添加到dom属性中
        for selector in selector_dict:
            css_prop_info = selector_dict[selector]
            try:
                ele_list = self.dom.select(selector)
                for ele in ele_list:
                    ele.attrs['css_mark'] = 1
                    for key in css_prop_info:
                        if key not in ele.attrs:
                            ele.attrs[key] = css_prop_info.get(key)
            except NotImplementedError:
                pass

    def transform_dom_tree(self):
        # 通过先序遍历构建自定义html tree，便于后续向量化计算
        tree_root = TreeNode(tag_name='root', attr_dict={})

        def build_recursive(dom_node, parent_node):
            if dom_node.name:
                cur_node, add_flag = parent_node.add_child(dom_node)
                if add_flag:
                    for child in dom_node.children:
                        build_recursive(child, cur_node)

        dom_root = self.dom.contents[0]
        build_recursive(dom_root, tree_root)
        # 构建完成后将TreeNode的index清零，避免下一次实例化时index继续累加
        TreeNode.on_build()
        return tree_root
