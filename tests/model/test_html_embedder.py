import unittest
from src.config.config_loader import TaskCfg
from src.model.html_embedding import BowEmbedder, TextEmbedder, StructureEmbedder
from src.dom_tree.dom_preprocess import DomProcessor

local_html_path = '../../datas/huawei_ads_1.html'
config_file = '../../config/config.yaml'


class EmbedderTest(unittest.TestCase):
    def setUp(self):
        cfg = TaskCfg.load_config_yaml(config_file)
        self.model_cfg = cfg.similarity_model
        self.bow_embedder = BowEmbedder(cfg.similarity_model, cfg.openai)
        self.text_embedder = TextEmbedder(cfg.similarity_model, cfg.openai)
        self.structure_embedder = StructureEmbedder(cfg.similarity_model, cfg.openai)
        # 特征编码模型的测试依赖构建和预处理dom tree流程
        with open(local_html_path, 'r', encoding='utf-8') as f:
            html_text = f.read().strip()
        dom_processor = DomProcessor(html_text, cfg.html)
        dom_processor.filter_dom()
        dom_processor.process_css()
        self.tree_root = dom_processor.transform_dom_tree()

    def test_bow_embedding(self):
        # 测试bag-of-words编码模型
        feature_vec = self.bow_embedder.get_feature_vec(self.tree_root)
        self.assertTrue(isinstance(feature_vec, list))
        self.assertEqual(len(feature_vec), self.model_cfg.feature_dim_bow)

    def test_plain_text_embedding(self):
        # 测试树序列化文本编码器模型
        feature_vec = self.text_embedder.get_feature_vec(self.tree_root)
        self.assertTrue(isinstance(feature_vec, list))
        self.assertEqual(len(feature_vec), 1536)

    def test_structure_embedding(self):
        # 测试树序列化文本编码器模型
        feature_vec = self.structure_embedder.get_feature_vec(self.tree_root)
        self.assertTrue(isinstance(feature_vec, list))
        self.assertEqual(len(feature_vec), 1536)
