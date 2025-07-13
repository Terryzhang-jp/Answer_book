"""
全局存储管理器 - 用于在不同服务实例之间共享对话数据
"""

import json
import os
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from loguru import logger
from config.settings import get_settings


class GlobalStorage:
    """全局存储管理器，用于跨服务实例共享数据 - 支持分片存储"""

    _instance = None
    _backup_storage: Dict[str, List[BaseMessage]] = {}
    _thread_timestamps: Dict[str, datetime] = {}  # 线程最后活跃时间
    _storage_file = "memory/global_backup_storage.json"  # 兼容旧版本

    def __init__(self):
        self.settings = get_settings()
        # 分片存储配置
        self.shard_count = self.settings.STORAGE_SHARD_COUNT
        self.base_path = Path(self.settings.STORAGE_BASE_PATH)
        self.enable_sharding = self.settings.STORAGE_ENABLE_SHARDING
        self.max_shard_size_mb = self.settings.STORAGE_MAX_SHARD_SIZE_MB

        # 确保存储目录存在
        self.base_path.mkdir(parents=True, exist_ok=True)

        # 配置参数
        self.TTL_HOURS = 24  # 线程过期时间（小时）
        self.MAX_THREADS = 1000  # 最大线程数
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalStorage, cls).__new__(cls)
            cls._instance.__init__()
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """初始化全局存储"""
        if self.enable_sharding:
            logger.info("启用分片存储模式")
            self._load_from_shards()
        else:
            logger.info("使用传统单文件存储模式")
            self._load_from_file()
        logger.info("全局存储管理器初始化完成")

    def _get_shard_id(self, thread_id: str) -> int:
        """根据thread_id计算分片ID"""
        # 使用MD5哈希确保分布均匀
        hash_value = hashlib.md5(thread_id.encode()).hexdigest()
        return int(hash_value, 16) % self.shard_count

    def _get_shard_path(self, shard_id: int) -> Path:
        """获取分片文件路径"""
        return self.base_path / f"shard_{shard_id:03d}.json"

    def _get_user_id_from_thread(self, thread_id: str) -> str:
        """从thread_id提取user_id（如果可能）"""
        # 尝试从thread_id中提取user_id
        # 如果thread_id包含user信息，可以在这里解析
        # 目前使用thread_id本身作为分片依据
        return thread_id
    
    def save_messages(self, thread_id: str, messages: List[BaseMessage]):
        """保存消息到全局存储"""
        # 先保存数据到内存
        self._backup_storage[thread_id] = messages.copy()
        self._thread_timestamps[thread_id] = datetime.now()  # 更新活跃时间

        # 然后执行清理检查（保存后触发，确保当前线程不被误删）
        self._cleanup_expired_threads()
        self._cleanup_excess_threads()

        # 保存到文件（分片或单文件）
        if self.enable_sharding:
            self._save_to_shard(thread_id, messages)
        else:
            self._save_to_file()

        logger.info(f"全局存储保存成功，线程ID: {thread_id}, 消息数: {len(messages)}, 总线程数: {len(self._backup_storage)}")
    
    def get_messages(self, thread_id: str) -> List[BaseMessage]:
        """从全局存储获取消息"""
        # 先尝试从内存获取
        if thread_id in self._backup_storage:
            self._thread_timestamps[thread_id] = datetime.now()
            messages = self._backup_storage[thread_id]
        else:
            # 如果内存中没有，尝试从分片文件加载
            if self.enable_sharding:
                messages = self._load_from_shard(thread_id)
                if messages:
                    # 加载到内存中
                    self._backup_storage[thread_id] = messages
                    self._thread_timestamps[thread_id] = datetime.now()
            else:
                messages = []

        logger.info(f"全局存储检索结果 - 线程ID: {thread_id}, 消息数: {len(messages)}")
        return messages
    
    def _save_to_file(self):
        """将存储数据保存到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self._storage_file), exist_ok=True)

            # 将消息转换为可序列化的格式
            serializable_data = {
                "threads": {},
                "timestamps": {},
                "metadata": {
                    "ttl_hours": self.TTL_HOURS,
                    "max_threads": self.MAX_THREADS,
                    "last_saved": datetime.now().isoformat()
                }
            }

            # 保存消息数据
            for thread_id, messages in self._backup_storage.items():
                serializable_data["threads"][thread_id] = []
                for msg in messages:
                    msg_data = {
                        "type": msg.__class__.__name__,
                        "content": msg.content
                    }
                    if hasattr(msg, 'additional_kwargs'):
                        msg_data["additional_kwargs"] = msg.additional_kwargs
                    serializable_data["threads"][thread_id].append(msg_data)

            # 保存时间戳数据
            for thread_id, timestamp in self._thread_timestamps.items():
                serializable_data["timestamps"][thread_id] = timestamp.isoformat()

            # 保存到文件
            with open(self._storage_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, ensure_ascii=False, indent=2)

            logger.debug(f"全局存储数据已保存到文件: {self._storage_file}")
        except Exception as e:
            logger.error(f"保存全局存储数据到文件失败: {e}")
    
    def _load_from_file(self):
        """从文件加载存储数据"""
        try:
            if not os.path.exists(self._storage_file):
                logger.info("全局存储文件不存在，使用空存储")
                return

            with open(self._storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 兼容旧格式和新格式
            if "threads" in data and "timestamps" in data:
                # 新格式：包含时间戳
                threads_data = data["threads"]
                timestamps_data = data.get("timestamps", {})

                # 加载时间戳
                self._thread_timestamps = {}
                for thread_id, timestamp_str in timestamps_data.items():
                    try:
                        self._thread_timestamps[thread_id] = datetime.fromisoformat(timestamp_str)
                    except ValueError:
                        # 如果时间戳格式错误，使用当前时间
                        self._thread_timestamps[thread_id] = datetime.now()

                logger.info(f"加载新格式存储文件，TTL: {data.get('metadata', {}).get('ttl_hours', 'unknown')}小时")
            else:
                # 旧格式：直接是线程数据
                threads_data = data
                # 为旧数据设置默认时间戳
                self._thread_timestamps = {thread_id: datetime.now() for thread_id in threads_data.keys()}
                logger.info("加载旧格式存储文件，为所有线程设置当前时间戳")

            # 将数据转换回消息对象
            self._backup_storage = {}
            for thread_id, messages_data in threads_data.items():
                messages = []
                for msg_data in messages_data:
                    msg_type = msg_data.get("type", "HumanMessage")
                    content = msg_data.get("content", "")
                    additional_kwargs = msg_data.get("additional_kwargs", {})

                    if msg_type == "HumanMessage":
                        msg = HumanMessage(content=content, additional_kwargs=additional_kwargs)
                    elif msg_type == "AIMessage":
                        msg = AIMessage(content=content, additional_kwargs=additional_kwargs)
                    elif msg_type == "SystemMessage":
                        msg = SystemMessage(content=content, additional_kwargs=additional_kwargs)
                    else:
                        # 默认使用HumanMessage
                        msg = HumanMessage(content=content, additional_kwargs=additional_kwargs)

                    messages.append(msg)

                self._backup_storage[thread_id] = messages

            logger.info(f"从文件加载全局存储数据成功，包含{len(self._backup_storage)}个线程")

            # 加载后立即执行一次清理
            self._cleanup_expired_threads()
            self._cleanup_excess_threads()

        except Exception as e:
            logger.error(f"从文件加载全局存储数据失败: {e}")
            self._backup_storage = {}
            self._thread_timestamps = {}
    
    def get_all_thread_ids(self) -> List[str]:
        """获取所有线程ID"""
        return list(self._backup_storage.keys())

    def has_messages(self, thread_id: str) -> bool:
        """检查是否存在指定线程的消息"""
        return thread_id in self._backup_storage

    def clear_thread(self, thread_id: str):
        """清除指定线程的数据"""
        # 从内存中清除
        if thread_id in self._backup_storage:
            del self._backup_storage[thread_id]
        if thread_id in self._thread_timestamps:
            del self._thread_timestamps[thread_id]

        # 从分片文件中清除
        if self.enable_sharding:
            self._clear_from_shard(thread_id)
        else:
            self._save_to_file()

        logger.info(f"已清除线程数据: {thread_id}")
    
    def clear_all(self):
        """清除所有数据"""
        self._backup_storage.clear()
        self._thread_timestamps.clear()
        self._save_to_file()
        logger.info("已清除所有全局存储数据")

    def _cleanup_expired_threads(self):
        """清理过期线程（TTL机制）"""
        current_time = datetime.now()
        expired_threads = []

        # 检查过期线程
        for thread_id, last_active in self._thread_timestamps.items():
            if current_time - last_active > timedelta(hours=self.TTL_HOURS):
                expired_threads.append(thread_id)

        # 清理过期线程
        if expired_threads:
            for thread_id in expired_threads:
                if thread_id in self._backup_storage:
                    del self._backup_storage[thread_id]
                if thread_id in self._thread_timestamps:
                    del self._thread_timestamps[thread_id]

            self._save_to_file()
            logger.info(f"[Cleanup] {len(expired_threads)} expired threads removed: {expired_threads[:3]}{'...' if len(expired_threads) > 3 else ''}")

    def _cleanup_excess_threads(self):
        """清理超出数量限制的线程（容量限制机制）"""
        current_count = len(self._backup_storage)
        if current_count <= self.MAX_THREADS:
            return

        # 按最后活跃时间排序，清理最旧的线程
        sorted_threads = sorted(
            self._thread_timestamps.items(),
            key=lambda x: x[1]  # 按时间戳排序
        )

        threads_to_remove = current_count - self.MAX_THREADS
        removed_threads = []

        for i in range(threads_to_remove):
            thread_id, _ = sorted_threads[i]
            if thread_id in self._backup_storage:
                del self._backup_storage[thread_id]
            if thread_id in self._thread_timestamps:
                del self._thread_timestamps[thread_id]
            removed_threads.append(thread_id)

        if removed_threads:
            self._save_to_file()
            logger.info(f"[Cleanup] {len(removed_threads)} oldest threads removed due to capacity limit (max: {self.MAX_THREADS})")

    def force_cleanup(self):
        """手动触发清理（用于测试和维护）"""
        logger.info("开始手动清理...")
        initial_count = len(self._backup_storage)

        self._cleanup_expired_threads()
        self._cleanup_excess_threads()

        final_count = len(self._backup_storage)
        logger.info(f"清理完成：{initial_count} -> {final_count} 线程")

    def _save_to_shard(self, thread_id: str, messages: List[BaseMessage]):
        """保存消息到分片文件"""
        try:
            shard_id = self._get_shard_id(thread_id)
            shard_path = self._get_shard_path(shard_id)

            # 读取现有分片数据
            shard_data = {}
            if shard_path.exists():
                with open(shard_path, 'r', encoding='utf-8') as f:
                    shard_data = json.load(f)

            # 初始化分片结构
            if 'threads' not in shard_data:
                shard_data['threads'] = {}
            if 'metadata' not in shard_data:
                shard_data['metadata'] = {
                    'shard_id': shard_id,
                    'last_updated': datetime.now().isoformat(),
                    'thread_count': 0
                }

            # 转换消息为可序列化格式
            serializable_messages = []
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    serializable_messages.append({
                        "type": "HumanMessage",
                        "content": msg.content,
                        "additional_kwargs": msg.additional_kwargs
                    })
                elif isinstance(msg, AIMessage):
                    serializable_messages.append({
                        "type": "AIMessage",
                        "content": msg.content,
                        "additional_kwargs": msg.additional_kwargs
                    })
                elif isinstance(msg, SystemMessage):
                    serializable_messages.append({
                        "type": "SystemMessage",
                        "content": msg.content,
                        "additional_kwargs": msg.additional_kwargs
                    })

            # 更新分片数据
            shard_data['threads'][thread_id] = {
                'messages': serializable_messages,
                'last_updated': datetime.now().isoformat(),
                'message_count': len(messages)
            }
            shard_data['metadata']['last_updated'] = datetime.now().isoformat()
            shard_data['metadata']['thread_count'] = len(shard_data['threads'])

            # 原子写入
            temp_path = shard_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(shard_data, f, ensure_ascii=False, indent=2)
            temp_path.rename(shard_path)

            logger.debug(f"分片存储保存成功 - 分片ID: {shard_id}, 线程ID: {thread_id}")

        except Exception as e:
            logger.error(f"分片存储保存失败 - 线程ID: {thread_id}, 错误: {e}")

    def _load_from_shard(self, thread_id: str) -> List[BaseMessage]:
        """从分片文件加载消息"""
        try:
            shard_id = self._get_shard_id(thread_id)
            shard_path = self._get_shard_path(shard_id)

            if not shard_path.exists():
                return []

            with open(shard_path, 'r', encoding='utf-8') as f:
                shard_data = json.load(f)

            if 'threads' not in shard_data or thread_id not in shard_data['threads']:
                return []

            thread_data = shard_data['threads'][thread_id]
            messages = []

            for msg_data in thread_data['messages']:
                if msg_data["type"] == "HumanMessage":
                    messages.append(HumanMessage(
                        content=msg_data["content"],
                        additional_kwargs=msg_data.get("additional_kwargs", {})
                    ))
                elif msg_data["type"] == "AIMessage":
                    messages.append(AIMessage(
                        content=msg_data["content"],
                        additional_kwargs=msg_data.get("additional_kwargs", {})
                    ))
                elif msg_data["type"] == "SystemMessage":
                    messages.append(SystemMessage(
                        content=msg_data["content"],
                        additional_kwargs=msg_data.get("additional_kwargs", {})
                    ))

            logger.debug(f"分片存储加载成功 - 分片ID: {shard_id}, 线程ID: {thread_id}, 消息数: {len(messages)}")
            return messages

        except Exception as e:
            logger.error(f"分片存储加载失败 - 线程ID: {thread_id}, 错误: {e}")
            return []

    def _load_from_shards(self):
        """从所有分片文件加载数据到内存"""
        try:
            total_threads = 0
            total_messages = 0

            for shard_id in range(self.shard_count):
                shard_path = self._get_shard_path(shard_id)
                if not shard_path.exists():
                    continue

                with open(shard_path, 'r', encoding='utf-8') as f:
                    shard_data = json.load(f)

                if 'threads' not in shard_data:
                    continue

                for thread_id, thread_data in shard_data['threads'].items():
                    messages = []
                    for msg_data in thread_data['messages']:
                        if msg_data["type"] == "HumanMessage":
                            messages.append(HumanMessage(
                                content=msg_data["content"],
                                additional_kwargs=msg_data.get("additional_kwargs", {})
                            ))
                        elif msg_data["type"] == "AIMessage":
                            messages.append(AIMessage(
                                content=msg_data["content"],
                                additional_kwargs=msg_data.get("additional_kwargs", {})
                            ))
                        elif msg_data["type"] == "SystemMessage":
                            messages.append(SystemMessage(
                                content=msg_data["content"],
                                additional_kwargs=msg_data.get("additional_kwargs", {})
                            ))

                    self._backup_storage[thread_id] = messages
                    # 使用文件中的时间戳或当前时间
                    if 'last_updated' in thread_data:
                        self._thread_timestamps[thread_id] = datetime.fromisoformat(thread_data['last_updated'])
                    else:
                        self._thread_timestamps[thread_id] = datetime.now()

                    total_messages += len(messages)

                total_threads += len(shard_data['threads'])

            logger.info(f"分片存储加载完成 - 总线程数: {total_threads}, 总消息数: {total_messages}")

        except Exception as e:
            logger.error(f"分片存储加载失败: {e}")

    def _clear_from_shard(self, thread_id: str):
        """从分片文件中清除指定线程的数据"""
        try:
            shard_id = self._get_shard_id(thread_id)
            shard_path = self._get_shard_path(shard_id)

            if not shard_path.exists():
                return

            with open(shard_path, 'r', encoding='utf-8') as f:
                shard_data = json.load(f)

            if 'threads' not in shard_data or thread_id not in shard_data['threads']:
                return

            # 删除线程数据
            del shard_data['threads'][thread_id]

            # 更新元数据
            if 'metadata' in shard_data:
                shard_data['metadata']['last_updated'] = datetime.now().isoformat()
                shard_data['metadata']['thread_count'] = len(shard_data['threads'])

            # 原子写入
            temp_path = shard_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(shard_data, f, ensure_ascii=False, indent=2)
            temp_path.rename(shard_path)

            logger.debug(f"分片存储清除成功 - 分片ID: {shard_id}, 线程ID: {thread_id}")

        except Exception as e:
            logger.error(f"分片存储清除失败 - 线程ID: {thread_id}, 错误: {e}")


# 创建全局实例
global_storage = GlobalStorage()
