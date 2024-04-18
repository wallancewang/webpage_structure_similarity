import unittest
from src.model.openai_model import OpenaiEmbedding
from src.config.config_loader import TaskCfg

config_file = '../../config/config.yaml'


class OpenaiEmbeddingTest(unittest.TestCase):
    def setUp(self):
        cfg = TaskCfg.load_config_yaml(config_file)
        self.openai_model = OpenaiEmbedding(cfg.openai)
        self.openai_cfg = cfg.openai

    def test_normal_text_embedding(self):
        text = 'normal test case for openai embedding api'
        embed = self.openai_model.get_text_embed(text)
        self.assertTrue(isinstance(embed, list))
        self.assertEqual(len(embed), 1536)

    def test_long_text_embedding(self):
        text = 'a' * 10000
        embed = self.openai_model.get_text_embed(text)
        self.assertTrue(isinstance(embed, list))
        self.assertEqual(len(embed), 1536)

    def test_batch_text_embedding(self):
        text_list = ['test case for openai embedding api',
                     'give a high-quality embedding to represent the structure of the given html:',
                     '中文文本openai编码测试用例',
                     '<html><head></head><title></title><div class="main"></div></html>'
                     '<html><head></head><title></title></html>']
        embed_list = self.openai_model.get_text_embed(text_list)
        self.assertTrue(isinstance(embed_list, list))
        self.assertEqual(len(embed_list), len(text_list))
        for embed in embed_list:
            self.assertTrue(isinstance(embed, list))
            self.assertEqual(len(embed), 1536)


if __name__ == '__main__':
    unittest.main()