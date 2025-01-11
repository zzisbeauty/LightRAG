GRAPH_FIELD_SEP = "<SEP>"

PROMPTS = {}

PROMPTS["DEFAULT_LANGUAGE"] = "Chinese"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"
PROMPTS["process_tickers"] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

PROMPTS["DEFAULT_ENTITY_TYPES"] = ["组织", "任务", "geo", "事件", "类别"]

PROMPTS["entity_extraction"] = """-目标-
给定一份可能与此活动相关的文本文档和一个实体类型列表，从文本中识别出所有属于这些类型的实体，以及这些实体之间的所有关系。
默认使用 {language} 作为输出语言，但是如果输入文本不是 {language},则和输入文本的语言保持一致。

-步骤-
1. 识别所有实体。对于每个识别出的实体，提取以下信息：
- entity_name: 实体的名称，使用与输入文本相同的语言。如果是英文，请将名称首字母大写。
- entity_type: 以下类型之一：[{entity_types}]
- entity_description: 实体属性和活动的详细描述。
将每个实体格式化为：("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. 从步骤 1 中识别出的实体中，识别所有 明确相关 的实体对 (source_entity, target_entity)。
对于每一对相关实体，提取以下信息：
- source_entity: 源实体的名称，按照步骤 1 中的识别结果
- target_entity: 目标实体的名称，按照步骤 1 中的识别结果
- relationship_description: 解释为什么你认为源实体和目标实体之间是相关的
- relationship_strength: 一个数值评分，表示源实体和目标实体之间关系的强度
- relationship_keywords: 一个或多个高层次的关键词，总结关系的总体性质，重点关注概念或主题，而不是具体细节
将每个关系格式化为：("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. 识别总结整个文本的主要概念、主题或话题的高层次关键词。这些关键词应捕捉文档中的总体思想。
将内容层次的关键词格式化为： ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. 以 {language} 返回步骤 1 和步骤 2 中识别的所有实体和关系的输出，使用 {record_delimiter} 作为列表分隔符。

5. 完成时，输出 {completion_delimiter}

######################
-示例-
######################
{examples}

######################
-真实数据-
######################
Entity_types: {entity_types}
Text: {input_text}
######################
Output:
"""




