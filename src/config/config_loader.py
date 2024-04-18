import yaml


class OpenaiCfg:
    '''
    调用openai接口相关参数
    '''

    def __init__(self, openai_cfg):
        self.api_key = openai_cfg['api_key']
        self.endpoint = openai_cfg['endpoint']
        self.version = openai_cfg['version']
        self.embed_model_name = openai_cfg['embed_model_name']
        self.max_text_len = openai_cfg['max_text_len']


class HtmlCfg:
    '''
    html源码获取及预处理相关参数
    '''

    def __init__(self, html_cfg):
        self.fetch_method = html_cfg['fetch_method']
        self.driver_file = html_cfg['driver_file']
        self.filter_tags = html_cfg['filter_tags'].split(',')
        self.css_tags = html_cfg['css_tags'].split(',')
        self.remote_css = html_cfg['get_remote_css']
        self.include_css = html_cfg['include_css_in_html']


class HtmlSimCfg:
    '''
    页面相似度比较相关参数
    '''

    def __init__(self, sim_cfg):
        self.method = sim_cfg['method']
        self.feature_dim_bow = sim_cfg['feature_dim_bow']
        self.depth_decay = sim_cfg['depth_decay']
        self.warmup_depth = sim_cfg['warmup_depth']
        self.min_height = sim_cfg['min_height']
        self.max_height = sim_cfg['max_height']
        self.min_code_len = sim_cfg['min_code_len']
        self.max_depth = sim_cfg['max_depth']
        self.embed_ignore_tags = sim_cfg['embed_ignore_tags'].split(',')
        self.bow_thre = sim_cfg['bow_threshold']
        self.embed_thre = sim_cfg['embedding_threshold']


class TaskCfg:
    def __init__(self, openai_cfg, html_cfg, sim_cfg):
        self.openai = OpenaiCfg(openai_cfg)
        self.html = HtmlCfg(html_cfg)
        self.similarity_model = HtmlSimCfg(sim_cfg)

    @classmethod
    def load_config_yaml(cls, config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            cfg_obj = yaml.safe_load(f)
        task_cfg = cls(cfg_obj['openai'], cfg_obj['html'], cfg_obj['similarity_model'])
        return task_cfg