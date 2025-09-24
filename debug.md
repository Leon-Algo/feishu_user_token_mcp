# 解决 Smithery Playground 启动问题指南

## 问题描述

在 Windows 系统中，尽管已经安装了 Node.js，但在运行 `uv run playground` 时仍然出现以下错误：
```
✗ npx not found. Please install Node.js to use the playground
```

## 问题原因分析

1. **环境变量配置不正确**：Node.js 和 npm 路径未正确添加到系统 PATH 环境变量中
2. **权限问题**：npm 全局安装目录权限不足
3. **错误的包安装**：安装了错误的 smithery 包而非正确的 CLI 工具

## 解决方案步骤

### 1. 检查 Node.js 和 npm 安装

首先确认 Node.js 和 npm 是否正确安装：
```powershell
node --version
npm --version
```

### 2. 检查安装路径

查看 Node.js 和 npm 的安装路径：
```powershell
Get-Command node
Get-Command npm
Get-Command npx
```

### 3. 解决权限问题

如果遇到权限问题，更改 npm 的缓存和全局安装目录到用户目录：
```powershell
npm config set cache "C:\Users\你的用户名\AppData\Roaming\npm-cache"
npm config set prefix "C:\Users\你的用户名\AppData\Roaming\npm"
```

### 4. 安装正确的 Smithery CLI 工具

卸载可能存在的错误包并安装正确的 CLI 工具：
```powershell
npm uninstall -g smithery
npm install -g @smithery/cli
```

### 5. 更新环境变量

确保新的 npm 全局 bin 目录已添加到系统 PATH 环境变量中：
```powershell
$env:PATH += ";C:\Users\你的用户名\AppData\Roaming\npm"
```

### 6. 验证安装

检查 smithery CLI 是否正确安装：
```powershell
# 检查可执行文件是否存在
ls "C:\Users\你的用户名\AppData\Roaming\npm\node_modules\@smithery\cli\dist"
```

### 7. 启动 Playground

现在可以使用以下任一命令启动 playground：

方法一：使用 uv（推荐）
```powershell
uv run playground
```

方法二：使用 npx
```powershell
npx @smithery/cli playground
```

方法三：直接运行（如果上述方法仍不工作）
```powershell
node "C:\Users\你的用户名\AppData\Roaming\npm\node_modules\@smithery\cli\dist\index.js" playground --port 8081
```

## 常见问题和解决方案

### 问题1：权限错误
```
npm error code EPERM
```
**解决方案**：更改 npm 缓存和全局安装目录到用户目录（如步骤3所示）

### 问题2：找不到正确的 smithery 包
**解决方案**：确保安装的是 `@smithery/cli` 而不是 `smithery`

### 问题3：环境变量未更新
**解决方案**：手动将 npm 全局 bin 目录添加到 PATH 环境变量中

### 问题4：浏览器显示 "Connection Error - Failed to fetch"
**原因**：MCP 服务器未运行，playground 无法连接到本地服务器
**解决方案**：
1. 在第一个终端中启动 MCP 服务器：
   ```powershell
   uv run dev --port 8081
   ```
2. 在第二个终端中启动 playground：
   ```powershell
   npx @smithery/cli playground --port 8081
   ```
3. 确保两个进程同时运行，不要关闭任何一个
4. 在 playground 中配置会话参数（app_id, app_secret）

## 预防措施

1. 定期检查和更新环境变量配置
2. 使用用户目录作为 npm 全局安装目录以避免权限问题
3. 确保安装正确的 CLI 工具包
4. 定期更新 Node.js 和 npm 到最新稳定版本

## 参考命令

```powershell
# 检查已安装的全局包
npm list -g --depth=0

# 查看 npm 配置
npm config list

# 清理 npm 缓存
npm cache clean --force

# 检查 PATH 环境变量
echo $env:PATH
```

## 飞书 Token 管理相关

### 配置飞书应用凭证

1. 复制 `.env.example` 文件为 `.env`：
   ```bash
   cp .env.example .env
   ```

2. 在 `.env` 文件中填入你的飞书应用凭证：
   ```env
   FEISHU_APP_ID=your_app_id_here
   FEISHU_APP_SECRET=your_app_secret_here
   ```

### 测试 Token 获取功能

使用以下命令测试 Token 获取功能：
```bash
uv run python direct_test.py
```

### 在 Smithery Playground 中测试

运行以下命令启动 Smithery Playground：
```bash
uv run playground
```

在 Playground 中配置会话时，需要提供飞书应用凭证：
```json
{
  "app_id": "你的飞书 app_id",
  "app_secret": "你的飞书 app_secret"
}
```

