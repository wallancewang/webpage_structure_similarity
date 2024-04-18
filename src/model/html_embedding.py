from src.config.config_loader import HtmlSimCfg, OpenaiCfg
from src.dom_tree.html_tree import TreeNode
from src.model.openai_model import OpenaiEmbedding
from src.model.registry import EmbedRegistry
from src.util.log_util import create_logger

logger = create_logger(__name__)


class Embedder:
    '''
    html编码器基类
    '''

    def __init__(self, model_cfg: HtmlSimCfg, openai_cfg: OpenaiCfg):
        self.cfg = model_cfg
        self.openai_embed_model = OpenaiEmbedding(openai_cfg)

    def get_feature_vec(self, tree_root: TreeNode):
        raise NotImplementedError


@EmbedRegistry.registry('bow')
class BowEmbedder(Embedder):
    def get_feature_vec(self, tree_root: TreeNode):
        '''
        利用节点类型和属性值构造虚拟word，利用bag-of-words和hash构造特征
        :return dom_tree的特征向量
        '''
        feature_vec = [0] * self.cfg.feature_dim_bow
        # 先序遍历得到结点列表
        node_list, _ = tree_root.traverse_preorder()
        # 深度衰减系数，深度越大，对应结点特征权重越低
        decay = self.cfg.depth_decay
        warmup_depth = self.cfg.warmup_depth
        for node in node_list:
            attr_dict = node.attr_dict
            depth = node.depth
            css_mark = attr_dict.get('css_mark', 0)
            for attr_key, attr_value in attr_dict.items():
                if attr_key == 'css_mark':
                    continue
                # 利用结点和属性信息构造虚拟word
                word = f'{node.tag_name}_{attr_key}_{attr_value}'
                # 根据深度衰减计算权重
                weight = decay ** max(0, depth - warmup_depth)
                if css_mark:
                    # 对css修饰的结点，增加权重
                    weight = min(1, weight * 2)
                word_hash = abs(hash(word)) % (10 ** 8)
                index = word_hash % self.cfg.feature_dim_bow
                feature_vec[index] += weight
        return feature_vec


@EmbedRegistry.registry('plain_text')
class TextEmbedder(Embedder):

    def get_feature_vec(self, tree_root: TreeNode):
        '''
        将处理后的domTree序列化为html源文本后，利用openai text-embddding向量化
        :return dom_tree的embedding结果
        '''
        exclude_tags = self.cfg.embed_ignore_tags
        max_depth = self.cfg.max_depth
        html_text = tree_root.get_html_structure_code(exclude_tags, max_depth)
        logger.debug('getting openai embedding for filtered html code')
        html_embed = self.openai_embed_model.get_text_embed(html_text)
        logger.debug('openai embedding done')
        return html_embed


@EmbedRegistry.registry('html_structure')
class StructureEmbedder(Embedder):
    def select_subtrees_for_embedding(self, tree_root: TreeNode):
        nodes_for_embeds = []

        def node_selector(node):
            '''
            先序遍历递归的筛选可以直接序列化编码的子树
            '''
            leaf_tag = 0
            html_code = ''
            # 判断以该结点为根结点的子树是否可以直接序列化编码
            if node.height <= self.cfg.min_height:
                leaf_tag = 1
                html_code = node.get_html_structure_code(exclude_attrs=self.cfg.embed_ignore_tags)
            elif node.height <= self.cfg.max_height:
                html_code = node.get_html_structure_code(exclude_attrs=self.cfg.embed_ignore_tags)
                if len(html_code) <= self.cfg.min_code_len:
                    leaf_tag = 1
            if leaf_tag:
                # 子树可以直接序列化编码
                nodes_for_embeds.append((html_code, node.index, leaf_tag))
            else:
                # 当前子树高度过大，需要分治，此时需要先编码结点文本
                node_text = node.get_node_html_tag(exclude_attrs=self.cfg.embed_ignore_tags)
                if node_text:
                    nodes_for_embeds.append((node_text, node.index, leaf_tag))
                # 继续进入子树判断
                for child in node.children:
                    node_selector(child)

        node_selector(tree_root)
        return nodes_for_embeds

    def get_feature_vec(self, tree_root: TreeNode):
        '''
        逐层计算子树embedding，通过树结构聚合到父节点
        :return dom_tree的embedding结果
        '''
        # 先序遍历得到结点列表以及计算各子树高度
        node_list, _ = tree_root.traverse_preorder()
        # 筛选得到需要向量化的子树/结点文本，以及对应结点的index
        nodes_for_embeds = self.select_subtrees_for_embedding(tree_root)
        # 批量调用openai接口得到结点和部分子树的embedding
        node_texts = [text for text, _, _ in nodes_for_embeds]
        logger.debug(f'getting openai embedding for {len(nodes_for_embeds)} subtrees or nodes')
        embedding_list = self.openai_embed_model.get_text_embed(node_texts)
        logger.debug('openai embedding done')
        node_embedding_list = [(None, 0)] * len(node_list)
        for i, (_, node_idx, is_leaf) in enumerate(nodes_for_embeds):
            node_embedding_list[node_idx - 1] = (embedding_list[i], is_leaf)
        # 子树/叶子结点embedding逐层聚合得到根节点embedding
        root_embedding = tree_root.get_structure_embed(node_embedding_list)
        return list(root_embedding)


class CssEmbedder(Embedder):
    def get_feature_vec(self, css_selector_dict):
        '''
        将css通过bag-of-words向量化,用于html和css分开计算相似度的场景
        :return css的特征向量
        '''
        feature_vec = [0.0] * self.cfg.feature_dim_bow
        for selector_text in css_selector_dict:
            for prop_key in css_selector_dict:
                prop_value = css_selector_dict.get(prop_key)
                word = f'{selector_text}_{prop_key}_{prop_value}'
                word_hash = abs(hash(word)) % (10 ** 8)
                index = word_hash % self.cfg.feature_dim_bow
                feature_vec[index] += 1.0
        return feature_vec
