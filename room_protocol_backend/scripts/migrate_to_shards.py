#!/usr/bin/env python3
"""
数据迁移脚本：从单文件存储迁移到分片存储
"""

import json
import os
import sys
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import get_settings
from loguru import logger

class StorageMigrator:
    """存储迁移器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.shard_count = self.settings.STORAGE_SHARD_COUNT
        self.base_path = Path(self.settings.STORAGE_BASE_PATH)
        self.old_storage_file = "memory/global_backup_storage.json"
        
        # 确保目标目录存在
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"迁移器初始化完成 - 分片数量: {self.shard_count}, 目标路径: {self.base_path}")
    
    def _get_shard_id(self, thread_id: str) -> int:
        """根据thread_id计算分片ID"""
        hash_value = hashlib.md5(thread_id.encode()).hexdigest()
        return int(hash_value, 16) % self.shard_count
    
    def _get_shard_path(self, shard_id: int) -> Path:
        """获取分片文件路径"""
        return self.base_path / f"shard_{shard_id:03d}.json"
    
    def backup_old_data(self) -> bool:
        """备份原始数据"""
        try:
            if not os.path.exists(self.old_storage_file):
                logger.warning(f"原始存储文件不存在: {self.old_storage_file}")
                return True
            
            backup_file = f"{self.old_storage_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 复制文件
            import shutil
            shutil.copy2(self.old_storage_file, backup_file)
            
            logger.info(f"数据备份完成: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"数据备份失败: {e}")
            return False
    
    def load_old_data(self) -> Dict[str, Any]:
        """加载原始数据"""
        try:
            if not os.path.exists(self.old_storage_file):
                logger.warning(f"原始存储文件不存在: {self.old_storage_file}")
                return {}
            
            with open(self.old_storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"原始数据加载完成 - 线程数: {len(data.get('threads', {}))}")
            return data
            
        except Exception as e:
            logger.error(f"原始数据加载失败: {e}")
            return {}
    
    def migrate_to_shards(self, old_data: Dict[str, Any]) -> bool:
        """迁移数据到分片存储"""
        try:
            if not old_data or 'threads' not in old_data:
                logger.info("没有需要迁移的数据")
                return True
            
            threads = old_data['threads']
            timestamps = old_data.get('timestamps', {})
            
            # 按分片组织数据
            shard_data = {}
            for shard_id in range(self.shard_count):
                shard_data[shard_id] = {
                    'threads': {},
                    'metadata': {
                        'shard_id': shard_id,
                        'last_updated': datetime.now().isoformat(),
                        'thread_count': 0
                    }
                }
            
            # 分配线程到分片
            migrated_count = 0
            for thread_id, messages in threads.items():
                shard_id = self._get_shard_id(thread_id)
                
                # 获取时间戳
                last_updated = timestamps.get(thread_id, datetime.now().isoformat())
                if isinstance(last_updated, str):
                    # 已经是ISO格式
                    pass
                else:
                    # 转换为ISO格式
                    last_updated = datetime.now().isoformat()
                
                shard_data[shard_id]['threads'][thread_id] = {
                    'messages': messages,
                    'last_updated': last_updated,
                    'message_count': len(messages)
                }
                migrated_count += 1
            
            # 写入分片文件
            for shard_id, data in shard_data.items():
                if not data['threads']:
                    continue  # 跳过空分片
                
                data['metadata']['thread_count'] = len(data['threads'])
                shard_path = self._get_shard_path(shard_id)
                
                # 原子写入
                temp_path = shard_path.with_suffix('.tmp')
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                temp_path.rename(shard_path)
                
                logger.info(f"分片 {shard_id} 迁移完成 - 线程数: {len(data['threads'])}")
            
            logger.info(f"数据迁移完成 - 总线程数: {migrated_count}")
            return True
            
        except Exception as e:
            logger.error(f"数据迁移失败: {e}")
            return False
    
    def verify_migration(self, old_data: Dict[str, Any]) -> bool:
        """验证迁移结果"""
        try:
            if not old_data or 'threads' not in old_data:
                logger.info("没有数据需要验证")
                return True
            
            old_threads = old_data['threads']
            migrated_threads = {}
            
            # 从分片文件读取数据
            for shard_id in range(self.shard_count):
                shard_path = self._get_shard_path(shard_id)
                if not shard_path.exists():
                    continue
                
                with open(shard_path, 'r', encoding='utf-8') as f:
                    shard_data = json.load(f)
                
                if 'threads' in shard_data:
                    migrated_threads.update(shard_data['threads'])
            
            # 验证数据完整性
            old_count = len(old_threads)
            migrated_count = len(migrated_threads)
            
            if old_count != migrated_count:
                logger.error(f"数据数量不匹配 - 原始: {old_count}, 迁移后: {migrated_count}")
                return False
            
            # 验证每个线程的数据
            for thread_id, old_messages in old_threads.items():
                if thread_id not in migrated_threads:
                    logger.error(f"线程数据丢失: {thread_id}")
                    return False
                
                migrated_messages = migrated_threads[thread_id]['messages']
                if len(old_messages) != len(migrated_messages):
                    logger.error(f"线程 {thread_id} 消息数量不匹配 - 原始: {len(old_messages)}, 迁移后: {len(migrated_messages)}")
                    return False
            
            logger.info(f"数据验证通过 - 线程数: {migrated_count}")
            return True
            
        except Exception as e:
            logger.error(f"数据验证失败: {e}")
            return False
    
    def run_migration(self) -> bool:
        """执行完整的迁移流程"""
        logger.info("开始数据迁移...")
        
        # 1. 备份原始数据
        if not self.backup_old_data():
            return False
        
        # 2. 加载原始数据
        old_data = self.load_old_data()
        
        # 3. 迁移到分片存储
        if not self.migrate_to_shards(old_data):
            return False
        
        # 4. 验证迁移结果
        if not self.verify_migration(old_data):
            return False
        
        logger.info("数据迁移完成！")
        return True

def main():
    """主函数"""
    logger.info("存储迁移脚本启动")
    
    migrator = StorageMigrator()
    
    if migrator.run_migration():
        logger.info("迁移成功完成")
        return 0
    else:
        logger.error("迁移失败")
        return 1

if __name__ == "__main__":
    exit(main())
