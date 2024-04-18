import unittest
import bs4
from src.dom_tree.dom_preprocess import DomProcessor
from src.dom_tree.html_tree import TreeNode
from src.config.config_loader import TaskCfg

local_html_path = '../../datas/huawei_ads_1.html'
config_file = '../../config/config.yaml'


class DomTreeTest(unittest.TestCase):
    '''
    用于测试dom tree预处理和转换相关的操作
    '''

    def setUp(self):
        with open(local_html_path, 'r', encoding='utf-8') as f:
            self.html_text = f.read().strip()
        cfg = TaskCfg.load_config_yaml(config_file)
        self.html_cfg = cfg.html

    def test_dom_tree_build(self):
        # 测试利用bs4构造dom tree
        dom_processor = DomProcessor(self.html_text, self.html_cfg)
        self.assertTrue(isinstance(dom_processor.dom, bs4.BeautifulSoup))
        self.assertGreater(len(dom_processor.dom.contents), 0)
        self.assertEqual(dom_processor.dom.contents[0].name, 'html')

    def test_dom_tree_filter(self):
        # 测试filter_dom方法是否按预期去除对应标签
        dom_processor = DomProcessor(self.html_text, self.html_cfg)
        dom_processor.filter_dom()
        find_list = []
        for tag in self.html_cfg.filter_tags:
            elements = dom_processor.dom.find_all(tag)
            find_list.extend(elements)
        self.assertEqual(len(find_list), 0)

    def test_process_css(self):
        dom_processor = DomProcessor(self.html_text, self.html_cfg)
        dom_processor.process_css()
        find_list = []
        for tag in self.html_cfg.css_tags:
            elements = dom_processor.dom.find_all(tag)
            find_list.extend(elements)
        self.assertIn('css_dict', dom_processor.__dict__)
        self.assertEqual(len(find_list), 0)

    def test_transform_dom_tree(self):
        # 测试将bs4 dom tree重新构建为自定义树结构的方法
        dom_processor = DomProcessor(self.html_text, self.html_cfg)
        tree_root = dom_processor.transform_dom_tree()
        self.assertTrue(isinstance(tree_root, TreeNode))


if __name__ == '__main__':
    unittest.main()