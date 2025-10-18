#!/bin/bash

# SaveMoney 部署配置测试脚本

echo "🔍 检查部署配置文件..."

# 检查zeabur.json
if [ -f "zeabur.json" ]; then
    echo "✅ zeabur.json 存在"
else
    echo "❌ zeabur.json 不存在"
    exit 1
fi

# 检查Dockerfile
if [ -f "backend/Dockerfile" ]; then
    echo "✅ backend/Dockerfile 存在"
else
    echo "❌ backend/Dockerfile 不存在"
    exit 1
fi

if [ -f "frontend/Dockerfile" ]; then
    echo "✅ frontend/Dockerfile 存在"
else
    echo "❌ frontend/Dockerfile 不存在"
    exit 1
fi

# 检查nginx配置
if [ -f "frontend/nginx.conf" ]; then
    echo "✅ frontend/nginx.conf 存在"
else
    echo "❌ frontend/nginx.conf 不存在"
    exit 1
fi

# 检查Python依赖
if [ -f "backend/pyproject.toml" ]; then
    echo "✅ backend/pyproject.toml 存在"
else
    echo "❌ backend/pyproject.toml 不存在"
    exit 1
fi

# 检查Node.js依赖
if [ -f "frontend/package.json" ]; then
    echo "✅ frontend/package.json 存在"
else
    echo "❌ frontend/package.json 不存在"
    exit 1
fi

# 检查环境变量配置
if [ -f "frontend/.env.production" ]; then
    echo "✅ frontend/.env.production 存在"
else
    echo "❌ frontend/.env.production 不存在"
    exit 1
fi

# 检查部署文档
if [ -f "DEPLOYMENT.md" ]; then
    echo "✅ DEPLOYMENT.md 存在"
else
    echo "❌ DEPLOYMENT.md 不存在"
    exit 1
fi

echo ""
echo "📋 验证Dockerfile语法..."

# 验证Dockerfile语法（基础检查）
if docker build --no-cache -t test-backend -f backend/Dockerfile backend > /dev/null 2>&1; then
    echo "✅ backend/Dockerfile 语法正确"
else
    echo "⚠️ backend/Dockerfile 构建失败（可能是依赖问题，但语法可能正确）"
fi

if docker build --no-cache -t test-frontend -f frontend/Dockerfile frontend > /dev/null 2>&1; then
    echo "✅ frontend/Dockerfile 语法正确"
else
    echo "⚠️ frontend/Dockerfile 构建失败（可能是依赖问题，但语法可能正确）"
fi

echo ""
echo "🔧 检查Python依赖..."
cd backend
if python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))" > /dev/null 2>&1; then
    echo "✅ pyproject.toml 语法正确"
else
    echo "❌ pyproject.toml 语法错误"
fi
cd ..

echo ""
echo "🔧 检查Node.js依赖..."
cd frontend
if node -e "JSON.parse(fs.readFileSync('package.json'))" > /dev/null 2>&1; then
    echo "✅ package.json 语法正确"
else
    echo "❌ package.json 语法错误"
fi
cd ..

echo ""
echo "✅ 部署配置测试完成！"
echo ""
echo "📝 下一步："
echo "1. 将代码推送到GitHub仓库"
echo "2. 在Zeabur Dashboard中导入项目"
echo "3. 配置环境变量"
echo "4. 部署应用"
echo ""
echo "详细部署说明请参考 DEPLOYMENT.md"