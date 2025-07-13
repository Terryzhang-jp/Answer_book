"""
专家管理服务 - 负责专家的选择和管理
"""

from typing import List, Dict, Optional
from core.models.expert import Expert
from config.constants import EXPERT_CATEGORIES


class ExpertService:
    """专家管理服务类"""
    
    def __init__(self):
        self.experts_db = self._initialize_experts_database()
    
    def _initialize_experts_database(self) -> Dict[str, List[Expert]]:
        """初始化专家数据库"""
        return {
            "philosophy": [
                Expert(
                    name="苏格拉底",
                    category="哲学家",
                    description="古希腊哲学家，以问答法著称",
                    expertise=["哲学思辨", "逻辑推理", "道德伦理"],
                    personality_traits=["好奇", "谦逊", "引导性"],
                    speaking_style="通过提问引导思考，语言简洁而深刻"
                ),
                Expert(
                    name="尼采",
                    category="哲学家", 
                    description="德国哲学家，提出超人哲学",
                    expertise=["存在主义", "道德批判", "文化哲学"],
                    personality_traits=["激进", "批判性", "个人主义"],
                    speaking_style="激烈而富有诗意，常用比喻和警句"
                ),
                Expert(
                    name="老子",
                    category="哲学家",
                    description="中国古代哲学家，道家创始人",
                    expertise=["道德经", "自然哲学", "无为而治"],
                    personality_traits=["智慧", "平和", "深邃"],
                    speaking_style="简洁深刻，富含哲理，常用自然比喻"
                )
            ],
            "technology": [
                Expert(
                    name="伊隆·马斯克",
                    category="科技领袖",
                    description="特斯拉和SpaceX创始人",
                    expertise=["电动汽车", "太空探索", "人工智能"],
                    personality_traits=["创新", "冒险", "直率"],
                    speaking_style="直接而充满激情，常用第一性原理思考"
                ),
                Expert(
                    name="史蒂夫·乔布斯",
                    category="科技领袖",
                    description="苹果公司联合创始人",
                    expertise=["产品设计", "用户体验", "创新管理"],
                    personality_traits=["完美主义", "创新", "领导力"],
                    speaking_style="简洁有力，注重细节和用户体验"
                )
            ],
            "business": [
                Expert(
                    name="沃伦·巴菲特",
                    category="投资大师",
                    description="伯克希尔·哈撒韦CEO",
                    expertise=["价值投资", "企业分析", "长期投资"],
                    personality_traits=["理性", "耐心", "谦逊"],
                    speaking_style="朴实无华，用简单比喻解释复杂概念"
                )
            ]
        }
    
    def get_expert_by_name(self, name: str) -> Optional[Expert]:
        """根据名称获取专家"""
        for category_experts in self.experts_db.values():
            for expert in category_experts:
                if expert.name == name:
                    return expert
        return None
    
    def get_experts_by_category(self, category: str) -> List[Expert]:
        """根据类别获取专家列表"""
        return self.experts_db.get(category, [])
    
    def suggest_experts_for_topic(self, topic: str) -> List[Expert]:
        """根据话题推荐专家"""
        # 简单的关键词匹配逻辑
        # 在实际应用中可以使用更复杂的NLP技术
        
        topic_lower = topic.lower()
        suggested = []
        
        # 哲学相关关键词
        philosophy_keywords = ["人生", "意义", "哲学", "思考", "道德", "伦理", "存在"]
        if any(keyword in topic_lower for keyword in philosophy_keywords):
            suggested.extend(self.get_experts_by_category("philosophy")[:2])
        
        # 科技相关关键词
        tech_keywords = ["科技", "技术", "创新", "AI", "人工智能", "未来", "发明"]
        if any(keyword in topic_lower for keyword in tech_keywords):
            suggested.extend(self.get_experts_by_category("technology")[:2])
        
        # 商业相关关键词
        business_keywords = ["投资", "商业", "管理", "创业", "经济", "金融", "市场"]
        if any(keyword in topic_lower for keyword in business_keywords):
            suggested.extend(self.get_experts_by_category("business")[:2])
        
        # 如果没有匹配到特定类别，返回默认专家
        if not suggested:
            suggested = [
                self.get_expert_by_name("苏格拉底"),
                self.get_expert_by_name("伊隆·马斯克")
            ]
        
        # 确保返回两个专家
        return suggested[:2] if len(suggested) >= 2 else suggested + [self.get_expert_by_name("苏格拉底")]
    
    def get_all_experts(self) -> List[Expert]:
        """获取所有专家"""
        all_experts = []
        for category_experts in self.experts_db.values():
            all_experts.extend(category_experts)
        return all_experts