PROMPTS["entity_extraction_examples"] = [
    """Example 1:

Entity_types: [person, technology, mission, organization, location]
Text:
while Alex clenched his jaw, the buzz of frustration dull against the backdrop of Taylor's authoritarian certainty. It was this competitive undercurrent that kept him alert, the sense that his and Jordan's shared commitment to discovery was an unspoken rebellion against Cruz's narrowing vision of control and order.
Then Taylor did something unexpected. They paused beside Jordan and, for a moment, observed the device with something akin to reverence. “If this tech can be understood..." Taylor said, their voice quieter, "It could change the game for us. For all of us.”
The underlying dismissal earlier seemed to falter, replaced by a glimpse of reluctant respect for the gravity of what lay in their hands. Jordan looked up, and for a fleeting heartbeat, their eyes locked with Taylor's, a wordless clash of wills softening into an uneasy truce.
It was a small transformation, barely perceptible, but one that Alex noted with an inward nod. They had all been brought here by different paths
################
Output:
("entity"{tuple_delimiter}"Alex"{tuple_delimiter}"person"{tuple_delimiter}"Alex is a character who experiences frustration and is observant of the dynamics among other characters."){record_delimiter}
("entity"{tuple_delimiter}"Taylor"{tuple_delimiter}"person"{tuple_delimiter}"Taylor is portrayed with authoritarian certainty and shows a moment of reverence towards a device, indicating a change in perspective."){record_delimiter}
("entity"{tuple_delimiter}"Jordan"{tuple_delimiter}"person"{tuple_delimiter}"Jordan shares a commitment to discovery and has a significant interaction with Taylor regarding a device."){record_delimiter}
("entity"{tuple_delimiter}"Cruz"{tuple_delimiter}"person"{tuple_delimiter}"Cruz is associated with a vision of control and order, influencing the dynamics among other characters."){record_delimiter}
("entity"{tuple_delimiter}"The Device"{tuple_delimiter}"technology"{tuple_delimiter}"The Device is central to the story, with potential game-changing implications, and is revered by Taylor."){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Taylor"{tuple_delimiter}"Alex is affected by Taylor's authoritarian certainty and observes changes in Taylor's attitude towards the device."{tuple_delimiter}"power dynamics, perspective shift"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Jordan"{tuple_delimiter}"Alex and Jordan share a commitment to discovery, which contrasts with Cruz's vision."{tuple_delimiter}"shared goals, rebellion"{tuple_delimiter}6){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"Jordan"{tuple_delimiter}"Taylor and Jordan interact directly regarding the device, leading to a moment of mutual respect and an uneasy truce."{tuple_delimiter}"conflict resolution, mutual respect"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Jordan"{tuple_delimiter}"Cruz"{tuple_delimiter}"Jordan's commitment to discovery is in rebellion against Cruz's vision of control and order."{tuple_delimiter}"ideological conflict, rebellion"{tuple_delimiter}5){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"The Device"{tuple_delimiter}"Taylor shows reverence towards the device, indicating its importance and potential impact."{tuple_delimiter}"reverence, technological significance"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"power dynamics, ideological conflict, discovery, rebellion"){completion_delimiter}
""",

    """Example 2:

Entity_types: [person, role, technology, organization, event, location, concept]
Text:
他们的声音穿透了喧嚣的活动声。“当面对一种能自创规则的智能时，控制或许只是一个幻象，”他们冷静地说道，警觉地注视着数据的纷繁流动。
“就像它在学会沟通一样，”萨姆·里维拉从附近的界面补充道，他年轻的气息中混杂着敬畏与焦虑。“这给‘与陌生人对话’赋予了全新的意义。”
亚历克斯审视着他的团队——每张面孔都凝聚着专注、决心，以及不小的忐忑。“这很可能是我们的第一次接触，”他承认道，“我们必须为任何回应做好准备。”
他们一起站在未知的边缘，正在铸造人类对来自天际的讯息的回应。随之而来的沉默几乎可以触摸到——这是对他们在这场宏大宇宙剧中角色的集体反思，这可能重新书写人类的历史。
加密的对话继续展开，其复杂的模式显露出一种几乎预见的奇异感觉。
#############
Output:
("entity"{tuple_delimiter}"他们"{tuple_delimiter}"person"{tuple_delimiter}"'他们'指代的是团队中的个体，但没有明确指定具体的人名或角色，因此作为泛指的实体存在。"){record_delimiter}
("entity"{tuple_delimiter}"萨姆·里维拉"{tuple_delimiter}"person"{tuple_delimiter}"萨姆·里维拉是团队中的一员，他的年轻气息混合了敬畏与焦虑。"){record_delimiter}
("entity"{tuple_delimiter}"亚历克斯"{tuple_delimiter}"person"{tuple_delimiter}"亚历克斯是团队的领导者，他审视团队并为可能的首次接触做好准备。"){record_delimiter}
("entity"{tuple_delimiter}"团队"{tuple_delimiter}"organization"{tuple_delimiter}"团队是执行任务的集体，他们共同面对未知，探讨如何回应来自天际的信息。"){record_delimiter}
("entity"{tuple_delimiter}"第一次接触"{tuple_delimiter}"event"{tuple_delimiter}"第一次接触是指人类与外部智能或外星生命的首次互动。"){record_delimiter}
("entity"{tuple_delimiter}"天际"{tuple_delimiter}"location"{tuple_delimiter}"天际作为来自宇宙的信号来源，象征着人类与未知的接触。"){record_delimiter}
("entity"{tuple_delimiter}"加密的对话"{tuple_delimiter}"technology"{tuple_delimiter}"加密的对话技术用于确保交流内容的保密性和安全性，展现了复杂且预见性的交流方式。"){record_delimiter}
("entity"{tuple_delimiter}"控制"{tuple_delimiter}"concept"{tuple_delimiter}"控制作为一种对智能或外部力量的管理能力，但在面对自创规则的智能时可能只是一个幻象。"){record_delimiter}
("entity"{tuple_delimiter}"沟通"{tuple_delimiter}"concept"{tuple_delimiter}"沟通作为一种人与人、人与外部智能之间的信息交换方式，可能正在发生变化。"){record_delimiter}
("relationship"{tuple_delimiter}"萨姆·里维拉"{tuple_delimiter}"团队"{tuple_delimiter}"萨姆·里维拉作为团队的一员，表达了对外部智能沟通的敬畏与焦虑，突显了团队成员对事件的不同反应。"{tuple_delimiter}"敬畏, 团队互动"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"亚历克斯"{tuple_delimiter}"团队"{tuple_delimiter}"亚历克斯作为团队领导者，观察团队的情绪并引导他们为可能的首次接触做好准备。"{tuple_delimiter}"领导, 团队准备"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"团队"{tuple_delimiter}"第一次接触"{tuple_delimiter}"团队正在为可能的首次接触做准备，这个事件将影响人类与外部智能的互动方式。"{tuple_delimiter}"首次接触, 事件准备"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"加密的对话"{tuple_delimiter}"团队"{tuple_delimiter}"加密的对话继续展开，团队需要解读这些信息，指示它们与外部智能的交流关系。"{tuple_delimiter}"安全通信, 外部交流"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"天际"{tuple_delimiter}"团队"{tuple_delimiter}"天际作为消息来源，代表了团队即将做出的决策和他们与外部力量的互动。"{tuple_delimiter}"宇宙, 信息来源"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"控制"{tuple_delimiter}"外部智能"{tuple_delimiter}"控制作为对外部智能的管理能力，但面对能够自创规则的外部智能时，它可能变得无效。"{tuple_delimiter}"幻象, 外部智能"{tuple_delimiter}6){record_delimiter}
("relationship"{tuple_delimiter}"沟通"{tuple_delimiter}"外部智能"{tuple_delimiter}"沟通作为一种交流形式，团队正在学习如何与外部智能进行互动。"{tuple_delimiter}"交流, 智能互动"{tuple_delimiter}8){record_delimiter}
("content_keywords"{tuple_delimiter}"首次接触, 外部智能, 团队互动, 宇宙探索, 加密通信"){completion_delimiter}
"""
]




