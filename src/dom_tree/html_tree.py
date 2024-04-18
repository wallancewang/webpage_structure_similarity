import numpy as np


class TreeNode:
    '''
    自定义html tree的树结点结构
    '''
    _index = 0

    def __init__(self, tag_name, attr_dict, depth=0):
        self.tag_name = tag_name
        self.attr_dict = attr_dict
        self.index = TreeNode._index
        TreeNode._index += 1
        self.depth = depth  # 树的深度
        self.height = 0  # 当前结点的子树高度
        self.children = []
        self.child_keys = set()

    def add_child(self, dom_node):
        '''
        根据传入的dom结点在新构建的树中添加子结点
        '''
        dom_node_desc, node_attr_dict = TreeNode.create_dom_node_desc(dom_node)
        if dom_node_desc in self.child_keys and len(node_attr_dict) > 1:
            # 属性相同的siblings只添加一个
            return None, False
        else:
            child_node = TreeNode(dom_node.name, node_attr_dict, self.depth + 1)
            self.children.append(child_node)
            self.child_keys.add(dom_node_desc)
            return child_node, True

    def get_node_html_tag(self, exclude_attrs=None):
        '''
        根据属性类型和属性值，构造结点html文本
        '''
        if self.tag_name == 'root':
            return ''
        html_tag = f'<{self.tag_name}'
        if self.attr_dict:
            html_tag += ' '
            for attr_key, attr_val in self.attr_dict.items():
                if exclude_attrs and attr_key in exclude_attrs or attr_key == 'css_mark':
                    continue
                html_tag += f'{attr_key}={attr_val} '
        html_tag = html_tag.strip() + '>'
        return html_tag

    @staticmethod
    def create_dom_node_desc(dom_node):
        '''
        根据传入的dom结点构造结点文本表示，这里目的是sibling去重以及筛选有用的属性
        '''
        node_text = dom_node.name
        attr_dict = {'css_mark': dom_node.attrs.get('css_mark', 0)}
        if dom_node.attrs:
            node_text += '->'
            for key in dom_node.attrs:
                if key in ['css_mark'] or 'href' in key:
                    continue
                value = dom_node.attrs.get(key)
                value_text = value if isinstance(value, str) else ' '.join(value)
                if value_text == '' or 'javascript' in value_text or value_text.startswith('url('):
                    continue
                node_text += f'{key}={value_text}|'
                attr_dict[key] = value_text
            while node_text.endswith('|'):
                node_text = node_text[:-1]
        if node_text.endswith('->'):
            node_text = node_text[:-1]
        return node_text, attr_dict

    @classmethod
    def on_build(cls):
        # 构建新树完成时调用，将index清零，防止多次实例化时index不断累加
        cls._index = 0

    def traverse_preorder(self):
        '''
        先序遍历得到结点列表，以及计算各结点高度
        '''
        node_list = []
        height = 0
        if self.tag_name != 'root':
            node_list.append(self)
        for child_node in self.children:
            sub_nodes, sub_height = child_node.traverse_preorder()
            node_list.extend(sub_nodes)
            height = max(height, sub_height)
        height += 1
        self.height = height
        return node_list, height

    def get_html_structure_code(self, exclude_attrs, max_depth=100):
        '''
        将当前结点对应的子树序列化为html源文本
        '''
        if self.depth < max_depth:
            html_code = self.get_node_html_tag(exclude_attrs)
        elif self.depth == max_depth:
            return self.get_node_html_tag() + f'</{self.tag_name}>'
        else:
            return ''
        if self.children:
            for child_node in self.children:
                child_code = child_node.get_html_structure_code(exclude_attrs, max_depth)
                if child_code:
                    html_code += '\n' + child_code
        if self.tag_name != 'root':
            html_code += f'\n</{self.tag_name}>'
        if html_code.startswith('\n'):
            html_code = html_code[1:]
        return html_code

    def get_structure_embed(self, node_embed_list):
        '''
        利用先序遍历将子树embedding逐层向上聚合，得到最终树的embedding
        '''
        # 根结点的embedding为空
        node_base_embed = node_embed_list[self.index - 1][0] if self.index > 0 else None
        child_embeds = []
        # 对于叶子结点对应的子树分治获取对应embedding
        for child in self.children:
            child_idx = child.index
            child_embed, child_tag = node_embed_list[child_idx]
            if child_tag == 1:
                child_embeds.append(child_embed)
            else:
                child_embeds.append(child.get_structure_embed(node_embed_list))
        # 这里采用简单平均聚合；实际在有训练情况下，可以采用transform等复杂结构聚合捕捉子节点序关系
        child_embeds = np.array(child_embeds)
        node_embed = np.mean(child_embeds, axis=0)
        if node_base_embed is not None:
            node_embed = (node_base_embed + node_embed) / 2
        return node_embed
