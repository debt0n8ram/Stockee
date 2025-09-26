from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.enhanced_social_service import EnhancedSocialService
from pydantic import BaseModel
from typing import List, Optional
import json

router = APIRouter(prefix="/api/enhanced-social", tags=["enhanced-social"])

class CreatePostRequest(BaseModel):
    content: str
    post_type: str = "general"
    symbol: Optional[str] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    mentions: Optional[List[str]] = None

class CreateChatRoomRequest(BaseModel):
    name: str
    description: str = ""
    is_public: bool = True
    max_members: int = 100

class SendMessageRequest(BaseModel):
    content: str
    message_type: str = "text"

class FollowUserRequest(BaseModel):
    following_id: str

class ReportContentRequest(BaseModel):
    content_type: str
    content_id: int
    reason: str
    description: str = ""

# Enhanced Post Management
@router.post("/posts")
async def create_enhanced_post(
    request: CreatePostRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new social post with enhanced features"""
    try:
        social_service = EnhancedSocialService(db)
        result = social_service.create_enhanced_post(
            user_id=current_user,
            content=request.content,
            post_type=request.post_type,
            symbol=request.symbol,
            tags=request.tags,
            images=request.images,
            mentions=request.mentions
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feed")
async def get_enhanced_feed(
    algorithm: str = Query("chronological", description="Feed algorithm: chronological, popular, personalized"),
    limit: int = Query(50, description="Number of posts to return"),
    offset: int = Query(0, description="Number of posts to skip"),
    post_type: Optional[str] = Query(None, description="Filter by post type"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get enhanced social feed with different algorithms"""
    try:
        social_service = EnhancedSocialService(db)
        result = social_service.get_enhanced_feed(
            user_id=current_user,
            limit=limit,
            offset=offset,
            post_type=post_type,
            symbol=symbol,
            algorithm=algorithm
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Real-time Chat Features
@router.post("/chat/rooms")
async def create_chat_room(
    request: CreateChatRoomRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat room"""
    try:
        social_service = EnhancedSocialService(db)
        result = social_service.create_chat_room(
            user_id=current_user,
            name=request.name,
            description=request.description,
            is_public=request.is_public,
            max_members=request.max_members
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/rooms")
async def get_user_chat_rooms(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat rooms for the current user"""
    try:
        social_service = EnhancedSocialService(db)
        rooms = social_service.chat_manager.get_user_chat_rooms(current_user)
        
        return {
            "rooms": rooms,
            "total_count": len(rooms)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/rooms/{room_id}/messages")
async def send_chat_message(
    room_id: int,
    request: SendMessageRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message in a chat room"""
    try:
        social_service = EnhancedSocialService(db)
        result = social_service.send_chat_message(
            user_id=current_user,
            room_id=room_id,
            content=request.content,
            message_type=request.message_type
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/rooms/{room_id}/messages")
async def get_room_messages(
    room_id: int,
    limit: int = Query(50, description="Number of messages to return"),
    offset: int = Query(0, description="Number of messages to skip"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for a chat room"""
    try:
        social_service = EnhancedSocialService(db)
        messages = social_service.chat_manager.get_room_messages(room_id, limit, offset)
        
        return {
            "messages": messages,
            "total_count": len(messages)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/chat/rooms/{room_id}/ws")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    room_id: int,
    user_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    try:
        social_service = EnhancedSocialService(db)
        
        # Add user to room's WebSocket connections
        await social_service.websocket_manager.connect(user_id, websocket)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data.get("type") == "join_room":
                # User joined the room
                await websocket.send_text(json.dumps({
                    "type": "user_joined",
                    "user_id": user_id,
                    "message": f"User {user_id} joined the room"
                }))
            
            elif message_data.get("type") == "typing":
                # User is typing
                await social_service.websocket_manager.broadcast_to_room(
                    room_id, user_id, {
                        "type": "user_typing",
                        "user_id": user_id,
                        "is_typing": message_data.get("is_typing", False)
                    }
                )
            
            elif message_data.get("type") == "message":
                # Send message to room
                result = social_service.send_chat_message(
                    user_id=user_id,
                    room_id=room_id,
                    content=message_data.get("content", ""),
                    message_type=message_data.get("message_type", "text")
                )
                
                if "error" in result:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": result["error"]
                    }))
    
    except WebSocketDisconnect:
        await social_service.websocket_manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await social_service.websocket_manager.disconnect(user_id)

# Enhanced Following System
@router.post("/follow")
async def follow_user(
    request: FollowUserRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Follow a user"""
    try:
        social_service = EnhancedSocialService(db)
        result = social_service.follow_user(current_user, request.following_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/follow/{following_id}")
async def unfollow_user(
    following_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unfollow a user"""
    try:
        social_service = EnhancedSocialService(db)
        result = social_service.unfollow_user(current_user, following_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions")
async def get_user_suggestions(
    limit: int = Query(10, description="Number of suggestions to return"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user suggestions based on mutual connections and interests"""
    try:
        social_service = EnhancedSocialService(db)
        result = social_service.get_user_suggestions(current_user, limit)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/followers/{user_id}")
async def get_user_followers(
    user_id: str,
    limit: int = Query(50, description="Number of followers to return"),
    offset: int = Query(0, description="Number of followers to skip"),
    db: Session = Depends(get_db)
):
    """Get followers of a user"""
    try:
        from app.db import models
        
        followers = db.query(models.SocialFollow).filter(
            models.SocialFollow.following_id == user_id
        ).offset(offset).limit(limit).all()
        
        follower_data = []
        for follow in followers:
            user = db.query(models.User).filter(models.User.id == follow.follower_id).first()
            if user:
                follower_data.append({
                    "user_id": user.id,
                    "username": user.username,
                    "followed_at": follow.created_at.isoformat()
                })
        
        return {
            "followers": follower_data,
            "total_count": len(follower_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/following/{user_id}")
async def get_user_following(
    user_id: str,
    limit: int = Query(50, description="Number of following to return"),
    offset: int = Query(0, description="Number of following to skip"),
    db: Session = Depends(get_db)
):
    """Get users that a user is following"""
    try:
        from app.db import models
        
        following = db.query(models.SocialFollow).filter(
            models.SocialFollow.follower_id == user_id
        ).offset(offset).limit(limit).all()
        
        following_data = []
        for follow in following:
            user = db.query(models.User).filter(models.User.id == follow.following_id).first()
            if user:
                following_data.append({
                    "user_id": user.id,
                    "username": user.username,
                    "followed_at": follow.created_at.isoformat()
                })
        
        return {
            "following": following_data,
            "total_count": len(following_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Content Moderation
@router.post("/moderate")
async def moderate_content(
    content: str,
    db: Session = Depends(get_db)
):
    """Moderate content for inappropriate material"""
    try:
        social_service = EnhancedSocialService(db)
        result = social_service.moderate_content(content)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/report")
async def report_content(
    request: ReportContentRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Report inappropriate content"""
    try:
        social_service = EnhancedSocialService(db)
        result = social_service.report_content(
            user_id=current_user,
            content_type=request.content_type,
            content_id=request.content_id,
            reason=request.reason,
            description=request.description
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Social Analytics
@router.get("/analytics/{user_id}")
async def get_social_analytics(
    user_id: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get social analytics for a user"""
    try:
        from app.db import models
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get post statistics
        posts = db.query(models.SocialPost).filter(
            and_(
                models.SocialPost.user_id == user_id,
                models.SocialPost.created_at >= start_date,
                models.SocialPost.created_at <= end_date
            )
        ).all()
        
        total_posts = len(posts)
        total_likes = sum(post.likes_count for post in posts)
        total_comments = sum(post.comments_count for post in posts)
        total_shares = sum(post.shares_count for post in posts)
        
        # Get follower growth
        followers = db.query(models.SocialFollow).filter(
            models.SocialFollow.following_id == user_id
        ).all()
        
        # Get engagement rate
        engagement_rate = 0
        if total_posts > 0:
            engagement_rate = (total_likes + total_comments + total_shares) / total_posts
        
        # Get top performing posts
        top_posts = sorted(posts, key=lambda x: x.likes_count + x.comments_count + x.shares_count, reverse=True)[:5]
        
        return {
            "user_id": user_id,
            "period_days": days,
            "statistics": {
                "total_posts": total_posts,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "total_shares": total_shares,
                "total_followers": len(followers),
                "engagement_rate": round(engagement_rate, 2)
            },
            "top_posts": [
                {
                    "id": post.id,
                    "content": post.content[:100] + "..." if len(post.content) > 100 else post.content,
                    "likes": post.likes_count,
                    "comments": post.comments_count,
                    "shares": post.shares_count,
                    "created_at": post.created_at.isoformat()
                }
                for post in top_posts
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Trending Content
@router.get("/trending")
async def get_trending_content(
    limit: int = Query(20, description="Number of trending items to return"),
    timeframe: str = Query("24h", description="Timeframe: 1h, 24h, 7d, 30d"),
    db: Session = Depends(get_db)
):
    """Get trending content"""
    try:
        from app.db import models
        from datetime import datetime, timedelta
        
        # Calculate time range
        now = datetime.now()
        if timeframe == "1h":
            start_time = now - timedelta(hours=1)
        elif timeframe == "24h":
            start_time = now - timedelta(days=1)
        elif timeframe == "7d":
            start_time = now - timedelta(days=7)
        elif timeframe == "30d":
            start_time = now - timedelta(days=30)
        else:
            start_time = now - timedelta(days=1)
        
        # Get trending posts
        trending_posts = db.query(models.SocialPost).filter(
            and_(
                models.SocialPost.created_at >= start_time,
                models.SocialPost.is_public == True
            )
        ).order_by(
            desc(
                models.SocialPost.likes_count * 2 + 
                models.SocialPost.comments_count * 3 + 
                models.SocialPost.shares_count * 5
            )
        ).limit(limit).all()
        
        # Get trending symbols
        trending_symbols = db.query(
            models.SocialPost.symbol,
            func.count(models.SocialPost.id).label('post_count'),
            func.sum(models.SocialPost.likes_count).label('total_likes')
        ).filter(
            and_(
                models.SocialPost.created_at >= start_time,
                models.SocialPost.symbol.isnot(None),
                models.SocialPost.is_public == True
            )
        ).group_by(models.SocialPost.symbol).order_by(desc('post_count')).limit(10).all()
        
        return {
            "timeframe": timeframe,
            "trending_posts": [
                {
                    "id": post.id,
                    "content": post.content[:100] + "..." if len(post.content) > 100 else post.content,
                    "symbol": post.symbol,
                    "likes": post.likes_count,
                    "comments": post.comments_count,
                    "shares": post.shares_count,
                    "created_at": post.created_at.isoformat()
                }
                for post in trending_posts
            ],
            "trending_symbols": [
                {
                    "symbol": symbol,
                    "post_count": post_count,
                    "total_likes": total_likes
                }
                for symbol, post_count, total_likes in trending_symbols
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper function for authentication (you'll need to implement this)
def get_current_user() -> str:
    """Get current authenticated user - implement based on your auth system"""
    # This is a placeholder - implement based on your authentication system
    return "user1"
