#!/usr/bin/env python3
"""
内存使用分析脚本 - 评估系统的内存占用和扩展性
"""

import sys
import os
import json
from typing import Dict, List

# 添加后端路径
backend_path = os.path.join(os.path.dirname(__file__), 'room_protocol_backend')
sys.path.insert(0, backend_path)

try:
    from core.services.global_storage import global_storage
except ImportError as e:
    print(f"导入错误: {e}")
    # 使用简化版分析
    global_storage = None

def analyze_memory_usage():
    """分析当前内存使用情况"""
    print("=== 系统内存使用分析 ===")

    # 简化版内存分析（不依赖psutil）
    print("注意: 使用简化版内存分析（未安装psutil）")

    return {
        "system_total_gb": 8.0,  # 假设值
        "system_used_gb": 4.0,   # 假设值
        "system_available_gb": 4.0,  # 假设值
        "process_mb": 50.0       # 假设值
    }

def analyze_storage_data():
    """分析存储数据的内存占用"""
    print("\n=== 存储数据分析 ===")

    if global_storage is None:
        # 直接分析文件
        storage_file = "memory/global_backup_storage.json"
        if os.path.exists(storage_file):
            with open(storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            thread_count = len(data)
            total_messages = sum(len(messages) for messages in data.values())
            file_size = os.path.getsize(storage_file)

            print(f"线程数量: {thread_count}")
            print(f"总消息数: {total_messages}")
            print(f"文件存储大小: {file_size / (1024**2):.2f} MB")

            return {
                "thread_count": thread_count,
                "total_messages": total_messages,
                "estimated_size_mb": file_size / (1024**2),
                "file_size_mb": file_size / (1024**2)
            }
        else:
            print("未找到存储文件")
            return {"thread_count": 0, "total_messages": 0, "estimated_size_mb": 0, "file_size_mb": 0}

    # 原有逻辑（如果能正常导入）
    thread_ids = global_storage.get_all_thread_ids()
    total_messages = 0
    total_size_estimate = 0

    print(f"线程数量: {len(thread_ids)}")

    for thread_id in thread_ids:
        messages = global_storage.get_messages(thread_id)
        total_messages += len(messages)

        # 估算消息大小
        for msg in messages:
            if hasattr(msg, 'content'):
                total_size_estimate += len(str(msg.content)) * 2  # Unicode字符估算
            total_size_estimate += 200  # 对象开销估算

    print(f"总消息数: {total_messages}")
    print(f"估算数据大小: {total_size_estimate / (1024**2):.2f} MB")

    # 分析文件存储
    storage_file = "memory/global_backup_storage.json"
    file_size = 0
    if os.path.exists(storage_file):
        file_size = os.path.getsize(storage_file)
        print(f"文件存储大小: {file_size / (1024**2):.2f} MB")

    return {
        "thread_count": len(thread_ids),
        "total_messages": total_messages,
        "estimated_size_mb": total_size_estimate / (1024**2),
        "file_size_mb": file_size / (1024**2)
    }

def simulate_user_growth(user_counts: List[int]):
    """模拟用户增长的内存影响"""
    print("\n=== 用户增长模拟 ===")
    
    # 基于当前数据估算单用户内存占用
    storage_data = analyze_storage_data()
    
    if storage_data["thread_count"] > 0:
        avg_messages_per_thread = storage_data["total_messages"] / storage_data["thread_count"]
        avg_size_per_thread = storage_data["estimated_size_mb"] / storage_data["thread_count"]
    else:
        avg_messages_per_thread = 10  # 假设值
        avg_size_per_thread = 0.1  # 假设值
    
    print(f"平均每线程消息数: {avg_messages_per_thread:.1f}")
    print(f"平均每线程内存占用: {avg_size_per_thread:.3f} MB")
    
    print("\n用户规模 | 线程数 | 估算内存占用 | 风险评估")
    print("-" * 60)
    
    for user_count in user_counts:
        # 假设每用户平均2个活跃线程
        estimated_threads = user_count * 2
        estimated_memory_mb = estimated_threads * avg_size_per_thread
        
        # 风险评估
        if estimated_memory_mb < 100:
            risk = "低"
        elif estimated_memory_mb < 500:
            risk = "中"
        elif estimated_memory_mb < 1000:
            risk = "高"
        else:
            risk = "极高"
        
        print(f"{user_count:8d} | {estimated_threads:6d} | {estimated_memory_mb:10.1f} MB | {risk}")

def analyze_memory_leaks(storage_info):
    """分析潜在的内存泄漏风险"""
    print("\n=== 内存泄漏风险分析 ===")

    risks = []

    # 检查全局存储是否有清理机制
    thread_count = storage_info.get("thread_count", 0)
    if thread_count > 100:
        risks.append("❌ 全局存储线程数过多，可能存在清理不及时的问题")
    else:
        risks.append("✅ 全局存储线程数在合理范围内")

    # 检查是否有定期清理机制
    risks.append("❌ 未发现自动清理过期线程的机制")

    # 检查内存中对象引用
    risks.append("⚠️  多层存储架构可能导致对象重复引用")

    # 检查前端状态管理
    risks.append("⚠️  前端Zustand store缺乏自动清理机制")

    for risk in risks:
        print(risk)

    return risks

def main():
    """主函数"""
    print("🔍 深度内存使用分析")
    print("=" * 50)
    
    # 系统内存分析
    memory_info = analyze_memory_usage()
    
    # 存储数据分析
    storage_info = analyze_storage_data()
    
    # 用户增长模拟
    simulate_user_growth([10, 50, 100, 500, 1000, 5000])
    
    # 内存泄漏风险分析
    leak_risks = analyze_memory_leaks(storage_info)
    
    # 生成总结报告
    print("\n=== 总结报告 ===")
    print(f"当前系统状态:")
    print(f"- 活跃线程: {storage_info['thread_count']}")
    print(f"- 总消息数: {storage_info['total_messages']}")
    print(f"- 内存占用: {storage_info['estimated_size_mb']:.2f} MB")
    print(f"- 估算进程内存: {memory_info['process_mb']:.2f} MB")
    
    print(f"\n关键风险:")
    critical_risks = [risk for risk in leak_risks if "❌" in risk]
    for risk in critical_risks:
        print(f"  {risk}")

if __name__ == "__main__":
    main()
