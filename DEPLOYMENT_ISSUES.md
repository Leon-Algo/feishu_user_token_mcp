# Smithery 部署问题记录 (2025-09-24)

本文档记录了在将 Feishu Token MCP 服务器部署到 Smithery 平台时遇到的具体问题和解决方案。

## 时间线

### 2025-09-24 22:45 - Docker 构建失败

**问题日志：**
```
22:45:21.023 Building Docker image...
22:45:37.642 #15 0.843   × Failed to build `feishu-token-mcp @ file:///app`
22:45:37.998 #15 0.843   ├─▶ The build backend returned an error
22:45:38.355 #15 0.843   ╰─▶ Call to `setuptools.build_meta.build_editable` failed (exit status: 1)
22:45:40.236 #15 0.843       toml section missing PosixPath('pyproject.toml') does not contain a tool.setuptools_scm section
22:45:41.346 #15 0.843       SetuptoolsWarning: File '/app/README.md' cannot be found
22:45:42.468 #15 0.843       SetuptoolsDeprecationWarning: `project.license` as a TOML table is deprecated
22:45:51.174 #15 0.843       error: error in 'egg_base' option: 'src' does not exist or is not a directory
```

**根本原因：**
1. `.dockerignore` 文件排除了 `README.md`，但 `pyproject.toml` 引用了它
2. `pyproject.toml` 中使用了已弃用的许可证表格格式
3. 包含了 `setuptools-scm` 依赖但没有相应配置
4. Docker 构建时在复制源码前就尝试安装包

### 2025-09-24 23:04 - ASGI 应用程序错误

**问题日志：**
```
23:04:40.353 [server] TypeError: 'SmitheryFastMCP' object is not callable
23:04:40.698 [server]   File "/app/.venv/lib/python3.12/site-packages/uvicorn/middleware/asgi2.py", line 14, in __call__
23:04:43.487 [server]                ^^^^^^^^^^^^^^^
```

**根本原因：**
- `create_server()` 返回的是 `SmitheryFastMCP` 对象
- uvicorn 期望的是可调用的 ASGI 应用程序
- 需要使用 `server._fastmcp.streamable_http_app` 属性

## 修复过程

### 步骤1：修复 Docker 构建配置

#### 1.1 更新 `.dockerignore`
```diff
# Documentation (keep README.md as it's referenced in pyproject.toml)
- README.md
CHANGELOG.md
debug.md
PATH_debug.md
AGENTS.md
```

#### 1.2 修复 `pyproject.toml`
```diff
[build-system]
- requires = ["setuptools>=45", "wheel", "setuptools-scm[toml]>=6.2"]
+ requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "feishu-token-mcp"
version = "1.0.0"
description = "A Model Context Protocol server for managing and automatically refreshing Feishu app and user access tokens"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
readme = "README.md"
- license = {text = "MIT"}
+ license = "MIT"
requires-python = ">=3.12"
```

#### 1.3 优化 Dockerfile
```diff
# Use Python 3.12 slim base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv for faster dependency management
RUN pip install uv

# Copy project files
COPY . .

# Install dependencies and the package
RUN uv sync --frozen --no-dev
```

**验证结果：**
- ✅ `uv sync` 成功
- ✅ 包构建成功
- ✅ 服务器导入正常

### 步骤2：修复 ASGI 应用程序配置

#### 2.1 分析对象结构
```bash
uv run python -c "from feishu_token_mcp.server import create_server; server = create_server(); print('FastMCP type:', type(server._fastmcp)); print('streamable_http_app type:', type(server._fastmcp.streamable_http_app)); print('streamable_http_app callable:', callable(server._fastmcp.streamable_http_app))"
```

输出：
```
FastMCP type: <class 'mcp.server.fastmcp.server.FastMCP'>
streamable_http_app type: <class 'function'>
streamable_http_app callable: True
```

#### 2.2 修复 Dockerfile 启动脚本
```diff
# Create startup script that starts the MCP server
RUN echo '#!/bin/bash\nset -e\nPORT=${PORT:-8080}\necho "Starting Feishu Token MCP server on port $PORT"\n
- exec uv run python -c "from feishu_token_mcp.server import create_server; import uvicorn; server = create_server(); uvicorn.run(server, host=\\"0.0.0.0\\", port=int(\\"$PORT\\"))"' > /app/start.sh && \
+ exec uv run python -c "from feishu_token_mcp.server import create_server; import uvicorn; server = create_server(); app = server._fastmcp.streamable_http_app; uvicorn.run(app, host=\\"0.0.0.0\\", port=int(\\"$PORT\\"))"' > /app/start.sh && \
    chmod +x /app/start.sh