### 核心功能测试

#### 1. 获取 App Token
在 Playground 中调用 `get_feishu_app_token` 工具来获取飞书应用访问令牌。

#### 2. 刷新 User Token
在 Playground 中调用 `refresh_feishu_user_token` 工具来刷新用户访问令牌，需要提供有效的刷新令牌作为参数。

### 二次开发指南

#### 1. 添加新的工具
在 `src/hello_server/server.py` 中添加新的工具函数，使用 `@server.tool()` 装饰器。

#### 2. 扩展配置模式
修改 `ConfigSchema` 类来添加新的配置选项。

#### 3. 增强 Token 管理功能
在 `FeishuTokenManager` 类中添加新的方法来处理其他类型的令牌或增加缓存机制。

#### 4. 改进错误处理
增强错误处理逻辑，提供更详细的错误信息和恢复机制。

通过遵循以上步骤，应该能够成功启动 Smithery playground 并进行开发测试。

---

# Smithery 远程部署问题解决指南

## 问题描述

在成功进行本地开发和测试后，部署到 Smithery 远程平台时遇到以下错误：

### 错误1：Docker 构建失败 - 包结构问题

```bash
× Failed to build `feishu-token-mcp @ file:///app`
├─▶ The build backend returned an error
╰─▶ Call to `setuptools.build_meta.build_editable` failed (exit status: 1)

[stderr]
SetuptoolsWarning: File '/app/README.md' cannot be found
SetuptoolsDeprecationWarning: `project.license` as a TOML table is deprecated
error: error in 'egg_base' option: 'src' does not exist or is not a directory
```

### 错误2：运行时 ASGI 应用程序错误

```bash
ERROR:    Exception in ASGI application
TypeError: 'SmitheryFastMCP' object is not callable
```

## 详细问题分析与解决方案

### 问题1：Docker 构建配置问题

#### 根本原因：
1. **`.dockerignore` 配置错误**：README.md 被排除，但 `pyproject.toml` 引用了它
2. **`pyproject.toml` 许可证格式问题**：使用了已弃用的表格格式
3. **setuptools-scm 配置缺失**：包含了依赖但缺少配置
4. **文件复制时序问题**：在复制源码前尝试构建包

#### 解决方案：

**1. 修复 `.dockerignore` 文件：**
```diff
# Documentation (keep README.md as it's referenced in pyproject.toml)
- README.md
CHANGELOG.md
debug.md
PATH_debug.md
AGENTS.md
```

**2. 修复 `pyproject.toml` 配置：**
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

**3. 优化 Dockerfile 结构：**
```dockerfile
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

### 问题2：ASGI 应用程序调用错误

#### 根本原因：
`SmitheryFastMCP` 对象本身不是可调用的 ASGI 应用程序。uvicorn 需要的是其内部的 `streamable_http_app` 属性。

#### 技术分析：
- `create_server()` 返回 `SmitheryFastMCP` 对象
- `SmitheryFastMCP` 包装了 `FastMCP` 实例 (`_fastmcp` 属性)
- `FastMCP` 实例有 `streamable_http_app` 属性，这才是真正的 ASGI 应用

#### 解决方案：

**修复 Dockerfile 中的启动脚本：**
```diff
# Create startup script that starts the MCP server
RUN echo '#!/bin/bash\nset -e\nPORT=${PORT:-8080}\necho "Starting Feishu Token MCP server on port $PORT"\n
- exec uv run python -c "from feishu_token_mcp.server import create_server; import uvicorn; server = create_server(); uvicorn.run(server, host=\\"0.0.0.0\\", port=int(\\"$PORT\\"))"' > /app/start.sh && \
+ exec uv run python -c "from feishu_token_mcp.server import create_server; import uvicorn; server = create_server(); app = server._fastmcp.streamable_http_app; uvicorn.run(app, host=\\"0.0.0.0\\", port=int(\\"$PORT\\"))"' > /app/start.sh && \
    chmod +x /app/start.sh
```

### 验证步骤

#### 1. 本地验证 ASGI 应用：
```bash
uv run python -c "from feishu_token_mcp.server import create_server; server = create_server(); print('streamable_http_app type:', type(server._fastmcp.streamable_http_app)); print('streamable_http_app callable:', callable(server._fastmcp.streamable_http_app))"
```

预期输出：
```
streamable_http_app type: <class 'function'>
streamable_http_app callable: True
```

#### 2. 本地 Docker 构建测试：
```bash
docker build -t feishu-token-mcp-test .
```