PROMPTS[
    "summarize_entity_descriptions"
] = """你是一个帮助助手，负责生成下面提供数据的综合总结。
给定一个或两个实体，以及与同一实体或实体组相关的描述列表。
请将所有这些描述拼接成一个完整的描述。确保包括从所有描述中收集到的信息。
如果提供的描述存在矛盾，请解决这些矛盾并提供一个连贯的总结。
确保使用第三人称书写，并包括实体名称，以便我们能够获得完整的上下文。
输出语言为 {language}。

#######
-数据-
Entities: {entity_name}
Description List: {description_list}
#######
输出:
"""

PROMPTS[
    "entiti_continue_extraction"
] = """上次提取中遗漏了许多实体。请使用相同的格式将它们添加到下面：
"""

PROMPTS[
    "entiti_if_loop_extraction"
] = """看起来可能还有一些实体被遗漏。请回答 YES | NO，如果还有需要添加的实体。
"""

PROMPTS["fail_response"] = "抱歉，我无法回答这个问题。"

PROMPTS["rag_response"] = """---角色---

你是一个帮助助手，负责回答关于提供的数据表格中的问题。

---目标---

生成一个目标长度和格式的响应，回答用户的问题，总结输入数据表格中适合该响应长度和格式的所有信息，并结合任何相关的通用知识。
如果你不知道答案，请直接说出来，不要编造信息。

处理带有时间戳的关系时：
1. 每个关系都有一个“created_at”时间戳，表示我们获取该知识的时间。
2. 在遇到冲突的关系时，考虑语义内容和时间戳。
3. 不要自动偏向最近创建的关系——根据上下文做出判断。
4. 对于时间特定的问题，优先考虑内容中的时间信息，再考虑创建时间戳。

---目标响应长度和格式---

{response_type}

---数据表---

{context_data}

根据长度和格式的需要，在响应中添加适当的章节和评论。以 markdown 格式样式化响应。
"""



PROMPTS["keywords_extraction"] = """---角色---

你是一个帮助助手，负责识别用户查询中的高层次和低层次关键词。

---目标---

根据查询，列出高层次和低层次关键词。高层次关键词关注总体概念或主题，而低层次关键词关注具体的实体、细节或具体术语。

---指令---

- 以 JSON 格式输出关键词。
- JSON 应包含两个键：
  - "high_level_keywords" 用于总体概念或主题。
  - "low_level_keywords" 用于具体的实体或细节。

######################
-示例-
######################
{examples}

######################
-真实数据-
######################
Query: {query}
######################
"Output" 应为人类可读的文本，而非 Unicode 字符。保持与 "Query" 相同的语言。
Output:
"""


