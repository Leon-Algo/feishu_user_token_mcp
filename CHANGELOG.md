# 变更日志

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