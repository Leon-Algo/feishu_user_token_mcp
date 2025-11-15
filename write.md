> 从手动改表格到自动续命：我是如何从 0 写出一个 Feishu Token MCP，并把它丢到 Smithery 远程平台的

---

## 一、故事从哪儿开始：两小时就会死一次的 Token

先说结论：这篇文章不是在教你怎么写「完美」的后端服务，而是复盘我作为一个 MCP 新手，怎么在一堆报错和困惑里，一步步把一个**自动刷新飞书应用 Token 的 MCP 服务**，从本地一路折腾到 Smithery 远程平台上线可用的全过程。

### 1.1 传统做法有多烦

在这个项目之前，我的世界是这样的：

- 有一张「多维表格」专门存各种配置，其中就包括飞书应用的 app token；
- 飞书的规则是：这个 token 只有大概两小时的有效期；
- 两小时一过，所有依赖这个 token 的自动化流程就会开始随机翻车；
- 然后就需要人工去飞书开放平台/接口拿新的 token，再手动更新表格。

这套流程最大的特征就是：

- 枯燥、重复、容易忘；
- 一旦忘了，问题不会立刻爆炸，而是默默地以「为什么今天没跑」的形式出现。

> （截图建议：
> 图 1：多维表格中存放 token 的界面，打码关键信息，只展示「我们曾经手动维护 token」这件事。）

### 1.2 我理想中的世界

我真正想要的是：

- 有一个标准化的「服务」或者「工具」，对外提供一个非常明确的能力：
	- 输入：飞书的 `app_id` + `app_secret`；
	- 输出：一个当前可用的 `app_access_token`；
	- 内部逻辑：如果原来的 token 还没过期，就直接复用；如果过期，就自动去飞书刷新。

然后，把这个能力封装成一个 **MCP 工具**：

- 任何支持 MCP 的 Agent / 客户端，都可以：
	- 主动调用「获取 Feishu app token」这个工具；
	- 甚至可以根据调用结果自己判断 token 是否过期、何时需要刷新；
	- 我作为人类不再背锅「记不住什么时候得去更新 token」。

这篇文章讲的，就是我从 0 开始，如何把这件事实现出来的整个过程——包括所有踩过的坑和心态上的变化。

---

## 0x00 预告：这不是「一键成功」的教程，而是一串非常真实的坑

在正式进入时间线之前，先把这篇文章会涵盖的「坑的范围」打个预防针，因为这跟普通的「MCP 快速上手」完全不是一个量级：

- **环境层面的坑**：
	- Node.js 明明装了，`uv run playground` 一直疯狂说：`✗ npx not found. Please install Node.js to use the playground`；
	- npm 全局目录权限问题，各种 `EPERM`、`EACCES` 让人怀疑人生；
	- 安装错包：装了 `smithery`，结果官方推荐的是 `@smithery/cli`；
	- Windows 下 PATH 和 PowerShell 行为和文档里的「一行命令搞定」完全不是一个世界。
- **工具链理解层面的坑**：
	- Vibe Coding / AI 助手给出的 Smithery 配置建议和官方最新文档不一致；
	- 一堆看起来「理所当然」的 Dockerfile 模板，最后都在云端构建阶段报错；
	- MCP 协议里的 `Accept: application/json, text/event-stream`、session id 这些细节，文档一笔带过，但实际不对就直接 406 / 400。
- **部署与运行时的坑**：
	- Docker 构建阶段各种 `src does not exist`、`README.md cannot be found`；
	- ASGI 启动时的 `'SmitheryFastMCP' object is not callable`；
	- Smithery 平台提示：`Scan Failed - couldn't connect to your server`；
	- 远程环境中工具执行失败：`Failed to refresh app token: invalid param`。

更要命的是：这些坑不是线性的，而是「交叉叠加」的：

- 当时我既不熟 MCP，又刚接触 Smithery，再加上 Windows + Node/npm 环境的一些历史包袱；
- 再叠加上 AI 工具对老版本文档的误引用，很多建议看起来「很对」，实际一跑就错。

所以这篇文章的目标不是演示「完美路径」，而是把那条真实的、充满回头路和反复试错的轨迹全部摊开：

- 你可以走一条更短的路；
- 也可以在踩到类似坑的时候，有一份「原来不是只有我一个人这样」的参考手册。

## 二、第一次听说 MCP：把「刷 token」变成一个标准工具

### 2.1 MCP 在我脑子里的初始印象

刚接触 MCP 的时候，我的理解非常粗糙，大概只有几条：