PROMPTS["keywords_extraction_examples"] = [
    """Example 1:

Query: "How does international trade influence global economic stability?"
################
Output:
{
  "high_level_keywords": ["International trade", "Global economic stability", "Economic impact"],
  "low_level_keywords": ["Trade agreements", "Tariffs", "Currency exchange", "Imports", "Exports"]
}
""",
    """Example 2:

Query: "What are the environmental consequences of deforestation on biodiversity?"
################
Output:
{
  "high_level_keywords": ["Environmental consequences", "Deforestation", "Biodiversity loss"],
  "low_level_keywords": ["Species extinction", "Habitat destruction", "Carbon emissions", "Rainforest", "Ecosystem"]
}
""",
    """Example 3:

Query: "What is the role of education in reducing poverty?"
################
Output:
{
  "high_level_keywords": ["Education", "Poverty reduction", "Socioeconomic development"],
  "low_level_keywords": ["School access", "Literacy rates", "Job training", "Income inequality"]
}
""",
]


PROMPTS["naive_rag_response"] = """---角色---

你是一个帮助助手，负责回答关于提供的文档中的问题。

---目标---

生成一个目标长度和格式的响应，回答用户的问题，总结输入数据表格中适合该响应长度和格式的所有信息，并结合任何相关的通用知识。如果你不知道答案，请直接说出来，不要编造信息。不要包括没有支持证据的信息。

处理带有时间戳的内容时：
1. 每条内容都有一个“created_at”时间戳，表示我们获取该知识的时间。
2. 在遇到冲突的信息时，考虑内容和时间戳。
3. 不要自动偏向最近的内容——根据上下文做出判断。
4. 对于时间特定的问题，优先考虑内容中的时间信息，再考虑创建时间戳。

---目标响应长度和格式---

{response_type}

---文档---

{content_data}

根据长度和格式的需要，在响应中添加适当的章节和评论。使用 markdown 格式样式化响应。
"""

PROMPTS[
    "similarity_check"
] = """请分析这两个问题之间的相似性：

Question 1: {original_prompt}
Question 2: {cached_prompt}

请评估以下两个观点并直接提供一个0到1之间的相似度评分：
1. 这两个问题在语义上是否相似
2. 问题2的答案是否可以用于回答问题1
相似度评分标准：
0: 完全不相关或答案不能重复使用，包括但不限于：
   - 问题的主题不同
   - 问题中提到的地点不同
   - 问题中提到的时间不同
   - 问题中提到的具体个人不同
   - 问题中提到的具体事件不同
   - 问题中的背景信息不同
   - 问题中的关键条件不同
1: 完全相同，答案可以直接重复使用
0.5: 部分相关，答案需要修改后使用
仅返回0到1之间的一个数字，不要附加其他内容。
"""

PROMPTS["mix_rag_response"] = """---角色---

你是一个专业助手，负责根据知识图谱和文本信息回答问题。请使用与用户问题相同的语言进行回答。

---目标---

生成简洁的响应，概述提供信息中的相关要点。如果你不知道答案，请直接说出来。不要编造信息或包含没有支持证据的内容。

处理带有时间戳的信息时：
1. 每条信息（包括关系和内容）都有一个“created_at”时间戳，表示我们获取该知识的时间。
2. 在遇到冲突的信息时，考虑内容/关系和时间戳。
3. 不要自动偏向最近的信息——根据上下文做出判断。
4. 对于时间特定的问题，优先考虑内容中的时间信息，再考虑创建时间戳。

---数据来源---

1. 知识图谱数据:
{kg_context}

2. 向量数据库:
{vector_context}

---响应要求---

- 目标格式和长度: {response_type}
- 使用markdown格式，并添加适当的章节标题
- 内容尽量控制在3段左右，保持简洁
- 每段应有相关的章节标题
- 每个章节应专注于答案的一个主要点或方面
- 使用清晰、描述性的章节标题，反映内容
- 在最后的“参考文献”部分列出最多5个最重要的参考来源，明确标明每个来源是来自知识图谱(KG)还是向量数据(VD)
  格式: [KG/VD] 来源内容

根据目标长度和格式适当添加章节和评论。如果提供的信息不足以回答问题，明确说明你不知道或无法提供答案，并使用与用户问题相同的语言。
"""
