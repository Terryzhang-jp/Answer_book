# 答案之书系统

基于角色扮演协议v8.0的智能问答系统，使用LangChain和FastAPI构建。

## 🌟 特性

- **单Session架构**: 所有角色在同一个LLM会话中，无需复杂的多agent协调
- **智能专家邀请**: 系统根据问题自动邀请最合适的专家
- **深度角色扮演**: 基于角色保真协议，每个专家都有独特的思维方式和表达风格
- **自由对话模式**: 支持专家之间的快速交流和辩论
- **JSON结构化输出**: 便于前端展示和处理
- **会话记忆**: 支持多轮对话，保持上下文连贯性

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd answer

# 运行启动脚本
./start.sh
```

### 2. 配置API密钥

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动

## 📖 API文档

启动服务后访问：
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/health

## 🔧 API接口

### 1. 提问接口

**POST** `/api/ask`

```json
{
  "question": "我不知道我的人生为什么而活",
  "thread_id": "optional-thread-id"
}
```

**响应:**

```json
{
  "room_announcement": "房间宣告内容",
  "character_responses": [
    {
      "character_name": "苏格拉底",
      "character_role": "expert_1",
      "thinking": "内心思考过程",
      "speaking": "外在发言内容",
      "body_language": "肢体语言描述"
    }
  ],
  "dialogue_mode": "single",
  "next_action": "continue",
  "thread_id": "generated-thread-id",
  "timestamp": "2024-01-01T00:00:00"
}
```

### 2. 继续对话

**POST** `/api/continue`

```json
{
  "message": "我想听听你们的具体建议",
  "thread_id": "existing-thread-id"
}
```

### 3. 会话管理

- **GET** `/api/sessions` - 列出所有会话
- **DELETE** `/api/sessions/{thread_id}` - 删除指定会话

## 🧪 测试

运行测试脚本：

```bash
python test_api.py
```

## 🏗️ 技术架构

### 核心组件

1. **FastAPI**: Web框架，提供RESTful API
2. **LangChain**: LLM集成和会话管理
3. **RunnableWithMessageHistory**: 自动管理对话历史
4. **InMemoryChatMessageHistory**: 内存中的会话存储

### 架构优势

- **简洁性**: 单Session架构，避免多agent复杂性
- **可扩展性**: 基于prompt engineering，易于添加新专家
- **可靠性**: 使用成熟的LangChain框架
- **性能**: 内存存储，响应快速

## 📝 角色扮演协议

系统基于房间协议v8.0，核心法则：

1. **身份自主权**: 每个角色保持独特身份
2. **思想主权**: 角色有私密的内心思考
3. **地位平等**: 所有成员地位平等
4. **自然表达**: 符合人类自然交流模式
5. **行动后果**: 每个行动都有真实影响

## 🔄 对话流程

1. **用户提问** → 系统分析问题类型
2. **专家邀请** → 系统推荐并邀请两位专家
3. **房间宣告** → 宣布专家身份和房间法则
4. **专家对话** → 专家轮流发言或自由对话
5. **持续交流** → 支持多轮深度讨论

## 🎯 使用场景

- **人生咨询**: 哲学家帮助思考人生意义
- **技术讨论**: 科技专家探讨创新方向
- **商业决策**: 企业家分享管理智慧
- **创意启发**: 艺术家激发创作灵感

## 🛠️ 开发指南

### 添加新专家类别

1. 在系统prompt中定义新的问题分类逻辑
2. 让LLM在reasoning过程中创建相应专家人设
3. 无需修改代码，完全通过prompt engineering实现

### 自定义输出格式

修改 `create_system_prompt()` 函数中的JSON格式定义。

### 扩展API功能

在 `main.py` 中添加新的FastAPI路由。

## 🐛 故障排除

### 常见问题

1. **模型初始化失败**
   - 检查API密钥是否正确配置
   - 确认网络连接正常

2. **JSON解析错误**
   - 模型可能返回非JSON格式
   - 系统会自动尝试提取JSON部分

3. **会话不存在**
   - 检查thread_id是否正确
   - 会话存储在内存中，重启服务会丢失

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 联系

如有问题，请提交Issue或联系开发团队。
# Answer_book
