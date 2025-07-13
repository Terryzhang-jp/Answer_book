# Room Protocol Backend

一个基于FastAPI的智能对话房间系统后端，实现了完整的房间协议v8.0。

## 🌟 特性

- **智能专家邀请**: 根据用户问题自动邀请合适的专家
- **多轮对话支持**: 支持专家间的深度辩论和交流
- **系统对话**: 支持用户与系统管理员的直接交互
- **记忆系统**: 记录用户偏好和对话历史
- **模块化架构**: 清晰的分层架构，易于维护和扩展
- **完整测试**: 包含单元测试和集成测试

## 🏗️ 项目结构

```
room protocol backend/
├── api/                    # API层
│   ├── routes/            # 路由定义
│   ├── middleware/        # 中间件
│   └── dependencies/      # 依赖注入
├── core/                  # 核心业务层
│   ├── services/         # 业务逻辑服务
│   ├── models/           # 数据模型
│   └── schemas/          # Pydantic模型
├── utils/                 # 工具层
│   └── memory_system.py  # 记忆系统
├── config/               # 配置层
│   ├── settings.py       # 配置管理
│   └── constants.py      # 常量定义
├── tests/                # 测试层
│   ├── unit/            # 单元测试
│   └── integration/     # 集成测试
├── static/              # 静态文件
├── main.py              # 应用入口
├── requirements.txt     # 生产依赖
└── requirements-dev.txt # 开发依赖
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 环境配置

复制环境变量模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件，配置API密钥：
```env
# 至少配置一个LLM API密钥
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# 其他配置
DEBUG=true
HOST=0.0.0.0
PORT=8000
```

### 3. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

### 4. API文档

启动服务后，访问以下地址查看API文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📡 API端点

### 健康检查
- `GET /api/health` - 健康检查

### 对话相关
- `POST /api/ask` - 提问
- `POST /api/continue` - 继续对话

### 会话管理
- `GET /api/sessions` - 列出所有会话
- `DELETE /api/sessions/{thread_id}` - 删除指定会话

## 🧪 运行测试

### 安装开发依赖
```bash
pip install -r requirements-dev.txt
```

### 运行所有测试
```bash
pytest
```

### 运行单元测试
```bash
pytest tests/unit/
```

### 运行集成测试
```bash
pytest tests/integration/
```

### 生成测试覆盖率报告
```bash
pytest --cov=. --cov-report=html
```

## 🔧 开发工具

### 代码格式化
```bash
black .
```

### 代码检查
```bash
flake8 .
```

### 类型检查
```bash
mypy .
```

### 导入排序
```bash
isort .
```

## 🏛️ 架构设计

### 分层架构

1. **API层**: 处理HTTP请求和响应
2. **服务层**: 实现业务逻辑
3. **模型层**: 定义数据结构
4. **工具层**: 提供通用功能

### 核心服务

- **LLMService**: 管理大语言模型交互
- **PromptService**: 管理系统提示词
- **ExpertService**: 管理专家数据库
- **ConversationService**: 处理对话逻辑
- **MemorySystem**: 管理用户记忆

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

如果您遇到问题或有疑问，请：

1. 查看 [API文档](http://localhost:8000/docs)
2. 检查 [Issues](../../issues)
3. 创建新的 Issue

## 🔮 未来计划

- [ ] 添加更多专家类型
- [ ] 实现专家个性化定制
- [ ] 添加对话导出功能
- [ ] 支持多语言
- [ ] 添加语音交互
- [ ] 实现分布式部署
