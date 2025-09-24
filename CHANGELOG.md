# 变更日志

## [1.0.1] - 2025-09-24

### 问题修复

#### Docker 部署问题修复
- **修复**: 修复了 `.dockerignore` 文件排除 `README.md` 导致的构建失败问题
- **修复**: 更新 `pyproject.toml` 中的许可证格式，从已弃用的表格格式改为字符串格式
- **修复**: 移除了 `setuptools-scm` 依赖，避免缺少配置导致的构建错误
- **优化**: 重新组织 Dockerfile 结构，优化构建缓存和文件复制顺序

#### ASGI 应用程序配置修复
- **修复**: 解决了 `TypeError: 'SmitheryFastMCP' object is not callable` 错误
- **技术细节**: 修复了启动脚本，使用 `server._fastmcp.streamable_http_app` 作为 ASGI 应用
- **验证**: 确保 ASGI 应用程序的可调用性，兼容 uvicorn 服务器

### 文档更新
- **新增**: 创建了 `DEPLOYMENT_ISSUES.md` 文档，详细记录部署问题和解决方案
- **更新**: 扩展了 `debug.md` 文档，添加了 Smithery 远程部署问题解决指南
- **更新**: 在 `README.md` 中添加了故障排查章节的链接

### 验证测试
- **本地测试**: ✅ 包构建和服务器启动正常
- **Docker 测试**: ✅ Docker 构建和容器运行成功
- **ASGI 验证**: ✅ StreamableHTTP 会话管理器正常启动

## [1.0.0] - 2025-09-24

### 新增功能

- 实现了飞书 App Access Token 的自动获取和刷新功能
- 实现了飞书 User Access Token 的刷新功能
- 创建了基于 Smithery 的 MCP 服务器
- 添加了会话配置支持，允许通过配置传递 `app_id` 和 `app_secret`
- 实现了环境变量支持，可以从 `.env` 文件加载配置
- 添加了完整的测试脚本集，包括直接测试和服务器测试

### 技术实现

- 使用 `@smithery.server` 装饰器创建 MCP 服务器
- 实现了 `FeishuTokenManager` 类来管理令牌的获取和刷新
- 添加了内存缓存机制来存储不同应用的令牌管理器实例
- 使用 `python-dotenv` 库来加载环境变量
- 使用 `requests` 库进行 HTTP 请求

### 文档更新

- 更新了 README.md，包含了完整的项目说明、使用方法和 API 参考
- 创建了 debug.md，提供了故障排查指南
- 添加了 `.env.example` 文件作为环境变量配置示例
- 创建了多个测试脚本，方便验证功能

### 依赖更新

- 添加了 `requests>=2.31.0` 依赖
- 添加了 `python-dotenv>=1.0.0` 依赖

## [0.1.0] - 2025-09-24

### 初始版本

- 基于 Smithery 模板创建项目
- 实现了基本的 MCP 服务器结构
- 添加了简单的 Hello World 工具示例