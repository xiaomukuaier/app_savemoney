# SaveMoney 应用部署指南

## Zeabur 部署说明

### 前置要求

1. 注册 Zeabur 账户
2. 连接 GitHub 仓库
3. 准备以下环境变量：

### 必需的环境变量

#### 后端服务环境变量

```bash
FEISHU_APP_ID=你的飞书应用ID
FEISHU_APP_SECRET=你的飞书应用密钥
FEISHU_TABLE_ID=你的飞书多维表格ID
OPENAI_API_KEY=你的OpenAI API密钥
LANGCHAIN_API_KEY=你的LangChain API密钥（可选）
```

#### 前端服务环境变量

```bash
VITE_API_BASE_URL=后端服务URL（Zeabur会自动设置）
```

### 部署步骤

#### 方法一：通过 Zeabur Dashboard

1. 登录 Zeabur Dashboard
2. 点击 "Create Project"
3. 选择 "Import from GitHub"
4. 选择 `xiaomukuaier/app_savemoney` 仓库
5. Zeabur 会自动检测 `zeabur.json` 配置文件
6. 在环境变量设置中配置上述环境变量
7. 点击部署

#### 方法二：通过 Zeabur CLI

1. 安装 Zeabur CLI
```bash
npm install -g @zeabur/cli
```

2. 登录
```bash
zeabur login
```

3. 部署
```bash
zeabur deploy
```

### 项目结构说明

Zeabur 会根据 `zeabur.json` 配置文件自动识别和部署：

- **后端服务**：基于 `backend/Dockerfile` 构建
- **前端服务**：基于 `frontend/Dockerfile` 构建
- **路由配置**：前端服务处理所有 `/` 请求，后端服务处理 `/api/*` 请求

### 健康检查

后端服务包含健康检查端点：
- `GET /health` - 返回服务状态

### 自定义域名

部署完成后，可以在 Zeabur Dashboard 中配置自定义域名。

### 监控和日志

- 在 Zeabur Dashboard 中查看服务状态
- 查看实时日志
- 监控资源使用情况

### 故障排除

#### 常见问题

1. **环境变量未设置**
   - 确保所有必需的环境变量都已正确设置
   - 检查环境变量名称是否正确

2. **CORS 错误**
   - 检查前端域名是否在允许的域名列表中
   - 可以在 `ALLOWED_ORIGINS` 环境变量中添加额外域名

3. **构建失败**
   - 检查 Dockerfile 语法
   - 确认依赖包版本兼容性

4. **服务无法启动**
   - 检查端口配置
   - 确认启动命令正确

#### 调试技巧

1. 查看构建日志
2. 检查环境变量是否正确注入
3. 验证服务健康检查
4. 测试 API 端点

### 更新部署

当代码更新时，Zeabur 会自动重新部署（如果配置了自动部署），或者可以手动触发重新部署。

### 备份和恢复

- 定期备份环境变量配置
- 飞书表格数据由飞书平台管理
- 应用本身是无状态的，不存储用户数据