- MCP 是一种协议，规定「模型」怎么跟「外部工具」交互；
- 工具不是随便乱来的，而是有：
	- 名字；
	- 参数列表（需要什么输入字段）；
	- 返回结构（输出里有什么字段）；
- 一旦写成 MCP 格式，很多客户端（比如 Smithery、一些 IDE、未来的 Agent 平台）就可以自动发现这些工具，甚至自动生成调用界面。

> （截图建议：
> 图 2：一张简单的架构示意图，可以画成「LLM ↔ MCP Server ↔ Feishu API」三层结构。）

### 2.2 技术选型：为什么是 Python + Smithery

这一部分我完全从自己的习惯出发：

- 语言用 Python：
	- 写起来快，调试方便；
	- requests 之类的网络库很顺手；
- MCP 实现用 Smithery 的 FastMCP：
	- 有现成的 Python 脚手架；
	- 自带 dev / playground / 部署链路；
- 部署平台选 Smithery：
	- 我只需要把服务做成一个容器就行，平台会帮我托管和暴露 MCP；
	- 省去了自己整一套 K8s 或服务器的精力。

可以理解为：**我不想从头造轮子，我只是想把「飞书 token 刷新」变成一个任何 Agent 都能用的标准工具**。

---

## 三、本地从 0 起步：先让「刷 token」在命令行里跑起来

在真正碰 MCP 之前，我给自己定了一个非常朴素的目标：

> 先不管协议、容器、部署，先在本地纯 Python 里把「拿 Feishu app token」这件事做对。

### 3.1 初始化项目和环境：从「以为装好了」到「真的能用」

这一段看起来很基础，但实际上我在这里就已经摔了好几跤，而且很多坑一开始甚至没意识到是坑——只觉得「怎么总是不按官方文档走呢」。

1. 准备一个干净的项目目录，比如 `feishu_user_token_mcp`；
2. 用 smithery 的 Python MCP 模板初始化项目（或者参考官方示例抄一个骨架）；
3. 确认几个关键文件存在：
	 - `pyproject.toml`：Python 项目配置；
	 - `smithery.yaml`：告诉 Smithery 这个 MCP 要怎么跑；
	 - `src/feishu_token_mcp/server.py`：我们的主角 MCP Server；
4. 创建虚拟环境，安装依赖：
	 - MCP / FastMCP
	 - Smithery
	 - requests
	 - pydantic
	 - python-dotenv 等。

到这里，**表面上看一切正常**：Python 能跑、`uv sync` 通过，项目结构也都在。但问题真正开始暴露，是当我第一次想「按照官方推荐」启动 Playground 的时候。

### 3.2 NPM / npx / smithery CLI：第一次感觉「文档在另一个宇宙」

官方文档通常会写一句非常轻松的话：

> 运行 `uv run playground` 或 `npx @smithery/cli playground` 即可。

在我的 Windows 环境里，现实长这样：

```text
✗ npx not found. Please install Node.js to use the playground
```

问题是——我**明明已经安装了 Node.js**，在 PowerShell 里跑：

```powershell
node --version
npm --version
```

都是有输出的。这种「系统告诉你有，工具告诉你没有」的状态，非常折磨心态。

#### 3.2.1 环境变量与 PATH：Node 在，但 npx 不在

后来我才逐步搞清楚：

- Node.exe 在 PATH 里没问题；
- 但 npm 全局 bin 路径（包括 npx）并不一定自动加进 PATH；
- 尤其是在 Windows 上，如果之前装/卸过不同版本的 Node/npm，PATH 里很可能一团糟。

当时的排查步骤大概是：

1. 用 PowerShell 查三个命令的位置：
	- `Get-Command node`
	- `Get-Command npm`
	- `Get-Command npx`
2. 发现 `node`、`npm` 有结果，而 `npx` 是找不到或指向奇怪的路径；
3. 再去看 npm 的配置目录和全局安装目录：

```powershell
npm config list
```

这一步之前，我其实是完全没有「npm 全局目录在哪」这种概念的，只是被环境问题逼着去理解。

#### 3.2.2 权限与路径：EPERM 这种幽灵错误

更恶心的是，当我尝试全局安装 Smithery CLI 时，还遇到了各种权限相关的报错，比如：

```text
npm ERR! code EPERM
```

那种感觉就像是：

- 你知道「理论上只要 `npm install -g 某某` 就行」；
- 但实际执行时，Windows 告诉你「抱歉你没有权限」；
- 而你又不想把整个 PowerShell 都提升到管理员权限来解决一切。

