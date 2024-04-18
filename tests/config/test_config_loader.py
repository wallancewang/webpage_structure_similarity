import unittest
from src.config.config_loader import TaskCfg

config_file = '../../config/config.yaml'


class TaskCfgTest(unittest.TestCase):
    def setUp(self):
        self.cfg = TaskCfg.load_config_yaml(config_file)

    def test_load_config_overall(self):
        # 测试配置参数整体的完整性
        self.assertIn('openai', self.cfg.__dict__)
        self.assertIn('html', self.cfg.__dict__)
        self.assertIn('similarity_model', self.cfg.__dict__)

    def test_load_config_openai(self):
        # 测试openai相关的配置参数完整性
        self.assertIn('api_key', self.cfg.openai.__dict__)
        self.assertIn('endpoint', self.cfg.openai.__dict__)
        self.assertIn('version', self.cfg.openai.__dict__)
        self.assertIn('embed_model_name', self.cfg.openai.__dict__)
        self.assertIn('max_text_len', self.cfg.openai.__dict__)

    def test_load_config_html(self):
        # 测试页面下载及预处理相关的配置参数完整性
        self.assertIn('fetch_method', self.cfg.html.__dict__)
        self.assertIn(self.cfg.html.fetch_method, ['webdriver', 'base'])
        self.assertIn('driver_file', self.cfg.html.__dict__)
        self.assertIn('filter_tags', self.cfg.html.__dict__)
        self.assertIn('css_tags', self.cfg.html.__dict__)
        self.assertIn('include_css', self.cfg.html.__dict__)
        self.assertIn('remote_css', self.cfg.html.__dict__)

    def test_load_config_sim_model(self):
        # 测试特征提取与相似度计算相关的配置参数完整性
        self.assertIn('method', self.cfg.similarity_model.__dict__)
        self.assertIn(self.cfg.similarity_model.method, ['bow', 'plain_text', 'html_structure'])
        if self.cfg.similarity_model.method == 'bow':
            self.assertIn('feature_dim_bow', self.cfg.similarity_model.__dict__)
            self.assertIn('depth_decay', self.cfg.similarity_model.__dict__)
            self.assertIn('warmup_depth', self.cfg.similarity_model.__dict__)
            self.assertIn('bow_thre', self.cfg.similarity_model.__dict__)
        elif self.cfg.similarity_model.method == 'plain_text':
            self.assertIn('embed_ignore_tags', self.cfg.similarity_model.__dict__)
            self.assertIn('embed_thre', self.cfg.similarity_model.__dict__)
            self.assertIn('max_depth', self.cfg.similarity_model.__dict__)
        else:
            self.assertIn('embed_ignore_tags', self.cfg.similarity_model.__dict__)
            self.assertIn('embed_thre', self.cfg.similarity_model.__dict__)
            self.assertIn('min_height', self.cfg.similarity_model.__dict__)
            self.assertIn('max_height', self.cfg.similarity_model.__dict__)
            self.assertIn('min_code_len', self.cfg.similarity_model.__dict__)


if __name__ == '__main__':
    unittest.main()
