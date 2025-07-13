"""
应用常量定义
"""

# 对话模式
DIALOGUE_MODES = {
    "SINGLE": "single",
    "FREE_DIALOGUE": "free_dialogue"
}

# 角色类型
CHARACTER_ROLES = {
    "SYSTEM": "system",
    "EXPERT_1": "expert_1", 
    "EXPERT_2": "expert_2"
}

# 下一步行动
NEXT_ACTIONS = {
    "CONTINUE": "continue",
    "INVITE_EXPERT": "invite_expert",
    "REMOVE_EXPERT": "remove_expert",
    "END": "end"
}

# 成员变更行动
MEMBER_ACTIONS = {
    "INVITE": "invite",
    "REMOVE": "remove", 
    "NONE": "none"
}

# 专家类别
EXPERT_CATEGORIES = {
    "PHILOSOPHY": "人生哲学",
    "TECHNOLOGY": "科技创新", 
    "BUSINESS": "商业管理",
    "ART": "艺术创作",
    "SCIENCE": "科学研究",
    "PSYCHOLOGY": "心理学",
    "HISTORY": "历史学",
    "LITERATURE": "文学"
}

# 系统对话触发词
SYSTEM_TRIGGER_WORDS = [
    "系统", "房间管理员", "管理员", "房间", "系统你在吗"
]

# 多轮对话触发词
MULTI_ROUND_TRIGGER_WORDS = [
    "辩论", "讨论", "交流", "多轮", "深入", "来回", "互动"
]
