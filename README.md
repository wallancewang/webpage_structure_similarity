## 依赖信息

selenium==4.19.0<br>
用于模拟chrome浏览器发起请求获取网页源码<br>
cssutils==2.10.2<br>
用于解析css源码<br>
beautifulsoup4==4.11.1<br>
用于解析html源码构建domtree<br>
chromedriver<br>
配合selenium使用，模拟chrome浏览器自动化发起请求

## 入口信息
main.py：输入参数中传入待比较的两个网页的url，通过WebPageSimilarity的实例对象调用get_similarity方法实现相似度分析

## 代码功能描述

similarity.py: 网页相似度判定核心方法实现，WebPageSimilarity类中的get_similarity方法，
可以返回两个网页相似度标志和分数<br>
config: config_loader.py负责读取config.yaml配置文件并返回配置对象<br>
dom_tree: 实现dom tree构建及预处理相关方法<br>
- dom_preprocess.py: 定义DomProcessor类封装dom tree预处理和css解析相关的方法
- html_tree.py: 实现了自定义的树结点，包含向量化所需要的结点属性，以及结点的深度高度等信息<br>

download: page_download.py实现网页下载的两种方法<br>
model: html及css向量化的方法
- html_embedding.py: 实现bag-of-words，序列化成文本后向量化，基于树结构向量化三种方法
- openai_model.py: 封装调用openai text embedding相关方法
- registry.py: 实现向量化方法类的注册器

util: 公共方法，这里包括设置和创建logger的方法log_util.py

## 其它数据和信息

docs: 网页相似度实现方案说明文档<br>
config: config.yaml存放网页相似度判定各模块涉及的配置参数<br>
datas: 包含三个用于测试的html源文件，前两个来源是华为广告主页，最后一个来源华为云<br>
tests: 包含各模块以及整体相似度判定的测试用例
