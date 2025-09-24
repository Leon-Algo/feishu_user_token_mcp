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

通过遵循以上步骤，应该能够成功启动 Smithery playground 并进行开发测试。