```

**验证结果：**
- ✅ 本地服务器启动成功
- ✅ Docker 构建成功
- ✅ Docker 容器运行正常
- ✅ StreamableHTTP 会话管理器启动

## 最终验证

### 本地测试
```bash
# 1. 依赖同步
uv sync
# Result: ✅ 41 packages resolved, feishu-token-mcp built successfully

# 2. 服务器创建测试
uv run python -c "from feishu_token_mcp import create_server; print('Server created successfully!')"
# Result: ✅ Server created successfully!

# 3. ASGI 应用验证
uv run python -c "from feishu_token_mcp.server import create_server; server = create_server(); print('streamable_http_app callable:', callable(server._fastmcp.streamable_http_app))"
# Result: ✅ streamable_http_app callable: True

# 4. 本地服务器启动
uv run python -c "from feishu_token_mcp.server import create_server; import uvicorn; server = create_server(); app = server._fastmcp.streamable_http_app; uvicorn.run(app, host='0.0.0.0', port=8082)"
# Result: ✅ Server running on http://0.0.0.0:8082, StreamableHTTP session manager started
```

### Docker 测试
```bash
# 1. Docker 构建
docker build -t feishu-token-mcp-test .
# Result: ✅ Build successful in 7.2s

# 2. Docker 运行
docker run -d -p 8083:8080 --name feishu-test-fixed -e PORT=8080 feishu-token-mcp-test
# Result: ✅ Container started successfully

# 3. 容器日志检查
docker logs feishu-test-fixed
# Result: ✅ StreamableHTTP session manager started, Uvicorn running on http://0.0.0.0:8080
```

## 关键经验总结

### 1. Docker 构建问题
- **教训**：`.dockerignore` 和 `pyproject.toml` 必须保持一致
- **最佳实践**：使用现代的 `pyproject.toml` 格式，避免已弃用的配置

### 2. Smithery/FastMCP 集成问题
- **教训**：`SmitheryFastMCP` 不是直接的 ASGI 应用，需要访问内部属性
- **最佳实践**：使用 `server._fastmcp.streamable_http_app` 作为 ASGI 应用

### 3. 调试方法
- **有效工具**：使用 Python 一行命令进行快速对象结构分析
- **验证流程**：本地 → Docker 构建 → Docker 运行 → 远程部署

### 4. 部署流程
1. 本地开发和测试 ✅
2. 修复配置问题 ✅ 
3. Docker 构建验证 ✅
4. Docker 运行测试 ✅
5. 推送到 GitHub ⏳
6. Smithery 平台部署 ⏳
7. 配置测试凭证 ⏳

## 后续行动项

- [ ] 推送修复后的代码到 GitHub
- [ ] 在 Smithery 平台重新部署
- [ ] 配置测试 profile 与飞书凭证
- [ ] 验证 MCP 工具扫描功能
- [ ] 更新项目文档

## 相关文件修改记录

- ✅ `.dockerignore` - 移除 README.md 排除
- ✅ `pyproject.toml` - 修复许可证格式，移除 setuptools-scm
- ✅ `Dockerfile` - 优化构建流程，修复 ASGI 应用启动
- ✅ `debug.md` - 添加详细故障排查指南
- ✅ `README.md` - 添加故障排查章节链接