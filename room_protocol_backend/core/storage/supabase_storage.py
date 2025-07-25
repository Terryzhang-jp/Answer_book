"""
Supabase存储实现
提供基于Supabase PostgreSQL的持久化存储
"""

import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from loguru import logger

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from .storage_interface import ConversationStorageInterface
from config.settings import get_settings


class SupabaseStorage(ConversationStorageInterface):
    """Supabase存储实现"""
    
    def __init__(self):
        """初始化Supabase存储"""
        self.settings = get_settings()
        self._connection = None
        self._ensure_connection()
        self._ensure_tables()
        logger.info("Supabase存储初始化完成")
    
    def _ensure_connection(self) -> None:
        """确保数据库连接"""
        try:
            if self._connection is None or self._connection.closed:
                self._connection = psycopg2.connect(
                    host=self.settings.SUPABASE_DB_HOST,
                    port=self.settings.SUPABASE_DB_PORT,
                    database=self.settings.SUPABASE_DB_NAME,
                    user=self.settings.SUPABASE_DB_USER,
                    password=self.settings.SUPABASE_DB_PASSWORD,
                    gssencmode='disable',
                    sslmode='require'
                )
                logger.debug("Supabase数据库连接建立成功")
        except Exception as e:
            logger.error(f"Supabase数据库连接失败: {e}")
            raise
    
    def _ensure_tables(self) -> None:
        """确保数据库表存在"""
        try:
            with self._connection.cursor() as cursor:
                # 创建conversations表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        thread_id VARCHAR(255) UNIQUE NOT NULL,
                        user_id VARCHAR(255),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        metadata JSONB DEFAULT '{}'::jsonb
                    );
                """)
                
                # 创建messages表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
                        thread_id VARCHAR(255) NOT NULL,
                        message_type VARCHAR(50) NOT NULL,
                        content TEXT NOT NULL,
                        additional_kwargs JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        message_order INTEGER NOT NULL
                    );
                """)
                
                # 创建索引
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_conversations_thread_id 
                    ON conversations(thread_id);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_messages_thread_id 
                    ON messages(thread_id);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
                    ON messages(conversation_id);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_messages_created_at 
                    ON messages(created_at);
                """)
                
                self._connection.commit()
                logger.debug("Supabase数据库表结构确认完成")
                
        except Exception as e:
            logger.error(f"创建Supabase数据库表失败: {e}")
            self._connection.rollback()
            raise
    
    def _message_to_dict(self, message: BaseMessage) -> Dict[str, Any]:
        """将消息对象转换为字典"""
        return {
            "type": message.__class__.__name__,
            "content": message.content,
            "additional_kwargs": getattr(message, 'additional_kwargs', {})
        }
    
    def _dict_to_message(self, msg_dict: Dict[str, Any]) -> BaseMessage:
        """将字典转换为消息对象"""
        msg_type = msg_dict.get("type", "")
        content = msg_dict.get("content", "")
        additional_kwargs = msg_dict.get("additional_kwargs", {})
        
        if msg_type == "HumanMessage":
            return HumanMessage(content=content, additional_kwargs=additional_kwargs)
        elif msg_type == "AIMessage":
            return AIMessage(content=content, additional_kwargs=additional_kwargs)
        else:
            # 默认返回AIMessage
            return AIMessage(content=content, additional_kwargs=additional_kwargs)
    
    async def save_messages(self, thread_id: str, messages: List[BaseMessage]) -> bool:
        """保存消息到Supabase"""
        try:
            self._ensure_connection()
            
            with self._connection.cursor() as cursor:
                # 确保conversation记录存在
                cursor.execute("""
                    INSERT INTO conversations (thread_id, created_at, updated_at)
                    VALUES (%s, NOW(), NOW())
                    ON CONFLICT (thread_id) 
                    DO UPDATE SET updated_at = NOW()
                    RETURNING id;
                """, (thread_id,))
                
                conversation_id = cursor.fetchone()[0]
                
                # 删除现有消息（重新保存所有消息）
                cursor.execute("""
                    DELETE FROM messages WHERE thread_id = %s;
                """, (thread_id,))
                
                # 保存所有消息
                for order, message in enumerate(messages):
                    msg_dict = self._message_to_dict(message)
                    cursor.execute("""
                        INSERT INTO messages (
                            conversation_id, thread_id, message_type, 
                            content, additional_kwargs, message_order
                        ) VALUES (%s, %s, %s, %s, %s, %s);
                    """, (
                        conversation_id,
                        thread_id,
                        msg_dict["type"],
                        msg_dict["content"],
                        json.dumps(msg_dict["additional_kwargs"]),
                        order
                    ))
                
                self._connection.commit()
                logger.debug(f"Supabase保存消息成功 - thread_id: {thread_id}, 消息数: {len(messages)}")
                return True
                
        except Exception as e:
            logger.error(f"Supabase保存消息失败 - thread_id: {thread_id}, 错误: {e}")
            if self._connection:
                self._connection.rollback()
            return False
    
    async def get_messages(self, thread_id: str) -> List[BaseMessage]:
        """从Supabase获取消息"""
        try:
            self._ensure_connection()
            
            with self._connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT message_type, content, additional_kwargs
                    FROM messages 
                    WHERE thread_id = %s 
                    ORDER BY message_order ASC;
                """, (thread_id,))
                
                rows = cursor.fetchall()
                messages = []
                
                for row in rows:
                    msg_dict = {
                        "type": row["message_type"],
                        "content": row["content"],
                        "additional_kwargs": row["additional_kwargs"] or {}
                    }
                    messages.append(self._dict_to_message(msg_dict))
                
                logger.debug(f"Supabase获取消息成功 - thread_id: {thread_id}, 消息数: {len(messages)}")
                return messages
                
        except Exception as e:
            logger.error(f"Supabase获取消息失败 - thread_id: {thread_id}, 错误: {e}")
            return []
    
    async def get_recent_messages(self, thread_id: str, count: int = 5) -> List[BaseMessage]:
        """获取最近的N条消息"""
        try:
            self._ensure_connection()

            with self._connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT message_type, content, additional_kwargs
                    FROM messages
                    WHERE thread_id = %s
                    ORDER BY message_order DESC
                    LIMIT %s;
                """, (thread_id, count))

                rows = cursor.fetchall()
                messages = []

                for row in reversed(rows):  # 反转以保持正确顺序
                    msg_dict = {
                        "type": row["message_type"],
                        "content": row["content"],
                        "additional_kwargs": row["additional_kwargs"] or {}
                    }
                    messages.append(self._dict_to_message(msg_dict))

                logger.debug(f"Supabase获取最近消息成功 - thread_id: {thread_id}, 消息数: {len(messages)}")
                return messages

        except Exception as e:
            logger.error(f"Supabase获取最近消息失败 - thread_id: {thread_id}, 错误: {e}")
            return []

    async def delete_conversation(self, thread_id: str) -> bool:
        """从Supabase删除整个对话"""
        try:
            self._ensure_connection()
            
            with self._connection.cursor() as cursor:
                # 删除消息
                cursor.execute("""
                    DELETE FROM messages WHERE thread_id = %s;
                """, (thread_id,))
                
                # 删除conversation记录
                cursor.execute("""
                    DELETE FROM conversations WHERE thread_id = %s;
                """, (thread_id,))
                
                self._connection.commit()
                logger.debug(f"Supabase删除消息成功 - thread_id: {thread_id}")
                return True
                
        except Exception as e:
            logger.error(f"Supabase删除消息失败 - thread_id: {thread_id}, 错误: {e}")
            if self._connection:
                self._connection.rollback()
            return False
    
    async def list_conversations(self, user_id: Optional[str] = None) -> List[str]:
        """列出对话ID"""
        try:
            self._ensure_connection()

            with self._connection.cursor() as cursor:
                if user_id:
                    cursor.execute("""
                        SELECT thread_id FROM conversations
                        WHERE user_id = %s
                        ORDER BY updated_at DESC;
                    """, (user_id,))
                else:
                    cursor.execute("""
                        SELECT thread_id FROM conversations
                        ORDER BY updated_at DESC;
                    """)

                rows = cursor.fetchall()
                thread_ids = [row[0] for row in rows]

                logger.debug(f"Supabase列出对话成功 - 对话数: {len(thread_ids)}")
                return thread_ids

        except Exception as e:
            logger.error(f"Supabase列出对话失败: {e}")
            return []

    async def get_conversation_info(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """获取对话基本信息"""
        try:
            self._ensure_connection()

            with self._connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT c.*, COUNT(m.id) as message_count
                    FROM conversations c
                    LEFT JOIN messages m ON c.id = m.conversation_id
                    WHERE c.thread_id = %s
                    GROUP BY c.id;
                """, (thread_id,))

                row = cursor.fetchone()
                if row:
                    info = {
                        "thread_id": row["thread_id"],
                        "user_id": row["user_id"],
                        "created_at": str(row["created_at"]),
                        "updated_at": str(row["updated_at"]),
                        "message_count": row["message_count"],
                        "metadata": row["metadata"] or {}
                    }
                    logger.debug(f"Supabase获取对话信息成功 - thread_id: {thread_id}")
                    return info
                else:
                    logger.debug(f"Supabase对话不存在 - thread_id: {thread_id}")
                    return None

        except Exception as e:
            logger.error(f"Supabase获取对话信息失败 - thread_id: {thread_id}, 错误: {e}")
            return None

    async def list_threads(self) -> List[str]:
        """列出所有线程ID"""
        try:
            self._ensure_connection()
            
            with self._connection.cursor() as cursor:
                cursor.execute("""
                    SELECT thread_id FROM conversations 
                    ORDER BY updated_at DESC;
                """)
                
                rows = cursor.fetchall()
                thread_ids = [row[0] for row in rows]
                
                logger.debug(f"Supabase列出线程成功 - 线程数: {len(thread_ids)}")
                return thread_ids
                
        except Exception as e:
            logger.error(f"Supabase列出线程失败: {e}")
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        try:
            self._ensure_connection()
            
            with self._connection.cursor() as cursor:
                # 获取conversation统计
                cursor.execute("SELECT COUNT(*) FROM conversations;")
                conversation_count = cursor.fetchone()[0]
                
                # 获取message统计
                cursor.execute("SELECT COUNT(*) FROM messages;")
                message_count = cursor.fetchone()[0]
                
                # 获取最近活动
                cursor.execute("""
                    SELECT MAX(updated_at) FROM conversations;
                """)
                last_activity = cursor.fetchone()[0]
                
                stats = {
                    "storage_type": "supabase",
                    "conversation_count": conversation_count,
                    "message_count": message_count,
                    "last_activity": str(last_activity) if last_activity else None,
                    "status": "healthy"
                }
                
                logger.debug(f"Supabase统计信息: {stats}")
                return stats
                
        except Exception as e:
            logger.error(f"获取Supabase统计信息失败: {e}")
            return {
                "storage_type": "supabase",
                "status": "error",
                "error": str(e)
            }
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            logger.debug("Supabase数据库连接已关闭")
