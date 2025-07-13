"""
场景会话存储服务
"""

import json
import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger

from core.models.scenario import ScenarioSession


class ScenarioStorageInterface(ABC):
    """场景存储接口"""
    
    @abstractmethod
    async def save_session(self, session: ScenarioSession) -> bool:
        """保存会话"""
        pass
    
    @abstractmethod
    async def load_session(self, session_id: str) -> Optional[ScenarioSession]:
        """加载会话"""
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        pass
    
    @abstractmethod
    async def list_sessions(self, thread_id: Optional[str] = None, user_id: Optional[str] = None) -> List[ScenarioSession]:
        """列出会话"""
        pass
    
    @abstractmethod
    async def clear_all(self) -> bool:
        """清除所有会话"""
        pass


class FileScenarioStorage(ScenarioStorageInterface):
    """基于文件的场景存储实现"""
    
    def __init__(self, storage_dir: str = "data/scenario_sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"场景存储初始化完成，存储目录: {self.storage_dir}")
    
    def _get_session_file_path(self, session_id: str) -> Path:
        """获取会话文件路径"""
        return self.storage_dir / f"{session_id}.json"
    
    def _serialize_session(self, session: ScenarioSession) -> dict:
        """序列化会话对象"""
        data = session.model_dump()
        # 确保datetime对象被正确序列化
        if isinstance(data.get('created_at'), datetime):
            data['created_at'] = data['created_at'].isoformat()
        if isinstance(data.get('completed_at'), datetime):
            data['completed_at'] = data['completed_at'].isoformat()
        return data
    
    def _deserialize_session(self, data: dict) -> ScenarioSession:
        """反序列化会话对象"""
        # 转换datetime字段
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'completed_at' in data and isinstance(data['completed_at'], str):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        
        return ScenarioSession(**data)
    
    async def save_session(self, session: ScenarioSession) -> bool:
        """保存会话到文件"""
        try:
            file_path = self._get_session_file_path(session.id)
            data = self._serialize_session(session)
            
            # 原子写入（先写临时文件，再重命名）
            temp_path = file_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            temp_path.rename(file_path)
            logger.info(f"场景会话保存成功: {session.id}")
            return True
            
        except Exception as e:
            logger.error(f"保存场景会话失败 {session.id}: {e}")
            return False
    
    async def load_session(self, session_id: str) -> Optional[ScenarioSession]:
        """从文件加载会话"""
        try:
            file_path = self._get_session_file_path(session_id)
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            session = self._deserialize_session(data)
            logger.debug(f"场景会话加载成功: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"加载场景会话失败 {session_id}: {e}")
            return None
    
    async def delete_session(self, session_id: str) -> bool:
        """删除会话文件"""
        try:
            file_path = self._get_session_file_path(session_id)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"场景会话删除成功: {session_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"删除场景会话失败 {session_id}: {e}")
            return False
    
    async def list_sessions(self, thread_id: Optional[str] = None, user_id: Optional[str] = None) -> List[ScenarioSession]:
        """列出会话"""
        sessions = []
        try:
            for file_path in self.storage_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    session = self._deserialize_session(data)
                    
                    # 应用过滤条件
                    if thread_id and session.thread_id != thread_id:
                        continue
                    if user_id and session.user_id != user_id:
                        continue
                    
                    sessions.append(session)
                    
                except Exception as e:
                    logger.warning(f"跳过损坏的会话文件 {file_path}: {e}")
                    continue
            
            # 按创建时间排序
            sessions.sort(key=lambda x: x.created_at, reverse=True)
            logger.debug(f"列出场景会话成功，数量: {len(sessions)}")
            return sessions
            
        except Exception as e:
            logger.error(f"列出场景会话失败: {e}")
            return []
    
    async def clear_all(self) -> bool:
        """清除所有会话文件"""
        try:
            count = 0
            for file_path in self.storage_dir.glob("*.json"):
                file_path.unlink()
                count += 1
            
            logger.info(f"清除所有场景会话成功，数量: {count}")
            return True
            
        except Exception as e:
            logger.error(f"清除所有场景会话失败: {e}")
            return False
    
    async def migrate_from_memory(self, memory_sessions: Dict[str, ScenarioSession]) -> int:
        """从内存数据迁移到文件存储"""
        migrated_count = 0
        try:
            for session_id, session in memory_sessions.items():
                if await self.save_session(session):
                    migrated_count += 1
                else:
                    logger.warning(f"迁移会话失败: {session_id}")
            
            logger.info(f"场景会话迁移完成，成功迁移: {migrated_count}/{len(memory_sessions)}")
            return migrated_count
            
        except Exception as e:
            logger.error(f"场景会话迁移失败: {e}")
            return migrated_count


class MemoryScenarioStorage(ScenarioStorageInterface):
    """内存场景存储实现（向后兼容）"""
    
    def __init__(self):
        self.sessions: Dict[str, ScenarioSession] = {}
        logger.info("内存场景存储初始化完成")
    
    async def save_session(self, session: ScenarioSession) -> bool:
        """保存会话到内存"""
        self.sessions[session.id] = session
        return True
    
    async def load_session(self, session_id: str) -> Optional[ScenarioSession]:
        """从内存加载会话"""
        return self.sessions.get(session_id)
    
    async def delete_session(self, session_id: str) -> bool:
        """从内存删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    async def list_sessions(self, thread_id: Optional[str] = None, user_id: Optional[str] = None) -> List[ScenarioSession]:
        """列出内存中的会话"""
        sessions = list(self.sessions.values())
        
        # 应用过滤条件
        if thread_id:
            sessions = [s for s in sessions if s.thread_id == thread_id]
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        
        # 按创建时间排序
        sessions.sort(key=lambda x: x.created_at, reverse=True)
        return sessions
    
    async def clear_all(self) -> bool:
        """清除所有内存会话"""
        self.sessions.clear()
        return True


# 存储工厂
class ScenarioStorageFactory:
    """场景存储工厂"""
    
    @staticmethod
    def create_storage(storage_type: str = "file", **kwargs) -> ScenarioStorageInterface:
        """创建存储实例"""
        if storage_type == "file":
            return FileScenarioStorage(**kwargs)
        elif storage_type == "memory":
            return MemoryScenarioStorage()
        else:
            raise ValueError(f"不支持的存储类型: {storage_type}")


# 全局存储实例
_storage_instance: Optional[ScenarioStorageInterface] = None

def get_scenario_storage() -> ScenarioStorageInterface:
    """获取场景存储实例（单例模式）"""
    global _storage_instance
    if _storage_instance is None:
        # 从环境变量读取存储类型
        storage_type = os.getenv("SCENARIO_STORAGE_TYPE", "file")
        storage_dir = os.getenv("SCENARIO_STORAGE_DIR", "data/scenario_sessions")
        
        _storage_instance = ScenarioStorageFactory.create_storage(
            storage_type=storage_type,
            storage_dir=storage_dir
        )
        logger.info(f"场景存储实例创建完成，类型: {storage_type}")
    
    return _storage_instance