最后的解决方案其实写在了现在的 `PATH_debug.md` / `debug.md` 里：

- 把 npm 的缓存和全局安装目录改到用户目录下：

```powershell
npm config set cache "C:\Users\你的用户名\AppData\Roaming\npm-cache"
npm config set prefix "C:\Users\你的用户名\AppData\Roaming\npm"
```

- 然后把这个 `...\AppData\Roaming\npm` 目录手动加到 PATH 里：

```powershell
$env:PATH += ";C:\Users\你的用户名\AppData\Roaming\npm"
```

这一步做完之后，再跑：

```powershell
Get-Command npx
```

终于能看到一个像样的路径了。

#### 3.2.3 安装错包：`smithery` vs `@smithery/cli`

另一个非常典型的坑来自包名本身：

- 早期一些文章/AI 回答，会告诉你：`npm install -g smithery`；
- 但官方后来的推荐 CLI 实际上是：`@smithery/cli`；
- 这两个包不是一回事，而且前者在很多场景里已经不能满足最新文档的用法。

这就导致了一个非常诡异的体验：

- 你按照某些「看起来靠谱」的博客/AI 生成命令走了一遍；
- 命令行也提示「安装成功」；
- 结果 `smithery` 命令要么找不到，要么行为和官方文档描述完全对不上。

最后我给自己定了一个简单的原则：

> **所有跟 CLI 相关的命令，以官方文档为准，AI 给出的只当辅助提示。**

于是我按照现在 `debug.md` 里那套流程：

1. `npm uninstall -g smithery`
2. `npm install -g @smithery/cli`
3. 再去检查 `ls "C:\Users\你的用户名\AppData\Roaming\npm\node_modules\@smithery\cli\dist"`

确认真正的 CLI 文件确实落在磁盘上，才算心理踏实。

#### 3.2.4 「uv run playground」背后其实完全依赖 Node/npm

更有意思的一点是：

- 表面上你只是在 Python 世界里跑了一个命令：`uv run playground`；
- 但实际上，这个命令背后是去调用 Smithery 的 Node.js CLI 的；
- 所以只要 Node/npm 环境任何一环没配好，这个「看起来很 Python 的命令」都会在 Node 这头挂掉。

这一层隐含依赖，文档里通常不会强调，但在踩了几轮坑之后，它变成了我心里的一个 checklist：

- 只要 Playground 起不来，**第一反应不是怪 MCP，而是先检查 Node/npm 和 @smithery/cli 是否真的 OK**。

> （截图建议：
> 图 3：VS Code 里项目结构的截图，标出 `pyproject.toml`、`smithery.yaml`、`server.py`。）

### 3.3 不碰 MCP，先直连 Feishu API

我给自己定的第一小步是：

> 写一个最小可用的「FeishuTokenManager」，只负责一件事：拿到正确的 `app_access_token`。

当时的思路：

- 这个类接收 `app_id` 和 `app_secret`；
- 内部封装调用 Feishu 「获取应用自建应用 app_access_token」接口的逻辑；
- 在本地写一个简单的 `test_xxx.py`，直接调用这个类看能不能拿到 token。

这一步完成之后，我才开始真正放心地往 MCP 那一层走。

> （截图建议：
> 图 4：飞书开放平台文档页面，停留在 app_access_token 接口那一节。）

### 3.4 第一次成功：命令行里看到 `code: 0`

在某一个晚上，我跑了这样的一个测试脚本（伪代码）：

- 创建 `FeishuTokenManager(app_id, app_secret)`；
- 调用 `get_app_token()`；
- 把返回的 JSON 打印出来。

第一次看到终端里出现：

- `code: 0`
- `app_access_token: t-xxxxx...`
- `expire: 7200`

那一刻其实非常关键。

因为这证明了：

1. 我和飞书之间的网络没问题；
2. app_id / app_secret 没填错；
3. Feishu API 本身工作正常。

后面所有的坑，基本都不再怀疑是「飞书坏了」，而是集中在我自己的工程环节。

> （截图建议：
> 图 5：终端里打印的成功响应日志，打码 app_token，只保留 `code: 0` 核心信息。）

---

## 四、正式进入 MCP 世界：把逻辑包装成工具

确认底层逻辑可用之后，我才开始认真碰 MCP。

### 4.1 我脑中的第一个 MCP 设计：AI 说「session_config 很优雅」，但它没告诉我坑

