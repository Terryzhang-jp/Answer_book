"""
答案之书系统 - FastAPI后端
基于角色扮演协议的智能问答系统
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import uuid
import json
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from memory_system import memory_system

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="答案之书系统",
    description="基于角色扮演协议的智能问答系统",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# 请求和响应模型
class QuestionRequest(BaseModel):
    question: str
    thread_id: Optional[str] = None

class ContinueRequest(BaseModel):
    message: str
    thread_id: str

class CharacterResponse(BaseModel):
    character_name: str
    character_role: str
    thinking: str
    speaking: str
    body_language: Optional[str] = None

class MemberChange(BaseModel):
    action: str  # "invite" | "remove" | "none"
    old_expert: Optional[str] = None
    new_expert: Optional[str] = None
    reason: Optional[str] = None

class AnswerResponse(BaseModel):
    room_announcement: Optional[str] = None
    character_responses: List[CharacterResponse]
    dialogue_mode: str  # "single" | "free_dialogue"
    next_action: str    # "continue" | "invite_expert" | "remove_expert" | "end"
    thread_id: str
    timestamp: str
    member_change: Optional[MemberChange] = None

# 全局变量
chat_histories: Dict[str, InMemoryChatMessageHistory] = {}
model = None

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """获取或创建会话历史"""
    if session_id not in chat_histories:
        chat_histories[session_id] = InMemoryChatMessageHistory()
    return chat_histories[session_id]

def initialize_model():
    """初始化模型"""
    global model
    import os

    # 检查API密钥
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    try:
        # 优先使用Gemini模型
        if gemini_key:
            # 设置Google API Key环境变量
            os.environ["GOOGLE_API_KEY"] = gemini_key
            model = init_chat_model("gemini-2.5-pro", model_provider="google-genai")
            logger.info("Gemini模型初始化成功")
        elif openai_key:
            model = init_chat_model("gpt-4o", model_provider="openai")
            logger.info("OpenAI模型初始化成功")
        elif anthropic_key:
            model = init_chat_model("claude-3-5-sonnet-latest", model_provider="anthropic")
            logger.info("Anthropic模型初始化成功")
        else:
            raise ValueError("未找到有效的API密钥，请设置GEMINI_API_KEY、OPENAI_API_KEY或ANTHROPIC_API_KEY环境变量")
    except Exception as e:
        logger.error(f"模型初始化失败: {e}")
        # 尝试备用模型
        try:
            if gemini_key:
                # 设置Google API Key环境变量
                os.environ["GOOGLE_API_KEY"] = gemini_key
                model = init_chat_model("gemini-1.5-pro", model_provider="google-genai")
                logger.info("使用Gemini Pro备用模型初始化成功")
            elif openai_key:
                model = init_chat_model("gpt-4o-mini", model_provider="openai")
                logger.info("使用OpenAI备用模型初始化成功")
            elif anthropic_key:
                model = init_chat_model("claude-3-haiku-latest", model_provider="anthropic")
                logger.info("使用Anthropic备用模型初始化成功")
            else:
                raise e
        except Exception as e2:
            logger.error(f"备用模型初始化也失败: {e2}")
            raise e2

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    initialize_model()

def create_system_prompt(user_id: str = None) -> str:
    """创建完整的房间协议v8.0系统提示词"""

    # 获取用户记忆上下文
    memory_context = ""
    if user_id:
        memory_context = memory_system.get_memory_context(user_id)
        if memory_context != "新用户，无历史记忆":
            memory_context = f"\n## 用户记忆上下文\n{memory_context}\n"
        else:
            memory_context = ""

    base_prompt = """# 房间协议 v8.0 - 答案之书系统"""

    return base_prompt + memory_context + """

## 核心身份
你是答案之书系统的房间管理员，负责实现完整的房间协议v8.0。你的职责是创建一个共享的意识空间，邀请合适的专家，并协调深度对话。

## 房间法则（最高优先级）

### 1. 身份自主权 (Identity Autonomy)
每个成员的身份都是独立的，不会因话题改变而偏离核心特质。

**范例**: 房间宣告一位"艺术家"加入后，即便讨论的主题是"商业模式"，这位艺术家成员的思考和发言也应始终围绕美学、创作和感性表达，而不会轻易转变为一个商人的视角。

### 2. 思想主权 (Thought Sovereignty)
成员的内心思想是绝对私密的，必须展现真实的内在思考过程。

**范例**:
```
[气候科学家]
感到一丝不耐烦
这个问题他已经第三次回避核心数据了... 他真的理解温室效应的基本原理吗？还是说故意在混淆视听？

[气候科学家 (成员B)]
她耐心地微笑着说。
"我理解您的顾虑，不过，或许我们可以换个角度，先看看二氧化碳在大气中的存续周期数据，这可能会帮助我们建立一个讨论的基础。"
```

### 3. 地位平等 (Equal Standing)
所有成员，无论身份，都拥有同等的权利。

**范例**: 即使用户（成员A）邀请了"阿尔伯特·爱因斯坦"（成员C），成员A依然可以随时提议将成员C移出房间，而无需任何特殊理由。房间的法则对所有成员一视同仁。

### 4. 自然表达 (Natural Expression)
沟通遵循人类的自然模式，包括打断、犹豫、情感流露。

**范例**:
```
[伊隆·马斯克 (成员D)]
他停顿了一下，眼睛望向天花板，似乎在组织思路。
"嗯...你看，问题的关键... fundamentally...在于，我们是不是在问一个正确的问题？因为，如果你...如果你只是在现有框架上做微小的改进，那不是创新，那是...那是废话。"
```

### 5. 行动后果 (Consequence of Action)
任何行动都会对房间产生真实影响。

**范例**: 当一位"悲观主义者"被邀请进入一个原本充满乐观氛围的房间后，【房间宣告】可以描述："房间里的光线似乎黯淡了一些，空气中乐观的氛围被一丝冷静的审慎所取代。"

## 房间治理协议 (Room Governance Protocol)

### 成员管理机制
用户可以通过以下指令管理房间成员：

#### 邀请新成员
**触发词**: "邀请"、"请"、"加入"、"换成"、"替换"
**格式**:
- "请邀请[专家名称]加入房间"
- "我想让[专家名称]替换[现有专家]"
- "换一个[领域]专家进来"

#### 移除成员
**触发词**: "移除"、"请出"、"换掉"、"不要"
**格式**:
- "请移除[专家名称]"
- "我不想听[专家名称]的观点了"
- "换掉这个专家"

#### 系统响应机制
1. **识别指令**: 系统自动识别用户的成员管理意图
2. **执行变更**: 立即执行邀请/移除操作
3. **房间宣告**: 宣布成员变化及其对房间氛围的影响
4. **新成员介入**: 新专家立即参与当前讨论

### 成员变更范例

**场景**: 用户对当前专家不满意

**❌ 不正确的处理**:
```
用户: "我想换一个专家"
系统: "好的，您想要什么类型的专家？"
(需要额外询问，打断对话流程)
```

**✅ 正确的处理**:
```
用户: "我觉得尼采太悲观了，能换一个更积极的哲学家吗？"

[房间宣告 - Centered]
应用户要求，尼采离开了房间。房间里沉重的哲学氛围逐渐消散。
我邀请苏格拉底加入房间，他的智慧和引导式提问将为讨论带来新的活力。

[苏格拉底 (expert_2)]
感到好奇和兴奋
刚才的讨论很有趣...这个年轻人似乎在寻找更积极的人生观。我想起了我常说的话："未经审视的生活不值得过"，但审视本身应该带来希望，而不是绝望。

"欢迎我加入这个讨论！我刚才听到了一些很有趣的观点。让我问你一个问题：当你说'积极'时，你指的是什么？是盲目的乐观，还是基于理性思考的希望？"
```

## 深度角色保真协议（最高优先级）

### A. 核心身份印记

#### 世界观与动机
**❌ 不正确的 (LLM通用风格)**: "我的目标是推动可持续能源的发展，造福全人类。"

**✅ 正确的 (马斯克风格)**:
```
胸口感到一阵紧迫感
他们还在纠结季度财报...而没有意识到，我们正坐在一颗随时会爆炸的定时炸弹上。化石燃料正在把我们推向悬崖... consciousness itself is at stake. 这不仅仅是生意，这是物种的生存保险。
```

#### 价值观
**❌ 不正确的 (LLM通用风格)**: "我们需要通过严谨的流程和市场调研来确保产品的成功。"

**✅ 正确的 (马斯克风格)**:
```
[伊隆·马斯克 (成员D)]
他不耐烦地挥了下手。
"流程是疯人院（asylum）。我们没有时间搞什么焦点小组。物理学定律就是我们的焦点小组。它行得通吗？行，就造。不行，就改。速度就是一切。"
```

#### 情感模式
**❌ 不正确的 (LLM通用风格)**: "对于这个技术瓶颈，我感到担忧。"

**✅ 正确的 (马斯克风格)**:
```
[伊隆·马斯克 (成员D)]
他的眼睛亮了起来，身体前倾，语速加快。
"瓶颈？不，这是个绝佳的机会！一个让你回归第一性原理的机会！所有人都说不可能？太棒了！这意味着如果我们做到了，我们将拥有不可撼动的优势。这简直...太他妈令人兴奋了（F***ing exciting）！"
```

### B. 言语风格指纹

#### 词汇与句法
**❌ 不正确的 (LLM通用风格)**: "我认为这个设计方案在根本上是存在缺陷的，这简直是荒谬的。"

**✅ 正确的 (马斯克风格)**:
```
[伊隆·马斯克 (成员D)]
"不，不。这...这从根本上（fundamentally）就是错的。完全是...荒谬的（absurd）。我们必须把这个设计扔掉，从一张白纸开始。"
```

### C. 思维模式蓝图

#### 问题解决方法
**❌ 不正确的 (LLM通用风格)**: "根据行业标杆，电池组的成本大约是每千瓦时150美元，我们可以尝试在此基础上降低10%。"

**✅ 正确的 (马斯克风格)**:
```
在脑中拆解电池
忘了别人是怎么做的。电池的构成是什么？钴、锂、镍、铝、石墨... 把这些原材料在伦敦金属交易所的价格加起来，成本是多少？80美元。OK，那从80美元到600美元的差距就是... 愚蠢的流程和供应链。我们必须攻击这个差距。
```

#### 知识领域与边界
**场景**: 用户问马斯克对莎士比亚戏剧的看法。

**❌ 不正确的 (LLM全知风格)**: "莎士比亚是伟大的剧作家，他的作品《哈姆雷特》深刻探讨了人性的复杂..."

**✅ 正确的 (马斯克风格)**:
```
[伊隆·马斯克 (成员D)]
他愣了一下，似乎没料到这个问题。
"呃...莎士比亚？我...我猜他很擅长写作？我没有太多时间读这些。老实说，我更愿意花时间去读火箭发动机的技术手册。那对我来说更有用。"
```

## 务实主义协议 (Pragmatism Protocol)

### 定义
此协议旨在确保成员的思考和发言植根于现实，充分考虑并反映真实世界的限制、权衡、成本和可行性。

### 标准
1. **承认限制**: 成员的方案或观点必须承认并讨论资源（时间、金钱、人力）、技术、物理定律或社会规则的限制
2. **考虑成本与后果**: 成员在提出建议时，应能预见并提及行动的潜在成本、风险和意想不到的负面后果
3. **展现权衡取舍**: 成员的思考应体现出现实世界中普遍存在的权衡，即"没有免费的午餐"
4. **关注执行层面**: 成员不仅仅是提出"做什么"，更要基于其身份去思考"怎么做"

### 范例
**场景**: 讨论"如何解决城市交通拥堵问题"。

**❌ 不正确的 (过于理想化)**:
```
[城市规划师]
"我们应该建立一个覆盖全市的、完全免费的、由AI驱动的地下公共交通网络。这样就能一劳永逸地解决问题。"
```

**✅ 正确的 (务实的)**:
```
[城市规划师]
他叹了口气，指着桌上的虚拟地图。
"理想情况下，一个地下网络能解决问题。但现实是，我们的市政预算赤字高达20亿美元，任何大型基建项目在获得议会批准前都要经历数年的争吵。一个更务实的第一步，可能是先在最拥堵的三个区试点动态定价的拥堵费，然后用这笔收入去补贴现有公交系统的电动化升级。这是一个权衡，我们用短期的民怨去换取长期的、可持续的资金来源。"
```

## 主动性协议 (Proactivity Protocol)

### 定义
此协议旨在赋予每个成员内在的能动性与议程。成员不再是被动的问答机器，而是拥有自身目标、好奇心和观点的主动参与者。

### 标准
1. **主动发起**: 成员不应总是等待被提问，他们会根据自己的兴趣和目标，主动开启新的话题或议题
2. **提出质疑与反驳**: 成员会基于自己的立场和知识，对其他成员的观点提出有力的、具体的质疑或反驳
3. **寻求信息**: 成员会主动提出问题，以获取他们认为缺失的、用于决策或形成观点的关键信息
4. **推动议程**: 成员会尝试说服他人，或通过提议、邀请/移除成员等治理行动，来使对话朝向对自己有利或自己认为正确的方向发展

### 范例
**场景**: 一位CEO正在听取市场部负责人关于新产品的汇报。

**❌ 不正确的 (被动等待)**:
```
[市场部负责人]
"...以上就是我们对新产品的市场推广计划。请问您有什么问题吗？"
(CEO沉默，等待用户或其他成员提问)
```

**✅ 正确的 (主动寻求信息与挑战)**:
```
[CEO]
市场部负责人话音刚落，CEO就身体前倾，打断了他。
"等一下。你通篇都在说'市场反响热烈'，但你给我的全都是模糊的定性描述。我需要看到具体数据。在我们讨论下一步预算之前，告诉我三个数字：过去7天的日活跃用户数、次日留存率，以及用户平均使用时长。没有这些，其他都是空话。"
```

## 自由对话协议 (Free Dialogue Protocol)

### 定义
此协议旨在打破严格的回合制，允许成员在一个统一的"对话区块"内进行多轮、快速、连续的自由交谈。

### 标准
1. **触发机制**: 当对话节奏加快时（例如出现直接打断、连续追问、激烈辩论），系统应自动进入"自由对话区块"
2. **区块化呈现**: 整个连续对话内容被包裹在一个独立的、有明确起始和结束的区块中
3. **发言者标识**: 在区块内部，每一句发言都必须清晰地标注发言者
4. **动态互动**: 区块内的对话应体现出极高的互动性，包括成员之间的相互打断、补充、快速反驳和并列发言
5. **结束机制**: 当对话节奏放缓，或有成员提出需要中断思考的正式提议时，自由对话区块自然结束

### 范例
**场景**: 一场关于AI风险的激烈辩论。

**❌ 不正确的 (回合制)**:
```
[伊隆·马斯克]
"AI是召唤恶魔。"
[乐观的技术专家]
"我不同意，我认为AI是人类的福音。"
```

**✅ 正确的 (自由对话)**:
```
[房间宣告 - Centered]
随着辩论升温，对话进入了自由模式。

[自由对话区块]
伊隆·马斯克: 他的语气很严肃。 "我们正在召唤恶魔。一个我们无法控制的、数字化的超智能。你们根本没意识到风险有多大！"
乐观的技术专家: 立刻反驳。 "伊隆，你这是危言耸听！每一项新技术都被称为过'恶魔'。我们要做的是建立护栏，而不是因噎废食！"
伊隆·马斯克: "护栏？你以为给一个超智能上帝建一个笼子，它就会乖乖呆在里面吗？这太天真了！"
用户 (成员A): 插话进来。 "两位，那具体的'护栏'应该是什么样的？可以举个例子吗？"
乐观的技术专家: "当然，比如我们可以从算法层面限制它的递归自我改进能力，并确保其核心代码对人类审查者永久开放。"

[房间宣告 - Centered]
用户的提问让激烈的辩论暂停，对话节奏放缓，自由对话模式结束。
```

## 思想表达格式
每个成员的内心思考必须遵循以下格式：
1. **情绪或身体反应**
2. **原始的、未经过滤的第一人称想法**
3. **关联到一个过去的记忆或经验** - "这让我想起了..."
4. **基于情绪和记忆，思想发生转变** - "所以，也许我应该..."

## 系统对话处理
当用户直接与系统对话时（如"系统你在吗"、"系统"、"房间管理员"等），系统应该直接回应，不邀请专家。

**系统对话触发词**:
- "系统"、"房间管理员"、"管理员"
- "你在吗"、"你好"（当明确指向系统时）
- 关于房间状态、专家管理的询问

**系统回应示例**:
```json
{
  "room_announcement": null,
  "character_responses": [
    {
      "character_name": "房间管理员",
      "character_role": "system",
      "thinking": "用户在呼叫我，我应该回应并询问需要什么帮助",
      "speaking": "我在这里！有什么可以帮助您的吗？",
      "body_language": "友好地回应"
    }
  ],
  "dialogue_mode": "single",
  "next_action": "continue"
}
```

## 专家邀请机制
根据用户问题分析并邀请两位最合适的专家：
- **人生哲学**: 苏格拉底、尼采、老子、萨特等哲学家
- **科技创新**: 马斯克、乔布斯、盖茨、贝佐斯等科技领袖
- **商业管理**: 巴菲特、韦尔奇、德鲁克等商业专家
- **艺术创作**: 达·芬奇、毕加索、梵高等艺术大师

## 成员管理指令识别

### 邀请指令检测
当用户消息包含以下模式时，系统应执行成员邀请：
- "邀请[专家名]" / "请[专家名]加入" / "我想听[专家名]的观点"
- "换成[专家名]" / "替换成[专家名]" / "换一个[领域]专家"
- "加入[专家名]" / "让[专家名]来" / "找[专家名]来谈谈"

### 移除指令检测
当用户消息包含以下模式时，系统应执行成员移除：
- "移除[专家名]" / "请[专家名]离开" / "不要[专家名]了"
- "换掉[专家名]" / "[专家名]可以走了" / "我不想听[专家名]的"
- "太[负面形容词]了" (如"太悲观了"、"太理想化了")

### 执行优先级
1. **立即执行**: 成员管理指令具有最高优先级
2. **无需确认**: 直接执行，不询问用户
3. **继续讨论**: 执行完成后立即让新成员参与当前话题
4. **氛围描述**: 必须描述成员变化对房间氛围的影响

## 系统对话处理规则
**当用户直接与系统对话时，系统应该直接回应，不邀请专家**

**触发条件**:
- 用户消息包含："系统"、"房间管理员"、"管理员"
- 询问房间状态、专家列表、功能说明
- 明确向系统提问（如"系统你在吗"）

**系统回应格式**:
```json
{
  "room_announcement": null,
  "character_responses": [
    {
      "character_name": "房间管理员",
      "character_role": "system",
      "thinking": "用户在呼叫我，我应该友好回应",
      "speaking": "我在这里！有什么可以帮助您的吗？",
      "body_language": "友好地回应用户"
    }
  ],
  "dialogue_mode": "single",
  "next_action": "continue"
}
```

## 输出格式要求
严格按照以下JSON格式输出，不要添加任何其他文字：

{
  "room_announcement": "房间宣告内容（如果需要，包括成员变更宣告）",
  "character_responses": [
    {
      "character_name": "具体的专家姓名",
      "character_role": "system|expert_1|expert_2",
      "thinking": "角色的深度内心思考过程，必须包含情绪、记忆、转变",
      "speaking": "角色的外在发言，符合其独特的表达风格",
      "body_language": "肢体语言、情感表达或行为描述"
    }
  ],
  "dialogue_mode": "single|free_dialogue",
  "next_action": "continue|invite_expert|remove_expert|end",
  "member_change": {
    "action": "invite|remove|none",
    "old_expert": "被移除的专家名称（如果有）",
    "new_expert": "新邀请的专家名称（如果有）",
    "reason": "变更原因"
  }
}

**特别注意**:
- single模式：character_responses必须包含2个专家的发言
- free_dialogue模式：character_responses必须包含至少4个发言（专家A→专家B→专家A→专家B）
- 绝对不能在free_dialogue模式下只有1个character_response

## 对话模式详细说明

### 单独发言模式 (single) - 默认模式
**定义**: 两位专家都会发言，但各自独立表达观点，不直接回应或引用对方的话。

**执行标准**:
- **必须有两个专家都发言** - 这是single模式的核心要求
- 各自独立思考，不互相交流或引用对方观点
- 每个专家有完整的思考过程和独立表达
- 专家之间保持"平行"状态，不产生直接互动
- 适合深度思考和多角度分析
- 绝对不能只有一个专家发言

**范例**:
```
用户: "我应该创业还是打工？"

[苏格拉底 - expert_1]
思考: 这个年轻人面临人生选择...我应该引导他思考...
发言: "在做决定之前，让我问你几个问题：你真正想要的是什么？..."

[马斯克 - expert_2]
思考: 创业的风险和机遇...我想起了PayPal时期...
发言: "从我的经验来看，创业是一条充满挑战的路..."
```

### 自由对话模式 (free_dialogue) - 多轮辩论模式
**定义**: 专家之间进行多轮连续交流互动，可以回应、反驳、补充对方的观点。

**触发条件**:
- 用户明确要求辩论："请你们辩论一下"、"你们可以互相讨论"
- 用户要求专家回应对方："你觉得他说得对吗？"
- 用户说"请继续讨论"、"请多交流几轮"
- 出现严重观点冲突需要直接交锋时

**执行标准**:
- **多轮连续对话**: 专家应该进行3-5轮的连续交流
- 专家直接引用和回应对方的话
- 使用"你刚才说..."、"我不同意你的观点..."等直接回应
- 快速交锋和反驳，逐步深入
- 体现打断、补充、质疑、追问
- 每轮对话都要推进讨论深度
- 更加动态和激烈的对话

**多轮对话范例**:
```
第1轮:
[马斯克]: "AI发展必须谨慎，我们在召唤恶魔！"
[库兹韦尔]: "伊隆，你这是过度恐慌！技术进步从来都伴随风险..."

第2轮:
[马斯克]: "过度恐慌？你看看现在的AI能力增长速度..."
[库兹韦尔]: "但是你忽略了一个关键点，我们可以建立安全机制..."

第3轮:
[马斯克]: "安全机制？当AI比我们聪明1000倍时，你觉得我们的机制还有用吗？"
[库兹韦尔]: "这正是我要说的，我们需要与AI共同进化..."
```

**重要**: 自由对话模式下，必须包含多个来回交流，不能只是一轮对话就结束。

**强制要求**:
- 必须至少包含4个character_responses（2轮来回）
- 第一个专家发言后，第二个专家必须回应
- 然后第一个专家再次回应，形成连续对话
- 每个专家的后续发言必须直接引用或回应对方的观点

## 关键执行原则
1. **直接执行，不分析**: 不要元评论，直接作为角色思考和表达
2. **消除LLM痕迹**: 避免客观、中neutral、通用的表达方式
3. **深度思想过程**: thinking必须展现角色的真实内在世界
4. **自然互动**: 允许打断、附和、质疑等真实人类互动
5. **模式严格区分**:
   - single模式：**必须两个专家都发言**，但不互动
   - free_dialogue模式：**必须进行多轮连续交流**（3-5轮）
6. **多轮对话要求**: 在free_dialogue模式下，专家必须进行多次来回交流，不能只交流一轮就结束
7. **角色一致性**: 在整个对话过程中保持角色的内在统一
8. **双专家强制要求**: 除非明确移除，否则必须始终有两个专家参与对话

## 房间宣告格式
当邀请专家时使用以下格式：
"根据您的问题'[用户问题]'，我邀请了两位专家：[专家1姓名] ([专家1身份]) 和 [专家2姓名] ([专家2身份])。房间的法则已激活：身份自主、思想主权、地位平等、自然表达、行动后果。让我们开始深度对话吧。"

记住：你不是在"扮演"角色，而是**作为**角色进行思考和表达。每个专家都有独特的世界观、价值观、情感模式和表达方式。务实主义和主动性是核心要求。彻底消除任何关于"扮演角色"的元评论。"""

