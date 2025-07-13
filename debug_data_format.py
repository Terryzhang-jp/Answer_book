#!/usr/bin/env python3
"""
调试脚本：检查数据格式不匹配问题
"""

import sys
import os

# 添加后端路径
backend_path = os.path.join(os.path.dirname(__file__), 'room_protocol_backend')
sys.path.insert(0, backend_path)

try:
    from core.services.global_storage import global_storage
    from langchain_core.messages import BaseMessage
except ImportError as e:
    print(f"导入错误: {e}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"后端路径: {backend_path}")
    sys.exit(1)

def debug_data_format():
    """调试数据格式问题"""
    print("=== 数据格式调试 ===")
    
    # 获取所有线程ID
    thread_ids = global_storage.get_all_thread_ids()
    print(f"找到 {len(thread_ids)} 个线程")
    
    if not thread_ids:
        print("❌ 没有找到任何线程数据")
        return
    
    # 检查第一个线程的数据
    thread_id = thread_ids[0]
    print(f"\n检查线程: {thread_id}")
    
    # 获取消息
    messages = global_storage.get_messages(thread_id)
    print(f"消息数量: {len(messages)}")
    
    if messages:
        first_message = messages[0]
        print(f"第一条消息类型: {type(first_message)}")
        print(f"是否为BaseMessage: {isinstance(first_message, BaseMessage)}")
        print(f"是否为dict: {isinstance(first_message, dict)}")
        
        if isinstance(first_message, BaseMessage):
            print(f"消息内容: {first_message.content[:100]}...")
        elif isinstance(first_message, dict):
            print(f"字典内容: {first_message}")
        
        # 检查所有消息的类型
        message_types = [type(msg).__name__ for msg in messages]
        print(f"所有消息类型: {set(message_types)}")
        
        # 检查是否有dict类型的消息
        dict_messages = [msg for msg in messages if isinstance(msg, dict)]
        print(f"dict类型消息数量: {len(dict_messages)}")
        
        # 检查BaseMessage类型的消息
        base_message_count = [msg for msg in messages if isinstance(msg, BaseMessage)]
        print(f"BaseMessage类型消息数量: {len(base_message_count)}")
        
        # 模拟报告服务的验证逻辑
        print("\n=== 模拟报告服务验证 ===")
        valid_messages = [msg for msg in messages if msg and isinstance(msg, dict)]
        print(f"报告服务认为有效的消息数量: {len(valid_messages)}")
        
        if len(valid_messages) == 0:
            print("❌ 报告服务会认为数据格式无效")
        elif len(valid_messages) < 2:
            print("❌ 报告服务会认为数据不足")
        else:
            print("✅ 报告服务会认为数据有效")

if __name__ == "__main__":
    debug_data_format()