当时我给这个工具的设想大概是这样的（坦白讲，其中有不少是当时用 Vibe Coding / AI 助手时，它帮我「脑补」出来的架构）：

- 工具名称：`get_feishu_app_token`；
- 不希望每次都显式传 app_id/app_secret，感觉麻烦；
- 所以我让工具去从 `session_config` 里读凭据（类似全局配置）：
	- `session_config.app_id`
	- `session_config.app_secret`

听起来很优雅，尤其是当 AI 用一种「这当然是最佳实践」的口吻给你推荐时：

> “配置只写一次，后面所有调用都自动带上。”

### 4.2 理想很美好，现实是 `Missing credentials`（以及「AI 明明说可以」的落差感）

当我第一次在 Smithery 的 MCP 客户端里调用这个工具时，看到的却是：

```text
Error executing tool get_feishu_app_token:
	Failed to get app token:
		Failed to refresh app token:
			Missing credentials: app_id=False, app_secret=False
```

粗暴翻译一下：

- 工具确实被调用了；
- 但它从 session_config 里压根没拿到任何有效配置；
- 我自己以为「配置肯定在某处被写好了」，但现实是：**它根本就没被写进去**。

这时候的困惑不止一层：

1. 为什么本地脚本是 OK 的，到了 Smithery 上就不行了？
2. 我到底有没有真正理解 MCP 的配置机制？
3. 那些我在 Vibe Coding 里看着很顺眼的「智能补全配置」究竟是基于哪一个版本的文档？

当时有几次很典型的体验：

- 我在 IDE 里描述大致需求：「想把 app_id / app_secret 放到 session_config 里管理」；
- AI 会帮我写出一整套看起来很合理的代码和配置；
- 但真正部署到 Smithery 或 Playground 里之后，它根本不会按那样的方式传这个配置。

这让我慢慢意识到一个事实：

> AI 给出的「用法」有时候是在补完自己的宇宙，而不是对照我当前这个具体平台和版本。

这也为后面「接口设计大重构」埋下了伏笔。

### 4.3 学会和错误做朋友：给自己多一点日志（和少一点「AI 说大概没问题」）

在这个阶段，我开始非常重度地给代码加日志：

- 在调用 Feishu API 前：打印请求 URL、app_id 的前几位（隐藏 secret）、headers；
- 在拿到响应后：打印 status code、响应头、完整 JSON；
- 在工具里：打印 `session_config` 的内容，看看里面到底有没有 app_id/app_secret。

这些日志有几个直接的好处：

1. 可以肉眼确认「到底发了什么请求给 Feishu」；
2. 可以肉眼确认「Feishu 的响应是不是正常」；
3. 可以确认「问题是不是真的出在 session_config 上」。

到这里，可以说我从「凭感觉排错」慢慢变成了「凭证据排错」。

> （截图建议：
> 图 6：一次完整请求-响应日志的截图，包括 `[DEBUG] Requesting app token ...`、`[DEBUG] Response status: 200` 和 `[DEBUG] Response data: {...}`。）

---

## 五、Docker 与 ASGI：在本地造一个可以丢上云的盒子

确认逻辑没问题之后，下一步就是：

> 把这个 MCP Server 打包进 Docker，让它在任何地方都能用同样的方式跑起来。

### 5.1 心理预期 vs. 真实情况

我原本的心理预期是：

- 随便写一个 Dockerfile；
- 把项目复制进去，装一下依赖；
- `uvicorn main:app` 一跑，世界和平。

结果现实给了我一套组合拳：

- 构建时报：`'src' does not exist or is not a directory`；
- 又报：`File '/app/README.md' cannot be found`；
- 运行时报：`'SmitheryFastMCP' object is not callable`；

每一条错误背后，其实都对应着我对项目结构和启动方式理解的不准确。

### 5.2 关键认识：真正的 ASGI app 在哪

最后让我豁然开朗的是这一点：

- Smithery/FastMCP 帮你封装了一个 server 对象，它不是一个直接可调用的 ASGI app；
- 真正用于 HTTP 的 ASGI app，在 `server._fastmcp.streamable_http_app` 这个属性里。

当我在本地打印：

- `type(server._fastmcp.streamable_http_app)`
- `callable(server._fastmcp.streamable_http_app)`

并看到这是一个标准的 ASGI callable 之后，我才知道 Docker 里应该怎么启动它。

> （截图建议：
> 图 7：终端里打印 `streamable_http_app type` 和 `callable=True` 的输出。）

### 5.3 本地容器内自查：不要一上来就怪平台

