# 飞书 Access Token MCP

本项目是一个基于 [Smithery](https://smithery.ai/) 和 Python 构建的 MCP (Model-Context-Protocol) 服务，用于管理并自动刷新飞书的 `app_access_token` 和 `user_access_token`。

该服务将飞书的 Token 管理逻辑封装成一个 MCP 工具。客户端（如 AI Agent）可以通过配置会话（Session）并调用此工具，来获取一个有效的访问令牌，无需关心其内部的获取机制。

## 功能特性

- **MCP 服务化**：将 Token 管理封装为标准的 MCP 工具。
- **会话配置**：通过 MCP 会话安全地传递 `app_id` 和 `app_secret`。
- **自动刷新与状态管理**：在 `app_access_token` 过期前自动刷新。
- **用户 Token 刷新**：支持刷新 `user_access_token`。
- **Smithery 集成**：利用 `@smithery.server` 装饰器，轻松实现部署和会话管理。
- **环境变量支持**：支持从 `.env` 文件加载配置。

## 项目结构

```
feishu_user_token_mcp/
├── .env                 # 环境变量配置文件
├── .env.example         # 环境变量配置示例文件
├── .gitignore
├── README.md
├── debug.md             # 调试和故障排查指南
├── pyproject.toml       # Smithery 配置文件
├── smithery.yaml
├── simple_test.py       # 简单测试脚本
├── direct_test.py       # 直接测试脚本
├── test_server.py       # 服务器测试脚本
├── http_client_test.py  # HTTP 客户端测试脚本
├── check_env.py         # 环境变量检查脚本
└── src/
    └── hello_server/
        ├── __init__.py
        └── server.py    # MCP 服务器定义和核心逻辑
```

## 环境要求

- Python 3.12 (通过 uv 管理)
- 已通过 uv 固定解释器版本

## 安装与设置

1. **克隆仓库：**
   ```bash
   git clone <your-repo-url>
   cd feishu_user_token_mcp
   ```

2. **配置环境变量：**
   复制 `.env.example` 文件并重命名为 `.env`，然后添加您的飞书应用凭证：
   ```bash
   cp .env.example .env
   ```
   
   编辑 `.env` 文件：
   ```env
   FEISHU_APP_ID=your_app_id
   FEISHU_APP_SECRET=your_app_secret
   ```

3. **安装 `uv` (如果尚未安装):**
   这是一个高效的 Python 包管理器。
   ```bash
   pip install uv
   ```

4. **创建虚拟环境并安装依赖：**
   `uv` 会自动创建虚拟环境并安装项目依赖。
   ```bash
   uv sync
   ```

## 核心功能

### 1. 获取飞书 App Token

通过 `get_feishu_app_token` 工具获取有效的飞书应用访问令牌。该工具会自动处理令牌的刷新。

### 2. 刷新飞书 User Token

通过 `refresh_feishu_user_token` 工具使用刷新令牌获取新的用户访问令牌。

## 如何运行和测试

### 1. 检查环境变量配置

使用以下命令测试环境变量配置：
```bash
uv run python check_env.py
```

### 2. 直接测试 Token 管理功能

使用以下命令直接测试核心 Token 管理功能：
```bash
uv run python direct_test.py
```

### 3. 本地开发运行

使用以下命令启动本地开发服务器：
```bash
uv run dev
```

服务器将在 `http://127.0.0.1:8081` 上运行。

### 4. 在 Smithery Playground 中测试

为了方便地测试 MCP 服务，您可以使用 Smithery Playground。它提供了一个图形界面来配置会话和调用工具。

运行以下命令：
```bash
uv run playground
```

或者直接使用：
```bash
npx @smithery/cli playground --port 8081
```

此命令会将您的本地服务器通过 `ngrok` 安全地连接到 Smithery Playground。您会得到一个 URL，在浏览器中打开它即可开始测试。

**在 Playground 中的测试步骤：**

1. **配置会话 (Configure Session)**：
   在 Playground 页面的 "Session Config" 部分，填入您的飞书应用凭证：
   ```json
   {
     "app_id": "你的飞书 app_id",
     "app_secret": "你的飞书 app_secret"
   }
   ```
2. **调用工具**：
   在聊天框中，输入指令来调用我们定义的工具，例如：
   > "获取飞书 app token"

   或者

   > "Call the get_feishu_app_token tool"
   
   要测试用户 token 刷新功能：
   > "刷新用户 token"

3. **查看结果**：
   模型会调用相应的工具，您将在界面上看到返回的结果。

## 用于生产环境

此 MVP (最小可行产品) 实现使用内存中的字典来存储不同会话的 `TokenManager` 实例。这对于开发和大多数场景是足够的，但请注意：

- **重启后状态丢失**：如果应用程序重启，所有会话的令牌信息都将丢失，下次调用时会重新初始化。
- **扩展性**：如果需要部署到多个实例（例如，使用负载均衡），内存缓存将导致状态不一致。

对于需要跨实例共享状态或在重启后保留状态的生产环境，建议将 `token_manager_cache` 替换为外部的持久化存储，例如：
- **Redis**：一个快速的内存数据存储，非常适合缓存令牌。
- **数据库**：如 PostgreSQL 或 MySQL。

## 故障排查

如果在开发或部署过程中遇到问题，请查看 [debug.md](./debug.md) 文件，其中包含了详细的故障排查指南，包括：

- Smithery Playground 启动问题
- Docker 构建和部署问题
- ASGI 应用程序配置问题
- 远程部署到 Smithery 平台的常见问题

## 部署到 Smithery

准备好部署了吗？将您的代码推送到 GitHub 并部署到 Smithery：

1. 在 [github.com/new](https://github.com/new) 创建一个新的仓库

2. 初始化 git 并推送到 GitHub：
   ```bash
   git add .
   git commit -m "Initial commit: Feishu Access Token Manager"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

3. 在 [smithery.ai/new](https://smithery.ai/new) 部署您的服务器

## API 参考

### get_feishu_app_token

获取有效的飞书应用访问令牌。

**参数：**
- 无显式参数，从会话配置中获取 `app_id` 和 `app_secret`

**返回值：**
```json
{
  "app_access_token": "t-g1049oiTYL4Q23JHXCL4DST4ICYXMQC42V6JY57Y",
  "expires_at": 1758718220.6939602
}
```

### refresh_feishu_user_token

使用刷新令牌获取新的用户访问令牌。

**参数：**
- `refresh_token` (string): 用于刷新用户令牌的刷新令牌

**返回值：**
```json
{
  "access_token": "u-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "refresh_token": "ur-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "expires_in": 7200,
  "token_type": "Bearer",
  "scope": "contact:user.base:readonly"
}
```