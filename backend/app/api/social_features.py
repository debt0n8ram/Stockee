from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import json

from app.db.database import get_db
from app.services.social_features_service import SocialFeaturesService
from app.api.auth import get_current_user

router = APIRouter()

class CreatePostRequest(BaseModel):
    content: str
    post_type: str = "general"
    symbol: Optional[str] = None
    tags: Optional[List[str]] = None

class CommentRequest(BaseModel):
    content: str

class FollowRequest(BaseModel):
    following_id: str

@router.post("/posts")
async def create_post(
    request: CreatePostRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new social post."""
    try:
        service = SocialFeaturesService(db)
        result = service.create_post(
            user_id=current_user,
            content=request.content,
            post_type=request.post_type,
            symbol=request.symbol,
            tags=request.tags
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feed")
async def get_feed(
    limit: int = Query(50, description="Number of posts to return"),
    offset: int = Query(0, description="Number of posts to skip"),
    post_type: Optional[str] = Query(None, description="Filter by post type"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get social feed for a user."""
    try:
        service = SocialFeaturesService(db)
        result = service.get_feed(
            user_id=current_user,
            limit=limit,
            offset=offset,
            post_type=post_type,
            symbol=symbol
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Like or unlike a post."""
    try:
        service = SocialFeaturesService(db)
        result = service.like_post(user_id=current_user, post_id=post_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/{post_id}/comment")
async def comment_on_post(
    post_id: int,
    request: CommentRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a comment to a post."""
    try:
        service = SocialFeaturesService(db)
        result = service.comment_on_post(
            user_id=current_user,
            post_id=post_id,
            content=request.content
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/follow")
async def follow_user(
    request: FollowRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Follow or unfollow a user."""
    try:
        service = SocialFeaturesService(db)
        result = service.follow_user(
            follower_id=current_user,
            following_id=request.following_id
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/profile")
async def get_user_profile(
    user_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile with social stats."""
    try:
        service = SocialFeaturesService(db)
        result = service.get_user_profile(user_id=user_id, viewer_id=current_user)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trending/posts")
async def get_trending_posts(
    limit: int = Query(20, description="Number of posts to return"),
    time_period: str = Query("24h", description="Time period for trending"),
    db: Session = Depends(get_db)
):
    """Get trending posts based on engagement."""
    try:
        service = SocialFeaturesService(db)
        result = service.get_trending_posts(limit=limit, time_period=time_period)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trending/symbols")
async def get_trending_symbols(
    limit: int = Query(20, description="Number of symbols to return"),
    time_period: str = Query("24h", description="Time period for trending"),
    db: Session = Depends(get_db)
):
    """Get trending symbols based on social activity."""
    try:
        service = SocialFeaturesService(db)
        result = service.get_trending_symbols(limit=limit, time_period=time_period)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_posts(
    query: str = Query(..., description="Search query"),
    limit: int = Query(50, description="Number of posts to return"),
    offset: int = Query(0, description="Number of posts to skip"),
    db: Session = Depends(get_db)
):
    """Search posts by content or tags."""
    try:
        service = SocialFeaturesService(db)
        result = service.search_posts(query=query, limit=limit, offset=offset)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/followers")
async def get_user_followers(
    user_id: str,
    limit: int = Query(50, description="Number of followers to return"),
    offset: int = Query(0, description="Number of followers to skip"),
    db: Session = Depends(get_db)
):
    """Get list of user's followers."""
    try:
        service = SocialFeaturesService(db)
        result = service.get_user_followers(user_id=user_id, limit=limit, offset=offset)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/following")
async def get_user_following(
    user_id: str,
    limit: int = Query(50, description="Number of following to return"),
    offset: int = Query(0, description="Number of following to skip"),
    db: Session = Depends(get_db)
):
    """Get list of users that the user is following."""
    try:
        service = SocialFeaturesService(db)
        result = service.get_user_following(user_id=user_id, limit=limit, offset=offset)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/{post_id}")
async def get_post_details(
    post_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific post."""
    try:
        from app.db import models
        
        post = db.query(models.SocialPost).filter(models.SocialPost.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Get user info
        user = db.query(models.User).filter(models.User.id == post.user_id).first()
        
        # Get comments
        comments = db.query(models.SocialComment).filter(
            models.SocialComment.post_id == post_id
        ).order_by(models.SocialComment.created_at.desc()).all()
        
        # Check if current user liked the post
        user_liked = db.query(models.SocialLike).filter(
            models.SocialLike.post_id == post_id,
            models.SocialLike.user_id == current_user
        ).first() is not None
        
        # Format comments
        formatted_comments = []
        for comment in comments:
            comment_user = db.query(models.User).filter(models.User.id == comment.user_id).first()
            formatted_comments.append({
                "id": comment.id,
                "user_id": comment.user_id,
                "username": comment_user.username if comment_user else "Unknown",
                "content": comment.content,
                "created_at": comment.created_at.isoformat()
            })
        
        return {
            "id": post.id,
            "user_id": post.user_id,
            "username": user.username if user else "Unknown",
            "content": post.content,
            "post_type": post.post_type,
            "symbol": post.symbol,
            "tags": json.loads(post.tags) if post.tags else [],
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "shares_count": post.shares_count,
            "user_liked": user_liked,
            "created_at": post.created_at.isoformat(),
            "comments": formatted_comments
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a post (only by the author)."""
    try:
        from app.db import models
        
        post = db.query(models.SocialPost).filter(
            models.SocialPost.id == post_id,
            models.SocialPost.user_id == current_user
        ).first()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found or not authorized")
        
        # Delete associated likes, comments, and shares
        db.query(models.SocialLike).filter(models.SocialLike.post_id == post_id).delete()
        db.query(models.SocialComment).filter(models.SocialComment.post_id == post_id).delete()
        db.query(models.SocialShare).filter(models.SocialShare.post_id == post_id).delete()
        
        # Delete the post
        db.delete(post)
        db.commit()
        
        return {"success": True, "message": "Post deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/posts")
async def get_user_posts(
    user_id: str,
    limit: int = Query(50, description="Number of posts to return"),
    offset: int = Query(0, description="Number of posts to skip"),
    post_type: Optional[str] = Query(None, description="Filter by post type"),
    db: Session = Depends(get_db)
):
    """Get posts by a specific user."""
    try:
        from app.db import models
        
        # Build query
        query = db.query(models.SocialPost).filter(
            models.SocialPost.user_id == user_id,
            models.SocialPost.is_public == True
        )
        
        if post_type:
            query = query.filter(models.SocialPost.post_type == post_type)
        
        # Order by creation date
        query = query.order_by(models.SocialPost.created_at.desc())
        
        # Apply pagination
        posts = query.offset(offset).limit(limit).all()
        
        # Format posts
        formatted_posts = []
        for post in posts:
            # Get user info
            user = db.query(models.User).filter(models.User.id == post.user_id).first()
            
            formatted_posts.append({
                "id": post.id,
                "user_id": post.user_id,
                "username": user.username if user else "Unknown",
                "content": post.content,
                "post_type": post.post_type,
                "symbol": post.symbol,
                "tags": json.loads(post.tags) if post.tags else [],
                "likes_count": post.likes_count,
                "comments_count": post.comments_count,
                "shares_count": post.shares_count,
                "created_at": post.created_at.isoformat()
            })
        
        return {
            "posts": formatted_posts,
            "total": len(formatted_posts),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