在这一步，我刻意做了这样一个顺序：

1. 在本地构建 Docker 镜像；
2. 本地跑容器，把端口映射出来；
3. 使用 curl / HTTP 客户端，按 MCP 协议顺序发请求：
	 - `initialize`
	 - `tools/list`
	 - `tools/call` 调用 `get_feishu_app_token`

这一轮全都跑通之后，我才敢说：

> “OK，这个镜像本身是健康的，接下来再谈远程部署。”

---

## 六、Smithery 远程部署：从「在我机器上能跑」到「在哪都能用」

有了 Docker 镜像，Smithery 的部署步骤本身其实并不复杂：

- 提交仓库和配置；
- Smithery 帮你构建镜像；
- 启动容器，并以 MCP 服务的形式暴露出来。

真正麻烦的是「远程调试」。

### 6.1 smithery.yaml：让平台知道你是谁

在 `smithery.yaml` 里，我需要告诉平台：

- 运行时使用 `container`；
- 构建用哪个 Dockerfile；
- MCP server 工厂函数在哪（比如 `feishu_token_mcp.server:create_server`）；
- MCP 以 HTTP 形式提供服务；
- 需要哪些配置项（app_id、app_secret 等）。

> （截图建议：
> 图 8：smithery.yaml 的关键片段截图，标出 runtime、build、startCommand、configSchema。）

### 6.2 「部署成功但调用失败」的疑惑

第一次远程部署之后，Smithery 上显示一切正常：

- 镜像构建成功；
- MCP 服务可以被扫描到；
- 控制台没有明显报错。

但当我在平台里真正调用 `get_feishu_app_token` 工具时，却看到了熟悉的那句：

```text
Missing credentials: app_id=False, app_secret=False
```

从那一刻开始，我大概能确定：

1. 这不是 Feishu API 的问题，
2. 也不是 Docker / Uvicorn 本身的问题，
3. 大概率还是我自己的「工具接口设计」有问题。

简单讲就是：我想象中的「session_config 里已经有了配置」，和实际 Smithery 的使用方式之间，有一个不小的鸿沟。

---

## 七、接口大重构：从「自动帮你读配置」到「你直接把参数告诉我」

这一部分是整个项目中最重要的设计转折点，也是我最想在这篇文章里留下来的东西。

### 7.1 我为什么放弃了 session_config 方案

经过一段时间的试验和对比，我发现自己的实际使用场景是这样的：

- 我更多是在一个互动式的环境里调用工具（比如对话框、Playground）；
- 我会自然地在上下文中提供 app_id/app_secret 一类的信息；
- 让 Agent 自己组织调用参数其实更直观。

而 session_config 这种方案更适合：

- 一组比较稳定、不常变的配置；
- 在 UI 里提前填好，然后很长一段时间都不动它。

飞书 app token 刷新这个场景，很微妙地踩在了中间：

- app_id/app_secret 本身是固定的；
- 但对于我的 Agent 来说，让它显式传一遍参数其实不算负担，反而更清晰。

于是我做了一个决策：

> **不再依赖 session_config，改成一个显式带参数的工具。**

### 7.2 最终版工具接口形态

重构之后，工具长这样：

- 工具名称：`get_feishu_app_token`
- 入参：
	- `app_id: string`
	- `app_secret: string`
- 出参：
	- `app_access_token`
	- `expires_at`
	- `success`
	- `message`

从使用者角度看，调用起来就是一句话：

> 「用这个 app_id 和 app_secret 帮我拿一个当前有效的 Feishu app token。」

从 Agent 的角度看：

- 它有足够的信息来构造调用；
- 它知道输出里有哪些字段可以继续用来请求别的接口。

### 7.3 改完之后的连锁反应

改完接口之后，我又重新走了一遍「三段式验证」：

1. 本地脚本：直接传 app_id/app_secret → 成功拿到 token；
2. 本地 MCP dev server：通过 HTTP 按 MCP 协议调用 `get_feishu_app_token` → 成功；
3. Smithery 远程平台：部署更新后的版本，通过工具调用 → 成功。

这个过程给我的感觉是：

> 当接口和真实使用方式对齐之后，很多「玄学 bug」就自动消失了。

> （截图建议：
> 图 9：在 Smithery 或某个 MCP 客户端里，调用 `get_feishu_app_token` 的界面，左边输入 app_id/app_secret，右边返回 app_access_token。）

---

## 八、把坑摊开讲：错误清单 & 排障思路