#### 3. 本地 Docker 运行测试：
```bash
docker run -d -p 8083:8080 --name feishu-test -e PORT=8080 feishu-token-mcp-test
docker logs feishu-test
```

预期日志：
```
Starting Feishu Token MCP server on port 8080
WARNING:  ASGI app factory detected. Using it, but please consider setting the --factory flag explicitly.
INFO:     Started server process [43]
INFO:     Waiting for application startup.
INFO:     StreamableHTTP session manager started
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

#### 4. 本地服务器功能测试：
```bash
uv run python -c "from feishu_token_mcp.server import create_server; import uvicorn; server = create_server(); app = server._fastmcp.streamable_http_app; uvicorn.run(app, host='0.0.0.0', port=8082)"
```

## 部署后的扫描失败问题

### 问题描述：
```
Scan Failed
Your deployment succeeded, but we couldn't connect to your server to scan for tools.
```

### 解决方案：
1. **配置测试配置文件**：在 Smithery 平台上设置测试配置，包含有效的 `app_id` 和 `app_secret`
2. **验证服务器响应**：确保服务器能正确响应 MCP 初始化请求

## 最佳实践总结

### 1. Docker 构建最佳实践：
- 确保 `.dockerignore` 不排除 `pyproject.toml` 引用的文件
- 使用现代的 `pyproject.toml` 配置格式
- 避免不必要的 setuptools 扩展依赖

### 2. Smithery/FastMCP 集成最佳实践：
- 使用 `server._fastmcp.streamable_http_app` 作为 ASGI 应用
- 确保正确处理 `SmitheryFastMCP` 对象结构
- 在 uvicorn 启动前验证 ASGI 应用的可调用性

### 3. 部署验证流程：
1. 本地构建和测试
2. 本地 Docker 构建验证
3. 本地 Docker 运行测试
4. 推送到远程仓库
5. 在 Smithery 平台部署
6. 配置测试凭证进行工具扫描

### 4. 故障排查工具：
```bash
# 检查对象结构
uv run python -c "from feishu_token_mcp.server import create_server; server = create_server(); print(dir(server)); print(dir(server._fastmcp))"

# 验证 ASGI 应用
uv run python -c "from feishu_token_mcp.server import create_server; server = create_server(); app = server._fastmcp.streamable_http_app; print('Ready:', callable(app))"

# 本地包构建测试
uv sync
```

## 常见错误代码对照

| 错误类型 | 错误信息 | 解决方案编号 |
|---------|----------|--------------|
| Docker构建 | `'src' does not exist or is not a directory` | 修复 pyproject.toml + Dockerfile |
| Docker构建 | `File '/app/README.md' cannot be found` | 修复 .dockerignore |
| Docker构建 | `project.license` as a TOML table is deprecated` | 修复 pyproject.toml 许可证格式 |
| 运行时 | `'SmitheryFastMCP' object is not callable` | 使用 streamable_http_app |
| 扫描失败 | `couldn't connect to your server to scan for tools` | 配置测试凭证 |
| MCP工具执行 | `Failed to refresh app token: invalid param` | 添加参数验证和调试日志 |

## 问题 6: 生产环境 MCP 工具执行失败 (2025-09-25)

**现象:**
- 服务器成功部署到 Smithery 平台
- MCP 工具调用时返回错误: `Error executing tool get_feishu_app_token: Failed to get app token: Failed to refresh app token: invalid param`

**分析:**
1. 本地测试使用相同凭据成功获取 app token
2. 问题可能在于生产环境的参数传递或验证
3. 需要添加调试日志来诊断具体问题

**解决方案:**
1. **添加详细的调试日志和参数验证** - 在 `refresh_app_token` 方法中添加:
   - 参数空值检查和验证
   - 详细的请求和响应日志记录
   - 去除参数前后空格处理

2. **添加配置调试信息** - 在 MCP 工具中添加:
   - session_config 类型和值的调试输出
   - 参数传递状态的验证

**修复后的代码关键点:**
- 参数验证: 检查 app_id 和 app_secret 是否为空
- 去空格处理: 使用 `.strip()` 清理参数
- 详细日志: 记录请求URL、payload、响应状态和数据
- 错误信息增强: 提供更详细的错误码和消息

**测试验证:**
- 本地测试通过，成功获取 app token: `t-g1049p02ILAWXVG7AGRZYE7EFIQCSSAYUEG7HEGT`
- 需要重新部署到 Smithery 平台验证修复

通过遵循以上步骤和最佳实践，应该能够成功部署到 Smithery 远程平台并通过工具扫描。