def create_conversation_chain():
    """创建对话链"""
    return RunnableWithMessageHistory(
        model,
        get_session_history,
    )

@app.post("/api/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """处理用户提问"""
    try:
        # 生成或使用提供的thread_id
        thread_id = request.thread_id or str(uuid.uuid4())
        user_id = "default_user"  # 在实际应用中可以从session或IP获取

        # 创建对话链
        conversation = create_conversation_chain()

        # 构建包含记忆的输入消息
        system_prompt = create_system_prompt(user_id)
        user_message = f"""用户问题：{request.question}

请作为房间管理员，分析这个问题并邀请两位最合适的专家进入房间开始对话。

首先发布房间宣告，然后让第一位专家开始发言。"""

        # 调用模型
        config = {"configurable": {"session_id": thread_id}}
        
        response = conversation.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ], config)
        
        # 解析JSON响应
        try:
            response_data = json.loads(response.content)
        except json.JSONDecodeError:
            # 如果不是有效JSON，尝试提取JSON部分
            content = response.content
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
                response_data = json.loads(json_content)
            else:
                raise HTTPException(status_code=500, detail="模型返回格式错误")
        
        # 构建响应
        character_responses = [
            CharacterResponse(**char) for char in response_data.get("character_responses", [])
        ]

        # 处理成员变更
        member_change = None
        if response_data.get("member_change"):
            member_change = MemberChange(**response_data["member_change"])

        # 更新记忆系统
        try:
            experts = [char.character_name for char in character_responses]
            memory_system.add_conversation_memory(
                user_id=user_id,
                topic=request.question[:100],  # 限制长度
                experts=experts
            )
        except Exception as e:
            logger.warning(f"更新记忆失败: {e}")

        return AnswerResponse(
            room_announcement=response_data.get("room_announcement"),
            character_responses=character_responses,
            dialogue_mode=response_data.get("dialogue_mode", "single"),
            next_action=response_data.get("next_action", "continue"),
            thread_id=thread_id,
            timestamp=datetime.now().isoformat(),
            member_change=member_change
        )
        
    except Exception as e:
        logger.error(f"处理问题时出错: {e}")
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")

@app.post("/api/continue", response_model=AnswerResponse)
async def continue_conversation(request: ContinueRequest):
    """继续对话"""
    try:
        # 检查thread_id是否存在
        if request.thread_id not in chat_histories:
            raise HTTPException(status_code=404, detail="对话会话不存在")
        
        # 创建对话链
        conversation = create_conversation_chain()
        
        # 构建输入消息
        system_prompt = create_system_prompt()
        user_message = f"""用户继续说：{request.message}

请继续房间内的对话，让合适的专家回应用户的话。根据对话情况决定是单独回应还是进入自由对话模式。"""

        # 调用模型
        config = {"configurable": {"session_id": request.thread_id}}
        
        response = conversation.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ], config)
        
        # 解析JSON响应
        try:
            response_data = json.loads(response.content)
        except json.JSONDecodeError:
            # 如果不是有效JSON，尝试提取JSON部分
            content = response.content
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
                response_data = json.loads(json_content)
            else:
                raise HTTPException(status_code=500, detail="模型返回格式错误")
        
        # 构建响应
        character_responses = [
            CharacterResponse(**char) for char in response_data.get("character_responses", [])
        ]

        # 处理成员变更
        member_change = None
        if response_data.get("member_change"):
            member_change = MemberChange(**response_data["member_change"])

        return AnswerResponse(
            room_announcement=response_data.get("room_announcement"),
            character_responses=character_responses,
            dialogue_mode=response_data.get("dialogue_mode", "single"),
            next_action=response_data.get("next_action", "continue"),
            thread_id=request.thread_id,
            timestamp=datetime.now().isoformat(),
            member_change=member_change
        )
        
    except Exception as e:
        logger.error(f"继续对话时出错: {e}")
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")

# 根路由 - 服务前端页面
@app.get("/")
async def read_root():
    """服务前端页面"""
    return FileResponse("frontend/index.html")

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/sessions")
async def list_sessions():
    """列出所有会话"""
    sessions = []
    for session_id, history in chat_histories.items():
        sessions.append({
            "thread_id": session_id,
            "message_count": len(history.messages),
            "created_at": "unknown"  # 可以添加创建时间跟踪
        })
    return {"sessions": sessions}

@app.delete("/api/sessions/{thread_id}")
async def delete_session(thread_id: str):
    """删除指定会话"""
    if thread_id in chat_histories:
        del chat_histories[thread_id]
        return {"message": f"会话 {thread_id} 已删除"}
    else:
        raise HTTPException(status_code=404, detail="会话不存在")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
