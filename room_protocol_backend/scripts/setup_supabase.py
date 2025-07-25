#!/usr/bin/env python3
"""
Supabase数据库初始化脚本
创建必要的表结构和索引
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from dotenv import load_dotenv
from loguru import logger
from config.settings import get_settings

# 加载环境变量
load_dotenv()

def create_database_schema():
    """创建数据库表结构"""
    settings = get_settings()
    
    try:
        # 连接数据库
        connection = psycopg2.connect(
            host=settings.SUPABASE_DB_HOST,
            port=settings.SUPABASE_DB_PORT,
            database=settings.SUPABASE_DB_NAME,
            user=settings.SUPABASE_DB_USER,
            password=settings.SUPABASE_DB_PASSWORD,
            gssencmode='disable',
            sslmode='require'
        )
        
        logger.info("✅ 连接Supabase数据库成功")
        
        with connection.cursor() as cursor:
            # 创建conversations表
            logger.info("📋 创建conversations表...")
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
            logger.info("📋 创建messages表...")
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
            logger.info("🔍 创建索引...")
            
            # conversations表索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_thread_id 
                ON conversations(thread_id);
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_user_id 
                ON conversations(user_id);
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_created_at 
                ON conversations(created_at);
            """)
            
            # messages表索引
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
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_message_order 
                ON messages(thread_id, message_order);
            """)
            
            # 创建触发器更新updated_at
            logger.info("⚡ 创建触发器...")
            cursor.execute("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = NOW();
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
            """)
            
            cursor.execute("""
                DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
                CREATE TRIGGER update_conversations_updated_at
                    BEFORE UPDATE ON conversations
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();
            """)
            
            # 提交事务
            connection.commit()
            logger.info("✅ 数据库表结构创建完成")
            
            # 验证表结构
            logger.info("🔍 验证表结构...")
            cursor.execute("""
                SELECT table_name, column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name IN ('conversations', 'messages')
                ORDER BY table_name, ordinal_position;
            """)
            
            columns = cursor.fetchall()
            logger.info("📊 表结构验证:")
            current_table = None
            for table_name, column_name, data_type in columns:
                if table_name != current_table:
                    logger.info(f"  📋 {table_name}:")
                    current_table = table_name
                logger.info(f"    - {column_name}: {data_type}")
            
            # 检查索引
            cursor.execute("""
                SELECT indexname, tablename 
                FROM pg_indexes 
                WHERE tablename IN ('conversations', 'messages')
                AND schemaname = 'public'
                ORDER BY tablename, indexname;
            """)
            
            indexes = cursor.fetchall()
            logger.info("🔍 索引验证:")
            current_table = None
            for index_name, table_name in indexes:
                if table_name != current_table:
                    logger.info(f"  📋 {table_name}:")
                    current_table = table_name
                logger.info(f"    - {index_name}")
        
        connection.close()
        logger.info("🎉 Supabase数据库初始化完成!")
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        return False

def test_connection():
    """测试数据库连接"""
    settings = get_settings()
    
    try:
        connection = psycopg2.connect(
            host=settings.SUPABASE_DB_HOST,
            port=settings.SUPABASE_DB_PORT,
            database=settings.SUPABASE_DB_NAME,
            user=settings.SUPABASE_DB_USER,
            password=settings.SUPABASE_DB_PASSWORD,
            gssencmode='disable',
            sslmode='require'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            logger.info(f"✅ 数据库连接成功")
            logger.info(f"📊 PostgreSQL版本: {version}")
            
            cursor.execute("SELECT NOW();")
            current_time = cursor.fetchone()[0]
            logger.info(f"⏰ 服务器时间: {current_time}")
        
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("🚀 开始Supabase数据库初始化")
    
    # 检查配置
    settings = get_settings()
    if not all([
        settings.SUPABASE_DB_HOST,
        settings.SUPABASE_DB_USER,
        settings.SUPABASE_DB_PASSWORD
    ]):
        logger.error("❌ Supabase配置不完整，请检查环境变量")
        return False
    
    logger.info(f"🔗 连接信息:")
    logger.info(f"  主机: {settings.SUPABASE_DB_HOST}:{settings.SUPABASE_DB_PORT}")
    logger.info(f"  数据库: {settings.SUPABASE_DB_NAME}")
    logger.info(f"  用户: {settings.SUPABASE_DB_USER}")
    
    # 测试连接
    if not test_connection():
        return False
    
    # 创建表结构
    if not create_database_schema():
        return False
    
    logger.info("🎉 Supabase初始化完成!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
