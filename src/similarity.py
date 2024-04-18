import numpy as np
from src.config.config_loader import TaskCfg
from src.download.page_download import WebDriverDownloader, BaseDownloader
from src.dom_tree.dom_preprocess import DomProcessor
from src.model.registry import EmbedRegistry
from src.model.html_embedding import CssEmbedder
from src.util.log_util import create_logger

logger = create_logger(__name__)


def cosine_similarity(vec1, vec2):
    '''
    向量余弦相似度计算
    '''
    if isinstance(vec1, list):
        vec1 = np.array(vec1)
    if isinstance(vec2, list):
        vec2 = np.array(vec2)
    dot_pro = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0
    cos_sim = dot_pro / (norm_vec1 * norm_vec2)
    return cos_sim


def bow_vec_similarity(vec1, vec2):
    '''
    基于曼哈顿距离计算稀疏向量相似度
    '''
    diff = 0
    total = 0
    for i in range(len(vec1)):
        diff += abs(vec1[i] - vec2[i])
        total += max(vec1[i], vec2[i])
    if total == 0:
        return 0
    return 1 - diff / total


class WebPageSimilarity:
    '''
    网页相似度分析主流程
    '''

    def __init__(self, cfg: TaskCfg):
        self.cfg = cfg
        # 根据配置选择网页下载方法类
        self.page_downloader = WebDriverDownloader(cfg.html)
        if cfg.html.fetch_method != 'webdriver':
            self.page_downloader = BaseDownloader(cfg.html)
        # 从注册器中获取向量化方法类
        embedder_cls = EmbedRegistry.get_embedding_cls(cfg.similarity_model.method)
        self.embedder = embedder_cls(cfg.similarity_model, cfg.openai)
        self.css_embedder = None
        if not cfg.html.include_css:
            # 没有将css属性添加到对应html tag时才需要单独计算css特征向量
            self.css_embedder = CssEmbedder(cfg.similarity_model, cfg.openai)

    def get_page_feature_pipeline(self, url):
        '''
        根据url下载源码，处理dom tree以及提取特征流程
        '''
        html_text = self.page_downloader.get_html(url)
        if not html_text:
            # 下载网页失败，返回空的特征向量
            logger.error(f'download from {url} fails!')
            return [], []
        logger.info('begin to build dom tree')
        dom_processor = DomProcessor(html_text, self.cfg.html)
        logger.info('build dom tree done;begin to preprocess dom tree')
        dom_processor.filter_dom()
        dom_processor.process_css()
        tree_root = dom_processor.transform_dom_tree()
        logger.info('preprocess dom tree done;begin to get embedding')
        feature_vec = self.embedder.get_feature_vec(tree_root)
        css_vec = None
        if self.css_embedder is not None:
            css_vec = self.css_embedder.get_feature_vec(dom_processor.css_dict)
        logger.info('embedding done')
        return feature_vec, css_vec

    def get_similarity(self, url1, url2):
        logger.info(f'begin to get features of {url1}')
        feature_vec1, css_vec1 = self.get_page_feature_pipeline(url1)
        if feature_vec1:
            logger.info(f'features of {url1} done')
        else:
            # 下载网页失败时无法向量化，返回不相似
            logger.error(f'features of {url1} fails')
            return False, 0
        logger.info(f'begin to get features of {url2}')
        feature_vec2, css_vec2 = self.get_page_feature_pipeline(url2)
        if feature_vec2:
            logger.info(f'features of {url2} done')
        else:
            # 下载网页失败时无法向量化，返回不相似
            logger.error(f'features of {url2} fails')
            return False, 0
        is_sim = False
        if self.cfg.similarity_model.method == 'bow':
            # 使用bag-of-words向量化时基于曼哈顿距离计算相似度
            score = bow_vec_similarity(feature_vec1, feature_vec2)
            sim_score = score
            logger.debug(f'bow similarity score is {score}')
            if score >= self.cfg.similarity_model.bow_thre:
                is_sim = True
        else:
            # 使用文本编码器时基于余弦相似度计算
            score = cosine_similarity(feature_vec1, feature_vec2)
            sim_score = score
            logger.debug(f'cosine similarity score is {score}')
            if score >= self.cfg.similarity_model.embed_thre:
                is_sim = True
        if is_sim and not self.cfg.html.include_css:
            # css属性没有添加到对应的html tag中，需要额外计算css相似度
            css_score = bow_vec_similarity(css_vec1, css_vec2)
            sim_score = (sim_score + css_score) / 2
            logger.debug(f'css similarity score is {css_score}')
            if css_score < self.cfg.similarity_model.bow_thre:
                is_sim = False
        return is_sim, sim_score
