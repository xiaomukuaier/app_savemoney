# Zeabur 手动部署指南

由于Zeabur可能无法自动识别前后端分离的项目结构，请按照以下步骤手动配置：

## 第一步：删除现有部署

如果已经有部署，请先删除：
1. 进入 Zeabur Dashboard
2. 选择当前项目
3. 删除所有服务

## 第二步：手动创建服务

### 创建后端服务

1. **创建新服务**
   - 点击 "Create Service"
   - 选择 "Backend" 类型
   - 选择 "GitHub" 作为来源
   - 选择 `xiaomukuaier/app_savemoney` 仓库

2. **设置根目录**
   - 进入后端服务的 "Settings" 选项卡
   - 找到 "Root Directory" 字段
   - 输入：`backend`
   - 点击保存

3. **配置环境变量**
   - 在 "Environment Variables" 中设置：
   ```
   FEISHU_APP_ID=你的飞书应用ID
   FEISHU_APP_SECRET=你的飞书应用密钥
   FEISHU_TABLE_ID=你的飞书表格ID
   OPENAI_API_KEY=你的OpenAI API密钥
   LANGCHAIN_API_KEY=你的LangChain API密钥（可选）
   ```

4. **重新部署**
   - 点击 "Redeploy Service"

### 创建前端服务

1. **创建新服务**
   - 点击 "Create Service"
   - 选择 "Static" 类型
   - 选择 "GitHub" 作为来源
   - 选择 `xiaomukuaier/app_savemoney` 仓库

2. **设置根目录**
   - 进入前端服务的 "Settings" 选项卡
   - 找到 "Root Directory" 字段
   - 输入：`frontend`
   - 点击保存

3. **配置环境变量**
   - 在 "Environment Variables" 中设置：
   ```
   VITE_API_BASE_URL=后端服务的URL（Zeabur会自动提供）
   ```

4. **重新部署**
   - 点击 "Redeploy Service"

## 第三步：配置路由

1. **进入项目设置**
   - 选择项目，进入 "Routes" 选项卡

2. **添加路由规则**
   - `/api/*` → 后端服务
   - `/*` → 前端服务

## 验证部署

部署完成后，访问你的域名应该能看到：
- 前端界面正常显示
- 语音录音功能正常工作
- API请求能正确转发到后端

## 故障排除

### 如果前端显示404
- 检查前端服务的根目录是否正确设置为 `frontend`
- 确认前端构建成功（查看构建日志）

### 如果API请求失败
- 检查后端服务的根目录是否正确设置为 `backend`
- 确认后端服务正在运行（查看运行日志）
- 验证环境变量是否正确设置

### 如果构建失败
- 查看构建日志中的错误信息
- 确认依赖包版本兼容性
- 检查Python和Node.js版本要求

## 自动部署

配置完成后，每次推送到GitHub主分支，Zeabur会自动重新部署两个服务。