# 导入句子转换器库，用于文本嵌入和语义相似度计算
from sentence_transformers import SentenceTransformer

# 从 Hugging Face Hub 下载预训练的嵌入模型
# google/embeddinggemma-300m 是一个轻量级的文本嵌入模型
model = SentenceTransformer("google/embeddinggemma-300m")

# 定义查询问题和候选文档，用于演示语义搜索功能
# 用户查询：询问哪个行星被称为红色星球
query = "Which planet is known as the Red Planet?"

# 候选文档列表：包含不同行星的描述信息
# 其中第二个文档包含正确答案（火星）
documents = [
    "Venus is often called Earth's twin because of its similar size and proximity.",  # 金星描述
    "Mars, known for its reddish appearance, is often referred to as the Red Planet.",  # 火星描述（正确答案）
    "Jupiter, the largest planet in our solar system, has a prominent red spot.",  # 木星描述
    "Saturn, famous for its rings, is sometimes mistaken for the Red Planet."  # 土星描述
]

# 将查询文本转换为向量表示（嵌入）
# encode_query 方法专门用于编码查询文本
query_embeddings = model.encode_query(query)

# 将所有候选文档转换为向量表示
# encode_document 方法专门用于编码文档文本
document_embeddings = model.encode_document(documents)

# 打印嵌入向量的维度信息
# 查询嵌入：(768,) 表示768维的向量
# 文档嵌入：(4, 768) 表示4个文档，每个都是768维向量
print(query_embeddings.shape, document_embeddings.shape)
# (768,) (4, 768)

# 计算查询与每个文档之间的余弦相似度
# 相似度越高，表示文档与查询越相关
similarities = model.similarity(query_embeddings, document_embeddings)

# 打印相似度分数
# 结果是一个张量，包含查询与4个文档的相似度分数
# 数值越接近1表示越相似，越接近0表示越不相似
print(similarities)
# 输出示例：tensor([[0.3011, 0.6359, 0.4930, 0.4889]])
# 可以看出第二个文档（索引1）的相似度最高（0.6359），这正是包含"火星"答案的文档
