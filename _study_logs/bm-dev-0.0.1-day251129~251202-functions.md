## 文件说明

记录此项目的功能以及特点;

以及在启动后端服务后，学习后端代码实现逻辑



## 代码细节

### 系统概述

系统结构以及优势：是我的产品特点（总）

https://deepwiki.com/search/-1-rag-2-3-rag-4-rag_af4b2520-5ce4-496c-8b45-7c768d37ff3c?mode=fast#1


### 基于 uvicorn +  fastapi 的 web server 搭建

- fastAPI https://gemini.google.com/app/8b675cc37a33be51

    - FastAPI 是一个用于使用 Python 构建 API（应用程序编程接口） 的现代、高性能的 Web 框架； 它是把一个服务封装成一个 API 供外部客户端调用的框架

        https://gemini.google.com/share/60d4b531f209

- GUNICORN 是一个进程管理器，可以启动多个 worker。 其和 uvicor 以及 fastapi 之间的关系 https://gemini.google.com/share/fc64e31cb37f

    Gunicorn 的多进程管理依赖 Uvicorn 作为 worker 进程，但单进程模式下可以不使用 Uvicorn。你可以直接运行 FastAPI app 或使用其他 ASGI 服务器。

- Uvicorn 和 fastapi app  之间是什么关系

    - uvicorn 具备 ssl 的配置能力

    - Uvicorn 是单进程服务器，不支持多进程
  
    - 那就是说，一般的实际开发中，一般都是定义好了 fastAPI，这个应用随时接收 uvicorn 发送进来的信息。

        因此 uvicorn 是独立存在的一个真正面向 user client 的 server

        相对于 uvicorn ，fastapi 的 app 是真正处理请求的 server （这意味着 Uvicorn 是“主动的”服务器，或者说它是 app 和 user 之间的一个中间件
            
        uvicorn 存在的意义在于：它定义了一套完善的处理 user requests 的标准， fastapi 就是按照这个标准形成的应用框架，fastapi 基于这个框架部署的 app，就可以接受  uvicorn 推送过来的 user requests

        当 app 准备好后， uvicorn 只需要通过 uvicorn main:app --reload 这样的命令格式，去找到对应的 app 即可

        - 参考资料  https://gemini.google.com/share/bb674d1f8624 + 3 round conversation

- 代码启动 web server 的入口在 main，main 的解释说明：

    https://deepwiki.com/search/-todo-main-fastapi-def-main-ex_c0a5b14d-5703-4ffb-b265-9b89496e7850?mode=fast



### 功能实现细节

#### 向量数据库模块

- Qdrant 向量数据库

    https://deepwiki.com/search/displaysplashscreen_f2969a66-afd6-40ee-a66b-05434aafc6ad?mode=fast#19


#### 面试问题入口

作为面试官，我会针对LightRAG的文档处理模块提出以下技术问题：

https://deepwiki.com/search/pdfoffice_baf08a33-8433-49a4-b97d-747392bfbbc0?mode=fast

#### 从产品特点出发，引出面试的第一个方向：文档处理模块

问题： LightRAG支持多种文档格式处理，请描述其文档处理的整体架构设计？特别是如何处理不同格式的文档以及处理流程是怎样的？

回答：https://deepwiki.com/search/lightrag_0c29743e-066b-4a40-8fb6-0c4663b0d9e3?mode=fast

textract支持的格式：通过textract库支持TXT、DOCX、PPTX、CSV、PDF等格式的解析。这个能力是如何实现的：https://deepwiki.com/search/textracttextracttxtdocxpptxcsv_77276a8c-afe4-42ac-a907-5e2e43927227?mode=fast （LightRAG的文档解析架构确实是以DOCLING为核心，辅以常规解析工具，并通过RAG-Anything集成多模态能力）

- 这里记录了文档的处理流程：

    - https://deepwiki.com/search/displaysplashscreen_f2969a66-afd6-40ee-a66b-05434aafc6ad?mode=fast#42

    - https://deepwiki.com/search/displaysplashscreen_f2969a66-afd6-40ee-a66b-05434aafc6ad?mode=fast#50

- _文档处理过程的问题 - 1：现在先说文本类型的文档解析。你是一个面试官，你问我再搭建rag时，碰到的文本处理困难有哪些，你是怎么解决的。我该如何根据这个项目回答这个问题_  https://deepwiki.com/search/textracttextracttxtdocxpptxcsv_77276a8c-afe4-42ac-a907-5e2e43927227?mode=fast#3

    - 针对每种格式开发特定的解析方法 - `lightrag/api/routers/document_routes.py` 支持的文档类型

    - PDF：LightRAG优先使用DOCLING解析PDF。系统会首先检查是否配置了DOCLING引擎且可用，如果满足条件就使用DOCLING，否则回退到pypdf

        - PDF 分为文本型和图像型号：docling + 外置 OCR 模型处理成 docling 可以处理的格式

    - python-docx/pptx/xlsx

    - 日志信息（这个项目中涉及到大量的日志信息以及日志文件的解析方法）

        - 营收日志文件：改价等操作

        - 水厂运行日志文件：加药等 / 分为好多系统模块

        - sass 平台问题：网关、代码等信息的解析

            - 代码结构查询：哪些类有哪些方法

            - 依赖关系查询：哪些函数调用了哪些 API

            - 快速定位功能代码片段，着重是用户验收使用：处理用户认证以及关键认证信息的功能定位；

- _文档处理过程的问题 - 2 - 搭建完善的多并发系统框架，处理资源并发和 LLM 调用机制的限制 / LLM调用优化困难_

    - track_id 是 LightRAG 为每个文档上传操作生成的唯一跟踪标识符，用于监控异步文档处理进度

        - 当文件上传完毕后，文档的提取等处理是自动展开的： lightrag/api/routers/document_routes.py： `background_tasks.add_task(pipeline_index_file, rag, file_path, track_id)`

            LightRAG 没有传统的回调机制。处理完成后。 更新文档状态为 PROCESSED， 客户端通过 /track_status/{track_id} 轮询状态(`lightrag/api/routers/document_routes.py`)

- _文档处理过程的问题 - 3 文本分块与上下文保持困难_

- _文档处理过程的问题 - 4 图谱相关：实体关系提取的复杂性_

- _文档处理过程的问题 - 5 错误处理与状态跟踪困难_


#### 多模态文档处理：通过 RAG-Anything 集成支持PDF、图片、Office文档、表格、公式等解析

这个能力是如何实现的 https://deepwiki.com/search/textracttextracttxtdocxpptxcsv_77276a8c-afe4-42ac-a907-5e2e43927227?mode=fast#2

- _多模态模型问题 - 1：多模态模型是调用的 openai 的多模态模型吗？ 如果面试官问你的多模态能力是是如何搭建的。我可以说我是基于本地训练的多模态模型吗？ 这个难度是不是太大，导致给自己挖坑，如果不这样子回到。我还有哪些有价值的方向说明我在多模态方向做了哪些有价值的工作：_ https://deepwiki.com/search/textracttextracttxtdocxpptxcsv_77276a8c-afe4-42ac-a907-5e2e43927227?mode=fast#4

    - 表格信息

        - 多模态加持

        - 结构化提取：将表格数据转换为可查询的知识图谱实体和关系

    - 数学公式

        - 多模态加持

        - ~~LaTeX支持：前端支持LaTeX公式的渲染和显示~~ 这是前端内容
