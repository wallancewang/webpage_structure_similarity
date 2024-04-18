from openai import AzureOpenAI
from src.config.config_loader import OpenaiCfg


class OpenaiEmbedding:
    '''
    封装对openai text-embedding接口的调用
    '''
    def __init__(self, cfg: OpenaiCfg):
        self.cfg = cfg
        self.openai = AzureOpenAI(
            api_key=cfg.api_key,
            api_version=cfg.version,
            azure_endpoint=cfg.endpoint
        )

    def get_text_embed(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        texts = [text[:self.cfg.max_text_len] for text in texts]
        response = self.openai.embeddings.create(input=texts, model=self.cfg.embed_model_name)
        embed_data = response.data
        embed_list = [embed.embedding for embed in embed_data]
        if len(embed_list) == 1:
            return embed_list[0]
        return embed_list