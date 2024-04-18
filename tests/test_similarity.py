import unittest
from src.config.config_loader import TaskCfg
from src.similarity import WebPageSimilarity

config_file = '../config/config.yaml'
url1 = 'https://developer.huawei.com/consumer/cn/doc/promotion/ads_shenhe01-0000001055334495'
url2 = 'https://developer.huawei.com/consumer/cn/doc/promotion/ads_ocpc02-0000001058388925'
url3 = 'https://www.huaweicloud.com/product/cdn.html?utm_source=baidu&utm_medium=brand&utm_campaign=10033&utm_content=&utm_term=&utm_adplace=AdPlace024729'


class WebPageSimilarityTest(unittest.TestCase):
    def setUp(self):
        cfg = TaskCfg.load_config_yaml(config_file)
        # 测试脚本运行路径和main不同，需修改driver_file相对路径；如果配置中采用绝对路径，此处不需要修改
        cfg.html.driver_file = f'../{cfg.html.driver_file}'
        self.sim_model = WebPageSimilarity(cfg)

    def test_similarity_function(self):
        # 测试相似度判别功能，返回的相似度值应该是0-1之间的数
        sim_flag, sim_score = self.sim_model.get_similarity(url1, url2)
        self.assertTrue(0 <= sim_score <= 1)
        self.assertIn(sim_flag, [True, False])

    def test_similarity_performance(self):
        # 测试相似度判别效果，ur1和url2来自同一域，应该判别为相似；url1和url3来自不同域，应该判别为不相似
        sim_flag1, _ = self.sim_model.get_similarity(url1, url2)
        sim_flag2, _ = self.sim_model.get_similarity(url1, url3)
        self.assertTrue(sim_flag1)
        self.assertFalse(sim_flag2)


if __name__ == '__main__':
    unittest.main()
