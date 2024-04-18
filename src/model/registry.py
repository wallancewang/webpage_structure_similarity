class EmbedRegistry:
    '''
    向量化模型注册类，实现按照名称获取对应模型类
    '''
    model_dict = {}

    @classmethod
    def registry(cls, embed_name):
        def wrapper(embed_cls):
            cls.model_dict[embed_name] = embed_cls
            return embed_cls
        return wrapper

    @classmethod
    def get_embedding_cls(cls, embed_name):
        if embed_name not in cls.model_dict:
            raise ValueError(f'embedding method {embed_name} not defined')
        return cls.model_dict.get(embed_name)