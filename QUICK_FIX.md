# 快速故障排查参考

本文档提供了常见问题的快速解决方案，便于快速定位和修复问题。

## 🚨 常见错误快速查找

### Docker 构建错误

#### `'src' does not exist or is not a directory`
**原因**: pyproject.toml 配置问题或文件复制时序错误  
**解决**: 检查 Dockerfile 文件复制顺序，确保在 `COPY . .` 之后再运行 `uv sync`

#### `File '/app/README.md' cannot be found`
**原因**: .dockerignore 排除了 pyproject.toml 引用的文件  
**解决**: 从 .dockerignore 中移除 README.md

#### `project.license` as a TOML table is deprecated
**原因**: 使用了已弃用的许可证格式  
**解决**: `license = {text = "MIT"}` → `license = "MIT"`

### 运行时错误

#### `'SmitheryFastMCP' object is not callable`
**原因**: 传递了错误的对象给 uvicorn  
**解决**: 使用 `server._fastmcp.streamable_http_app` 而非 `server`

#### `Scan Failed - couldn't connect to your server`
**原因**: Smithery 无法连接到服务器进行工具扫描  
**解决**: 配置测试 profile 并提供有效的 app_id 和 app_secret

## 🔧 快速修复命令

### 验证对象结构
```bash
uv run python -c "from feishu_token_mcp.server import create_server; server = create_server(); print('ASGI app callable:', callable(server._fastmcp.streamable_http_app))"
```

### 测试包构建
```bash
uv sync
```

### 测试服务器启动
```bash
uv run python -c "from feishu_token_mcp import create_server; print('Server OK')"
```

### Docker 快速测试
```bash
docker build -t test-build . && docker run -d -p 8080:8080 --name test-container -e PORT=8080 test-build && docker logs test-container
```

## 📋 检查清单

### 部署前检查
- [ ] `.dockerignore` 不排除 pyproject.toml 引用的文件
- [ ] `pyproject.toml` 使用现代格式（license = "MIT"）
- [ ] Dockerfile 使用正确的 ASGI 应用启动
- [ ] 本地 `uv sync` 成功
- [ ] 本地服务器启动正常

### Docker 验证
- [ ] Docker 构建成功
- [ ] Docker 容器启动无错误
- [ ] 容器日志显示 StreamableHTTP 管理器启动
- [ ] 服务器监听正确端口

### Smithery 部署
- [ ] GitHub 代码已推送
- [ ] Smithery 部署成功
- [ ] 配置了测试 profile
- [ ] 工具扫描通过

## 🔍 调试技巧

### 查看对象内部结构
```python
from feishu_token_mcp.server import create_server
server = create_server()
print("SmitheryFastMCP attributes:", dir(server))
print("FastMCP attributes:", dir(server._fastmcp))
print("ASGI app type:", type(server._fastmcp.streamable_http_app))
```

### 验证 MCP 协议兼容性
```python
# 检查是否返回正确的 ASGI 应用
app = server._fastmcp.streamable_http_app
print("Is callable:", callable(app))
print("Is function:", isinstance(app, type(lambda: None)))
```

## 📚 相关文档

- [debug.md](./debug.md) - 详细故障排查指南
- [DEPLOYMENT_ISSUES.md](./DEPLOYMENT_ISSUES.md) - 部署问题记录
- [README.md](./README.md) - 项目说明和使用方法

## ⚡ 紧急修复

如果遇到部署紧急问题，按以下顺序快速检查：

1. **检查 pyproject.toml**: `license = "MIT"` (不是表格格式)
2. **检查 .dockerignore**: README.md 不应被排除
3. **检查 Dockerfile**: 使用 `server._fastmcp.streamable_http_app`
4. **验证本地**: `uv sync && uv run python -c "from feishu_token_mcp import create_server; print('OK')"`
5. **Docker 测试**: `docker build -t test .`

遵循这个快速参考，应该能在几分钟内定位和修复大多数部署问题。