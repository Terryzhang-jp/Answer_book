#!/usr/bin/env python3
"""
Insight生成功能调试脚本
专门用于调试insight生成过程中的问题
"""

import requests
import json
import sys
from typing import Dict, Any

# API配置
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def test_insight_generation_step_by_step():
    """逐步测试insight生成过程"""
    print("🔍 开始逐步调试insight生成过程...")
    print("=" * 60)
    
    # 1. 首先创建一个简单的对话
    print("\n📋 步骤1: 创建测试对话")
    room_data = {
        "question": "什么是智慧？",
        "user_id": "debug_user"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/room/create", headers=HEADERS, json=room_data, timeout=30)
        response.raise_for_status()
        room_result = response.json()
        thread_id = room_result.get("thread_id")
        
        print(f"✅ 对话创建成功")
        print(f"   Thread ID: {thread_id}")
        print(f"   房间宣告: {room_result.get('room_announcement', '')[:100]}...")
        
        # 显示专家回答
        character_responses = room_result.get('character_responses', [])
        print(f"   专家数量: {len(character_responses)}")
        for i, char in enumerate(character_responses):
            print(f"   专家{i+1}: {char.get('character_name', 'Unknown')}")
            print(f"     思考: {char.get('thinking', '')[:50]}...")
            print(f"     发言: {char.get('speaking', '')[:50]}...")
        
    except Exception as e:
        print(f"❌ 创建对话失败: {e}")
        return
    
    # 2. 等待一下，然后测试insight生成
    print(f"\n📋 步骤2: 生成insight")
    insight_data = {
        "user_id": "debug_user",
        "thread_id": thread_id
    }
    
    try:
        print("🔄 正在调用insight API...")
        response = requests.post(f"{BASE_URL}/api/insight/generate", headers=HEADERS, json=insight_data, timeout=30)
        
        print(f"📊 HTTP状态码: {response.status_code}")
        print(f"📊 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API调用成功")
            print(f"   成功状态: {result.get('success')}")
            print(f"   会话ID: {result.get('session_id')}")
            print(f"   分析摘要: {result.get('analysis_summary')}")
            print(f"   🌟 生成的Insight: \"{result.get('insight')}\"")
            
            # 检查是否是默认值
            insight = result.get('insight', '')
            if insight == "言有尽而意无穷，思无涯而道自明。":
                print("⚠️  这是默认值！说明LLM返回了空内容")
            else:
                print("✅ 这是LLM生成的新内容！")
                
        else:
            print(f"❌ API调用失败")
            print(f"   响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ insight生成失败: {e}")
        return
    
    # 3. 直接测试LLM调用
    print(f"\n📋 步骤3: 直接测试LLM调用")
    test_direct_llm_call()

def test_direct_llm_call():
    """直接测试LLM调用"""
    print("🤖 测试直接LLM调用...")
    
    # 模拟一个简单的对话数据
    test_data = {
        "user_questions": ["什么是智慧？"],
        "guest_responses": [
            {
                "character_name": "苏格拉底",
                "thinking": "这是一个古老而深刻的问题。智慧不仅仅是知识的积累，更是对无知的认知。",
                "speaking": "我知道的唯一一件事，就是我什么都不知道。真正的智慧在于认识到自己的无知，并保持对真理的渴望。智慧不是拥有答案，而是提出正确的问题。"
            }
        ]
    }
    
    # 构建prompt
    system_prompt = """你是一位智慧的哲学家，擅长用优美的语言表达深刻的道理。

请根据对话内容，生成一句优美的智慧箴言。

要求：
1. 不超过15个字
2. 语言优美，富有诗意
3. 表达深刻的人生哲理

风格参考：
- "心之所向，道之所在"
- "知者不言，言者不知"  
- "山重水复疑无路，柳暗花明又一村"

只返回一句箴言。"""

    user_prompt = f"""请分析以下对话，提炼出一句优美的智慧箴言：

用户问题：
{test_data['user_questions'][0]}

智者回答：
{test_data['guest_responses'][0]['speaking']}

请生成一句富有诗意和哲理的箴言："""

    print(f"📝 System Prompt:")
    print(f"   {system_prompt[:100]}...")
    print(f"📝 User Prompt:")
    print(f"   {user_prompt[:100]}...")
    
    # 这里我们无法直接调用LLM，但可以检查prompt的构建
    print("✅ Prompt构建完成")
    print("💡 建议：检查后端日志中LLM的实际响应内容")

def test_with_different_questions():
    """测试不同类型的问题"""
    print(f"\n📋 步骤4: 测试不同类型的问题")
    
    test_questions = [
        "人生的意义是什么？",
        "如何获得内心的平静？", 
        "什么是真正的友谊？",
        "如何面对失败？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔸 测试问题 {i}: {question}")
        
        # 创建对话
        room_data = {
            "question": question,
            "user_id": f"debug_user_{i}"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/room/create", headers=HEADERS, json=room_data, timeout=30)
            if response.status_code == 200:
                room_result = response.json()
                thread_id = room_result.get("thread_id")
                
                # 生成insight
                insight_data = {
                    "user_id": f"debug_user_{i}",
                    "thread_id": thread_id
                }
                
                insight_response = requests.post(f"{BASE_URL}/api/insight/generate", headers=HEADERS, json=insight_data, timeout=30)
                if insight_response.status_code == 200:
                    insight_result = insight_response.json()
                    insight = insight_result.get('insight', '')
                    
                    if insight == "言有尽而意无穷，思无涯而道自明。":
                        print(f"   ❌ 默认值: {insight}")
                    else:
                        print(f"   ✅ 新生成: {insight}")
                else:
                    print(f"   ❌ Insight生成失败: {insight_response.status_code}")
            else:
                print(f"   ❌ 对话创建失败: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")

def check_backend_health():
    """检查后端健康状态"""
    print("🏥 检查后端健康状态...")
    
    try:
        # 检查insight健康状态
        response = requests.get(f"{BASE_URL}/api/insight/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Insight服务正常")
            print(f"   模型状态: {health_data.get('model_status')}")
            print(f"   活跃会话: {health_data.get('active_sessions')}")
        else:
            print(f"⚠️ Insight服务异常: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 无法连接Insight服务: {e}")

def main():
    """主函数"""
    print("🐛 Insight生成功能调试脚本")
    print("专门用于调试insight生成过程中的问题")
    print("=" * 60)
    
    # 检查后端健康状态
    check_backend_health()
    
    # 逐步测试
    test_insight_generation_step_by_step()
    
    # 测试不同问题
    test_with_different_questions()
    
    print("\n" + "=" * 60)
    print("🎯 调试建议:")
    print("1. 检查后端日志中LLM的实际响应")
    print("2. 确认LLM模型是否正常工作")
    print("3. 检查prompt是否过于复杂")
    print("4. 验证对话数据是否正确传递给LLM")
    print("🎉 调试完成!")

if __name__ == "__main__":
    main()
