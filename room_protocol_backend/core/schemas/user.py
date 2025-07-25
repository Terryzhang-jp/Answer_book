"""
用户管理相关的数据模型
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"          # 管理员
    USER = "user"            # 普通用户
    VIEWER = "viewer"        # 只读用户
    OWNER = "owner"          # 组织所有者


class SubscriptionTier(str, Enum):
    """订阅等级枚举"""
    FREE = "free"            # 免费版
    PRO = "pro"              # 专业版
    ENTERPRISE = "enterprise" # 企业版


class User(BaseModel):
    """用户模型"""
    id: str = Field(..., description="用户唯一ID")
    email: EmailStr = Field(..., description="用户邮箱")
    name: str = Field(..., description="用户姓名")
    role: UserRole = Field(default=UserRole.USER, description="用户角色")
    organization_id: Optional[str] = Field(None, description="所属组织ID")
    subscription_tier: SubscriptionTier = Field(default=SubscriptionTier.FREE, description="订阅等级")
    
    # 配额管理
    api_quota_monthly: int = Field(default=1000, description="月度API调用配额")
    api_quota_used: int = Field(default=0, description="已使用的API配额")
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    
    # 用户设置
    settings: Dict[str, Any] = Field(default_factory=dict, description="用户个人设置")
    is_active: bool = Field(default=True, description="用户是否激活")


class Organization(BaseModel):
    """组织模型"""
    id: str = Field(..., description="组织唯一ID")
    name: str = Field(..., description="组织名称")
    subscription_plan: SubscriptionTier = Field(..., description="订阅计划")
    
    # 配额管理
    max_users: int = Field(default=10, description="最大用户数")
    api_quota_total: int = Field(default=10000, description="组织总API配额")
    api_quota_used: int = Field(default=0, description="已使用的API配额")
    
    # 组织设置
    settings: Dict[str, Any] = Field(default_factory=dict, description="组织设置")
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    is_active: bool = Field(default=True, description="组织是否激活")


class UserCreateRequest(BaseModel):
    """创建用户请求"""
    email: EmailStr = Field(..., description="用户邮箱")
    name: str = Field(..., description="用户姓名", min_length=1, max_length=100)
    password: str = Field(..., description="用户密码", min_length=6)
    organization_id: Optional[str] = Field(None, description="所属组织ID")


class UserUpdateRequest(BaseModel):
    """更新用户请求"""
    name: Optional[str] = Field(None, description="用户姓名", min_length=1, max_length=100)
    role: Optional[UserRole] = Field(None, description="用户角色")
    subscription_tier: Optional[SubscriptionTier] = Field(None, description="订阅等级")
    api_quota_monthly: Optional[int] = Field(None, description="月度API配额")
    settings: Optional[Dict[str, Any]] = Field(None, description="用户设置")
    is_active: Optional[bool] = Field(None, description="用户是否激活")


class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., description="用户密码")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="令牌过期时间（秒）")
    user: User = Field(..., description="用户信息")


class UserQuotaInfo(BaseModel):
    """用户配额信息"""
    user_id: str = Field(..., description="用户ID")
    monthly_quota: int = Field(..., description="月度配额")
    used_quota: int = Field(..., description="已使用配额")
    remaining_quota: int = Field(..., description="剩余配额")
    reset_date: datetime = Field(..., description="配额重置日期")


class UserListResponse(BaseModel):
    """用户列表响应"""
    users: List[User] = Field(..., description="用户列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="每页大小")