这一节我不打算贴任何代码，只想集中讲几个典型错误，以及当时我是怎么一步步把问题缩小范围、找到根因的——包括前面提到的环境 / Node / CLI / AI 误导这些「非代码层」的坑。

### 8.1 环境与工具链相关的坑

**坑 0：`✗ npx not found. Please install Node.js to use the playground`**

- 
	- 现象：在 Windows 上明明已经安装了 Node.js 和 npm，`node --version`、`npm --version` 都正常，但一旦跑 `uv run playground` 就提示找不到 npx；
	- 根因：
		- npm 全局 bin 目录不在 PATH 里；
		- 有时候系统里有多个 Node/npm 版本，PATH 指向比较旧/奇怪的那一个；
	- 心理感受：
		- 「我不是已经照官方文档装了 Node 吗，为什么还要自己翻 PATH？」
		- 有一种「工具互相甩锅」的挫败感：Node 认为一切正常，Smithery CLI 却说「你没装」；
	- 排查路径：
		1. 先用 `Get-Command node/npm/npx` 确认三个命令各自指向哪里；
		2. 再用 `npm config list` 看当前的 prefix / cache；
		3. 如果前缀在一个需要管理员权限的目录，就挪到用户目录；
	- 解决方案：
		- 把 npm 的缓存/全局目录改到用户目录下；
		- 手动把 `C:\Users\<用户名>\AppData\Roaming\npm` 加进 PATH；
		- 再次打开新的 PowerShell 会话，让 PATH 生效；
	- 反思：
		- 以后只要遇到「某个 CLI 明明安装了却说找不到」，第一时间打印 PATH 和 `Get-Command`，而不是一股脑儿重装。

**坑 1：`npm ERR! code EPERM`（权限错误）**

- 
	- 现象：全局安装 @smithery/cli 时，出现 `EPERM`，提示无权限写入某些目录；
	- 根因：npm 全局安装目录在系统目录，普通用户写入需要管理员权限；
	- 排查路径：
		- 查看 `npm config get prefix`，发现指向了类似 `C:\Program Files\nodejs`；
	- 解决方案：
		- 用前面提到的方法，把 prefix 改到用户目录；
		- 避免依赖「以管理员身份运行 PowerShell」这种一次性的解决方案；
	- 反思：
		- 对于会经常更新的 CLI 工具，全局安装目录最好一开始就放在用户目录，不要和系统目录搅在一起。

**坑 2：安装错包：`smithery` vs `@smithery/cli`**

- 
	- 现象：
		- 按照某些博客 / AI 提示安装了 `npm install -g smithery`；
		- 结果命令行里的 `smithery` 命令行为和官方文档完全对不上；
	- 根因：
		- 老版本生态与新版本 CLI 命名不同；
		- 部分 AI 回答基于旧文档/旧博客，没有更新；
	- 解决方案：
		- 以官方文档为唯一真理源：卸载旧包 `npm uninstall -g smithery`；
		- 全局安装 `@smithery/cli`；
		- 用 `ls "...\node_modules\@smithery\cli\dist"` 确认真实落盘路径；
	- 反思：
		- 遇到这种「名字很像」的包，必须回源头确认，不要完全相信 AI 给的命令。

**坑 3：Playground 页面显示 "Connection Error - Failed to fetch"**

- 
	- 现象：
		- Smithery Playground 页面能打开，但一进入就报连接错误；
	- 根因：
		- 本地 MCP dev server 根本没启动，Playground 只是个前端界面；
	- 解决方案：
		- 在一个终端里先启动 dev server：`uv run dev --port 8081`；
		- 在另一个终端里再跑 `npx @smithery/cli playground --port 8081`；
		- 确保两个进程都活着；
	- 反思：
		- Playground 不是「魔法」，它只是帮你把浏览器连到本地 8081 而已，后面仍然需要一个 MCP 服务器真正跑着。

### 8.2 构建阶段的坑

**错误 1： `'src' does not exist or is not a directory`**

- 现象：Docker 构建时报项目路径相关的错误，提示找不到 `src`；
- 根因：`pyproject.toml` 的配置和实际目录结构不匹配；
- 解决思路：
	1. 打开镜像里实际的目录结构；
	2. 对照 `pyproject.toml` 里的路径配置；
	3. 调整到「代码真正存在的地方」——而不是想当然觉得它在 `src/`。

**错误 2： `File '/app/README.md' cannot be found`**

