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