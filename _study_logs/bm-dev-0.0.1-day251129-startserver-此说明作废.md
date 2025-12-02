## 分支 / 工作说明

学习 rag 搭建原理。代码倒是其次。

### _todo list_

- [x] ~~【完成】目前新增了 launch json，但是没用。这个项目好像是模块化直接部署。不是一个脚本。这是这个项目的特点，因此需要模块化启动~~


## 服务入口

### _直接基于命令启动服务_

- 服务部署对话总： https://deepwiki.com/search/_3b6b1aeb-60d2-4029-a8a9-c11a22746a8f?mode=fast

    服务启动说明 https://deepwiki.com/search/_3b6b1aeb-60d2-4029-a8a9-c11a22746a8f?mode=fast#2

    ```shell
    # 方式1：源码启动  
    cd /app/LightRAG  
    python -m lightrag.api.lightrag_server  
    
    # 方式2：开发模式（支持热重载）  
    cd /app/LightRAG  
    uvicorn lightrag.api.lightrag_server:app --reload --host 0.0.0.0 --port 9621

    # 方式3
    cd /app
    uv run lightrag-server
    ```

### _debug 方式运行服务_

- _https://deepwiki.com/search/_3b6b1aeb-60d2-4029-a8a9-c11a22746a8f?mode=fast#9_

    使用对话中的方案一启动服务，但是只能启动后端服务

        - http://localhost:9621/docs#/
        - http://localhost:9621/health
        - ReDoc：/redoc

- _launch 中也配置了前后端可以一起打开的方式_

    此方式 http://localhost:9621/webui/#/  也可以打开

    这个项目的后端为前端提供静态文件以及其他功能。这里有解释说明：https://deepwiki.com/search/_3b6b1aeb-60d2-4029-a8a9-c11a22746a8f?mode=fast#15

- 单独的前段启动命令

    https://deepwiki.com/search/_3b6b1aeb-60d2-4029-a8a9-c11a22746a8f?mode=fast#19 中的方式一

    单独启动的前端开发服务器可以调用单独启动的后端 API 服务器；

- 总结前后端单独启动的命令

    https://deepwiki.com/search/_3b6b1aeb-60d2-4029-a8a9-c11a22746a8f?mode=fast#21
    
