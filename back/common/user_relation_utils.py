"""
用户关系操作工具函数
提供关注、取消关注、喜欢文章、取消喜欢等操作的封装
"""
from django.db import transaction
from django.db.models import F
from common.models import Users, UserFollow, UserLikedArticle, BlogArticle


def follow_user(follower_id, following_id):
    """
    关注用户
    
    Args:
        follower_id: 关注者ID
        following_id: 被关注者ID
    
    Returns:
        tuple: (success: bool, message: str)
    
    Raises:
        ValueError: 如果尝试关注自己
    """
    if follower_id == following_id:
        raise ValueError("不能关注自己")
    
    # 检查是否已经关注
    if UserFollow.objects.filter(
        follower_id=follower_id,
        following_id=following_id
    ).exists():
        return False, "已经关注过该用户"
    
    try:
        with transaction.atomic():
            # 创建关注关系（触发器会自动更新统计字段）
            UserFollow.objects.create(
                follower_id=follower_id,
                following_id=following_id
            )
        
        return True, "关注成功"
    except Exception as e:
        return False, f"关注失败: {str(e)}"


def unfollow_user(follower_id, following_id):
    """
    取消关注用户
    
    Args:
        follower_id: 关注者ID
        following_id: 被关注者ID
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # 检查是否已经关注
    if not UserFollow.objects.filter(
        follower_id=follower_id,
        following_id=following_id
    ).exists():
        return False, "未关注该用户"
    
    try:
        with transaction.atomic():
            # 删除关注关系（触发器会自动更新统计字段）
            UserFollow.objects.filter(
                follower_id=follower_id,
                following_id=following_id
            ).delete()
        
        return True, "取消关注成功"
    except Exception as e:
        return False, f"取消关注失败: {str(e)}"


def like_article(user_id, article_id):
    """
    喜欢文章
    
    Args:
        user_id: 用户ID
        article_id: 文章ID
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # 检查文章是否存在
    if not BlogArticle.objects.filter(id=article_id).exists():
        return False, "文章不存在"
    
    # 检查是否已经喜欢
    if UserLikedArticle.objects.filter(
        user_id=user_id,
        article_id=article_id
    ).exists():
        return False, "已经喜欢过该文章"
    
    try:
        with transaction.atomic():
            # 创建喜欢关系（触发器会自动更新统计字段）
            UserLikedArticle.objects.create(
                user_id=user_id,
                article_id=article_id
            )
        
        return True, "喜欢成功"
    except Exception as e:
        return False, f"喜欢失败: {str(e)}"


def unlike_article(user_id, article_id):
    """
    取消喜欢文章
    
    Args:
        user_id: 用户ID
        article_id: 文章ID
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # 检查是否已经喜欢
    if not UserLikedArticle.objects.filter(
        user_id=user_id,
        article_id=article_id
    ).exists():
        return False, "未喜欢该文章"
    
    try:
        with transaction.atomic():
            # 删除喜欢关系（触发器会自动更新统计字段）
            UserLikedArticle.objects.filter(
                user_id=user_id,
                article_id=article_id
            ).delete()
        
        return True, "取消喜欢成功"
    except Exception as e:
        return False, f"取消喜欢失败: {str(e)}"


def get_user_following(user_id):
    """
    获取用户关注的人列表
    
    Args:
        user_id: 用户ID
    
    Returns:
        QuerySet: 关注的用户列表
    """
    following_ids = UserFollow.objects.filter(
        follower_id=user_id
    ).values_list('following_id', flat=True)
    
    return Users.objects.filter(id__in=following_ids)


def get_user_followers(user_id):
    """
    获取关注该用户的用户列表
    
    Args:
        user_id: 用户ID
    
    Returns:
        QuerySet: 粉丝列表
    """
    follower_ids = UserFollow.objects.filter(
        following_id=user_id
    ).values_list('follower_id', flat=True)
    
    return Users.objects.filter(id__in=follower_ids)


def get_user_liked_articles(user_id):
    """
    获取用户喜欢的文章列表
    
    Args:
        user_id: 用户ID
    
    Returns:
        QuerySet: 喜欢的文章列表
    """
    article_ids = UserLikedArticle.objects.filter(
        user_id=user_id
    ).values_list('article_id', flat=True)
    
    return BlogArticle.objects.filter(id__in=article_ids)


def get_user_articles(user_id):
    """
    获取用户发布的文章列表
    
    Args:
        user_id: 用户ID
    
    Returns:
        QuerySet: 发布的文章列表
    """
    return BlogArticle.objects.filter(author_id=user_id)


def is_following(follower_id, following_id):
    """
    检查用户A是否关注了用户B
    
    Args:
        follower_id: 关注者ID
        following_id: 被关注者ID
    
    Returns:
        bool: 是否关注
    """
    return UserFollow.objects.filter(
        follower_id=follower_id,
        following_id=following_id
    ).exists()


def is_liked_article(user_id, article_id):
    """
    检查用户是否喜欢了某篇文章
    
    Args:
        user_id: 用户ID
        article_id: 文章ID
    
    Returns:
        bool: 是否喜欢
    """
    return UserLikedArticle.objects.filter(
        user_id=user_id,
        article_id=article_id
    ).exists()