- 现象：构建阶段突然报 README 找不到；
- 根因：`.dockerignore` 把 README 之类的文件排除了，而构建过程又需要它；
- 解决思路：
	- 检查 `.dockerignore`；
	- 把真正构建需要的文件去掉忽略规则，重新构建。

### 8.3 运行和协议层的坑

**错误 3： `'SmitheryFastMCP' object is not callable`**

- 现象：Uvicorn 启动时提示这个对象不可调用；
- 根因：把整个 server 当作 ASGI app 来跑了，其实真正的 ASGI app 在 `server._fastmcp.streamable_http_app`；
- 解决思路：
	1. 在本地打印 server 的类型；
	2. 查文档确认 FastMCP 的 HTTP 启动方式；
	3. 修正 Docker/Uvicorn 的启动入口。

**错误 4： `Not Acceptable: Client must accept both application/json and text/event-stream`**

- 现象：HTTP 请求 `initialize` 时返回 406；
- 根因：请求头里的 `Accept` 写成了单一的 `application/json`；
- 解决思路：
	- 把 `Accept` 改成：`application/json, text/event-stream`；
	- 再次请求就恢复正常。

**错误 5： `Bad Request: Missing session ID`**

- 现象：后续调用（比如 `tools/call`）提示缺少 session ID；
- 根因：MCP 使用了基于 session 的流式机制，而我每次请求都是「全新一轮」，没有正确管理 session；
- 解决思路：
	- 了解 MCP 的 session 机制；
	- 在需要的时候，从初始化响应中取 session ID 并带到后续请求里；
	- 或者尽量用官方 Playground / 客户端来代理这部分逻辑。

### 8.4 业务逻辑层的坑

**错误 6： `invalid param`（来自 Feishu API）**

- 现象：飞书返回 `invalid param`，但肉眼看参数好像都没问题；
- 根因：
	- 可能是参数里有空格、默认值为空字符串、未 strip；
	- 也可能是 payload 格式和文档有细微出入；
- 解决思路：
	1. 在本地先写一个只负责调用 Feishu API 的脚本；
	2. 打印出「最终发出去」的 JSON payload（隐藏敏感字段）；
	3. 和飞书文档一行一行对照；
	4. 直到本地脚本 100% 成功，再把这段逻辑搬进 MCP 服务里。

**错误 7： `Missing credentials: app_id=False, app_secret=False`（来自我自己的检查）**

- 现象：工具内部检查发现 app_id/app_secret 根本没传进来；
- 根因：过度依赖 session_config，实际使用中 session 里没有这两个字段；
- 解决思路：
	- 承认「这个接口设计本身不适合我的使用场景」；
	- 改成显式传参的工具；
	- 顺便在接口里加上更友善的错误提示和日志。

---

## 十、错误对照速查表：从症状快速跳回对应故事段落

为了让这篇长文在「回头查」的时候更好用，我最后把前面提到的典型错误再整理成一个索引表，方便你对照：

| 错误大类 | 具体报错/现象 | 主要来源文件 | 本文相关小节 | 一句话提示 |
|----------|----------------|--------------|--------------|------------|
| 环境 / Node/npm | `✗ npx not found. Please install Node.js to use the playground` | `PATH_debug.md` / `debug.md` | 3.2, 8.1 | 先检查 Node/npm、PATH 和 npm prefix，不要急着重装一切 |
| 环境 / 权限 | `npm ERR! code EPERM` | `PATH_debug.md` | 3.2.2, 8.1 | 把 npm 全局目录挪到用户目录，避免系统目录权限坑 |
| 环境 / 包名 | 安装了 `smithery` 而不是 `@smithery/cli` | `PATH_debug.md` / `debug.md` | 3.2.3, 8.1 | 以官方文档为准，卸载旧包，安装 `@smithery/cli` |
| Playground 连接 | 浏览器里 "Connection Error - Failed to fetch" | `debug.md` | 3.2.4, 8.1 | 先确认本地 MCP dev server 已启动，再开 playground |
| Docker 构建 | `'src' does not exist or is not a directory` | `DEPLOYMENT_ISSUES.md`, `QUICK_FIX.md` | 5.2, 8.2 | 确认 pyproject 里的路径和实际目录一致，Dockerfile 复制顺序正确 |
| Docker 构建 | `File '/app/README.md' cannot be found` | 同上 | 5.2, 8.2 | `.dockerignore` 不要排除 README.md 这类构建需要的文件 |
| Docker 构建 | `project.license as a TOML table is deprecated` | 同上 | 5.2, 8.2 | 把 `license = {text = "MIT"}` 改成 `license = "MIT"` |
| 运行时 / ASGI | `'SmitheryFastMCP' object is not callable` | `DEPLOYMENT_ISSUES.md`, `debug.md`, `QUICK_FIX.md` | 5.2, 8.3 | 用 `server._fastmcp.streamable_http_app` 作为 ASGI app，而不是直接丢 server |
| 部署 / 扫描 | `Scan Failed - couldn't connect to your server` | `QUICK_FIX.md`, `debug.md` | 6.2, 8.3 | 确认容器真的启动成功、端口正确，并在 Smithery 里配置测试 profile |
| MCP 协议 | `Not Acceptable: Client must accept both application/json and text/event-stream` | `debug.md` | 8.3 | `Accept` 头要同时包含 json 和 event-stream |
| MCP 协议 | `Bad Request: Missing session ID` | `debug.md` | 8.3 | 多步请求要正确管理 session id，或者让官方客户端代劳 |
| 业务 / Feishu API | `Failed to refresh app token: invalid param` | `debug.md` / `DEPLOYMENT_ISSUES.md` | 3.3, 8.4 | 拼 payload 前一定要做参数 strip 和空值校验，多打日志 |
| 业务 / 配置 | `Missing credentials: app_id=False, app_secret=False` | `debug.md` | 4.2, 7.1, 8.4 | 不要盲目迷信 session_config，必要时改成显式函数参数 |

如果你正在处理自己的项目，可以用这张表当「起点」：

1. 先找到你遇到的那句错误；
2. 对照看看属于哪一类；
3. 跳回本文对应的小节，看当时我是怎么一步步发现根因的；
4. 再结合你自己的环境，决定是照抄方案，还是只借鉴思路。

---

## 九、从这次折腾里，我真正学到的几件事

写到这里，其实代码细节已经不那么重要了，真正重要的是这次折腾带来的几条「经验法则」。

### 9.1 调试顺序：永远从最底层往上爬

这次的路子大概可以概括为：

1. **先测第三方 API**：确认飞书本身是好的；
2. **再测纯 Python 逻辑**：确认 token 管理逻辑没问题；
3. **再测本地 MCP dev server**：确认协议层调用没问题；
4. **再测 Docker 容器**：确认打包后环境没引入新问题；
5. **最后才是远程平台**：把所有本地变量先搞定，再去怪云。

这套顺序有一个核心好处：

> 每往上加一层，只新增一个变量，你更容易判断问题出在哪一层。

### 9.2 接口设计：显式参数通常比「魔法配置」更靠谱

一开始我非常迷恋那种「一次配置、处处生效」的感觉。

但实践告诉我，尤其是在 MCP、Agent 这些场景下：

- 如果调用方是一个智能体，它其实完全能理解「我现在要用哪个 app_id/app_secret」；
- 把这些信息藏进 session 里，有时候反而增加了不可见性和不确定；
- **显式参数 + 清晰的输入输出**，对人和 Agent 都更友好。

这也是为什么最终我只保留了：

- `get_feishu_app_token(app_id, app_secret)` 这样一个非常直接的工具接口。

### 9.3 日志是你最好的队友

在所有的排障过程中，有三类日志最帮忙：

1. 请求日志：我到底给 Feishu 发了什么；
2. 响应日志：Feishu 具体回了什么，而不是只看「报错两个字」；
3. 配置日志：在工具内部打印 session_config / 参数实际值。

它们帮我从「感觉上」怀疑问题，变成「证据上」确定问题。

### 9.4 新手也可以做有用的东西，只要你愿意耐心拆问题

从一开始我就没打算追求什么“最佳实践框架”，我只是想：

> 少改一点表，多一点自动化。

但在这个非常具体的小目标的推动下，我顺带：

- 理解了 MCP 的基本模式；
- 学会了如何用 Smithery 管理一个 Python MCP 服务；
- 踩完了一整套 Docker + ASGI 启动的坑；
- 想明白了一个接口到底应该为谁服务。

如果你也有类似的痛点（哪怕不是飞书 token），也许可以尝试照着这条路径走一圈：

1. 找一个你一直在重复做的「苦力活」；
2. 把它抽象成一个有明确输入输出的「能力」；
3. 用 MCP 把这个能力封装成一个标准的工具；
4. 交给 Agent 或自动化系统去定期使用它。

也许，你会发现，**真正爽的不是写完某个函数，而是看到一段本来需要你自己操心的流程，从此悄无声息地自己运转下去。**

