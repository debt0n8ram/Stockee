import logging
import json
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, desc, func

from app.db import models

logger = logging.getLogger(__name__)

class SocialFeaturesService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_post(self, user_id: str, content: str, post_type: str = "general", 
                   symbol: Optional[str] = None, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new social post."""
        try:
            # Create post
            post = models.SocialPost(
                user_id=user_id,
                content=content,
                post_type=post_type,
                symbol=symbol,
                tags=json.dumps(tags) if tags else None,
                likes_count=0,
                comments_count=0,
                shares_count=0,
                is_public=True
            )
            
            self.db.add(post)
            self.db.commit()
            self.db.refresh(post)
            
            return {
                "success": True,
                "post_id": post.id,
                "message": "Post created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating post: {e}")
            return {"error": str(e)}
    
    def get_feed(self, user_id: str, limit: int = 50, offset: int = 0, 
                post_type: Optional[str] = None, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get social feed for a user."""
        try:
            # Get user's following list
            following = self.db.query(models.SocialFollow).filter(
                models.SocialFollow.follower_id == user_id
            ).all()
            
            following_ids = [f.following_id for f in following]
            following_ids.append(user_id)  # Include user's own posts
            
            # Build query
            query = self.db.query(models.SocialPost).filter(
                models.SocialPost.user_id.in_(following_ids),
                models.SocialPost.is_public == True
            )
            
            if post_type:
                query = query.filter(models.SocialPost.post_type == post_type)
            
            if symbol:
                query = query.filter(models.SocialPost.symbol == symbol)
            
            # Order by creation date
            query = query.order_by(desc(models.SocialPost.created_at))
            
            # Apply pagination
            posts = query.offset(offset).limit(limit).all()
            
            # Format posts
            formatted_posts = []
            for post in posts:
                # Get user info
                user = self.db.query(models.User).filter(models.User.id == post.user_id).first()
                
                # Get likes
                likes = self.db.query(models.SocialLike).filter(
                    models.SocialLike.post_id == post.id
                ).all()
                
                # Get comments
                comments = self.db.query(models.SocialComment).filter(
                    models.SocialComment.post_id == post.id
                ).order_by(desc(models.SocialComment.created_at)).limit(5).all()
                
                # Check if current user liked the post
                user_liked = self.db.query(models.SocialLike).filter(
                    and_(
                        models.SocialLike.post_id == post.id,
                        models.SocialLike.user_id == user_id
                    )
                ).first() is not None
                
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
                    "user_liked": user_liked,
                    "created_at": post.created_at.isoformat(),
                    "comments": [
                        {
                            "id": comment.id,
                            "user_id": comment.user_id,
                            "content": comment.content,
                            "created_at": comment.created_at.isoformat()
                        } for comment in comments
                    ]
                })
            
            return {
                "posts": formatted_posts,
                "total": len(formatted_posts),
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Error getting feed: {e}")
            return {"error": str(e)}
    
    def like_post(self, user_id: str, post_id: int) -> Dict[str, Any]:
        """Like or unlike a post."""
        try:
            # Check if post exists
            post = self.db.query(models.SocialPost).filter(models.SocialPost.id == post_id).first()
            if not post:
                return {"error": "Post not found"}
            
            # Check if user already liked the post
            existing_like = self.db.query(models.SocialLike).filter(
                and_(
                    models.SocialLike.post_id == post_id,
                    models.SocialLike.user_id == user_id
                )
            ).first()
            
            if existing_like:
                # Unlike the post
                self.db.delete(existing_like)
                post.likes_count = max(0, post.likes_count - 1)
                action = "unliked"
            else:
                # Like the post
                like = models.SocialLike(
                    user_id=user_id,
                    post_id=post_id
                )
                self.db.add(like)
                post.likes_count += 1
                action = "liked"
            
            self.db.commit()
            
            return {
                "success": True,
                "action": action,
                "likes_count": post.likes_count
            }
            
        except Exception as e:
            logger.error(f"Error liking post: {e}")
            return {"error": str(e)}
    
    def comment_on_post(self, user_id: str, post_id: int, content: str) -> Dict[str, Any]:
        """Add a comment to a post."""
        try:
            # Check if post exists
            post = self.db.query(models.SocialPost).filter(models.SocialPost.id == post_id).first()
            if not post:
                return {"error": "Post not found"}
            
            # Create comment
            comment = models.SocialComment(
                user_id=user_id,
                post_id=post_id,
                content=content
            )
            
            self.db.add(comment)
            post.comments_count += 1
            self.db.commit()
            self.db.refresh(comment)
            
            return {
                "success": True,
                "comment_id": comment.id,
                "comments_count": post.comments_count
            }
            
        except Exception as e:
            logger.error(f"Error commenting on post: {e}")
            return {"error": str(e)}
    
    def follow_user(self, follower_id: str, following_id: str) -> Dict[str, Any]:
        """Follow or unfollow a user."""
        try:
            if follower_id == following_id:
                return {"error": "Cannot follow yourself"}
            
            # Check if follow relationship already exists
            existing_follow = self.db.query(models.SocialFollow).filter(
                and_(
                    models.SocialFollow.follower_id == follower_id,
                    models.SocialFollow.following_id == following_id
                )
            ).first()
            
            if existing_follow:
                # Unfollow
                self.db.delete(existing_follow)
                action = "unfollowed"
            else:
                # Follow
                follow = models.SocialFollow(
                    follower_id=follower_id,
                    following_id=following_id
                )
                self.db.add(follow)
                action = "followed"
            
            self.db.commit()
            
            return {
                "success": True,
                "action": action
            }
            
        except Exception as e:
            logger.error(f"Error following user: {e}")
            return {"error": str(e)}
    
    def get_user_profile(self, user_id: str, viewer_id: Optional[str] = None) -> Dict[str, Any]:
        """Get user profile with social stats."""
        try:
            # Get user info
            user = self.db.query(models.User).filter(models.User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            # Get follower count
            followers_count = self.db.query(models.SocialFollow).filter(
                models.SocialFollow.following_id == user_id
            ).count()
            
            # Get following count
            following_count = self.db.query(models.SocialFollow).filter(
                models.SocialFollow.follower_id == user_id
            ).count()
            
            # Get posts count
            posts_count = self.db.query(models.SocialPost).filter(
                models.SocialPost.user_id == user_id,
                models.SocialPost.is_public == True
            ).count()
            
            # Check if viewer is following this user
            is_following = False
            if viewer_id and viewer_id != user_id:
                follow = self.db.query(models.SocialFollow).filter(
                    and_(
                        models.SocialFollow.follower_id == viewer_id,
                        models.SocialFollow.following_id == user_id
                    )
                ).first()
                is_following = follow is not None
            
            # Get recent posts
            recent_posts = self.db.query(models.SocialPost).filter(
                models.SocialPost.user_id == user_id,
                models.SocialPost.is_public == True
            ).order_by(desc(models.SocialPost.created_at)).limit(10).all()
            
            formatted_posts = []
            for post in recent_posts:
                formatted_posts.append({
                    "id": post.id,
                    "content": post.content,
                    "post_type": post.post_type,
                    "symbol": post.symbol,
                    "likes_count": post.likes_count,
                    "comments_count": post.comments_count,
                    "created_at": post.created_at.isoformat()
                })
            
            return {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "followers_count": followers_count,
                "following_count": following_count,
                "posts_count": posts_count,
                "is_following": is_following,
                "recent_posts": formatted_posts
            }
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return {"error": str(e)}
    
    def get_trending_posts(self, limit: int = 20, time_period: str = "24h") -> Dict[str, Any]:
        """Get trending posts based on engagement."""
        try:
            # Calculate time threshold
            if time_period == "24h":
                threshold = datetime.now() - timedelta(hours=24)
            elif time_period == "7d":
                threshold = datetime.now() - timedelta(days=7)
            elif time_period == "30d":
                threshold = datetime.now() - timedelta(days=30)
            else:
                threshold = datetime.now() - timedelta(hours=24)
            
            # Get trending posts
            posts = self.db.query(models.SocialPost).filter(
                and_(
                    models.SocialPost.created_at >= threshold,
                    models.SocialPost.is_public == True
                )
            ).order_by(desc(models.SocialPost.likes_count + models.SocialPost.comments_count)).limit(limit).all()
            
            # Format posts
            formatted_posts = []
            for post in posts:
                # Get user info
                user = self.db.query(models.User).filter(models.User.id == post.user_id).first()
                
                # Calculate engagement score
                engagement_score = post.likes_count + (post.comments_count * 2) + post.shares_count
                
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
                    "engagement_score": engagement_score,
                    "created_at": post.created_at.isoformat()
                })
            
            return {
                "posts": formatted_posts,
                "time_period": time_period,
                "total": len(formatted_posts)
            }
            
        except Exception as e:
            logger.error(f"Error getting trending posts: {e}")
            return {"error": str(e)}
    
    def get_trending_symbols(self, limit: int = 20, time_period: str = "24h") -> Dict[str, Any]:
        """Get trending symbols based on social activity."""
        try:
            # Calculate time threshold
            if time_period == "24h":
                threshold = datetime.now() - timedelta(hours=24)
            elif time_period == "7d":
                threshold = datetime.now() - timedelta(days=7)
            elif time_period == "30d":
                threshold = datetime.now() - timedelta(days=30)
            else:
                threshold = datetime.now() - timedelta(hours=24)
            
            # Get symbol activity
            symbol_activity = self.db.query(
                models.SocialPost.symbol,
                func.count(models.SocialPost.id).label('post_count'),
                func.sum(models.SocialPost.likes_count).label('total_likes'),
                func.sum(models.SocialPost.comments_count).label('total_comments')
            ).filter(
                and_(
                    models.SocialPost.created_at >= threshold,
                    models.SocialPost.symbol.isnot(None),
                    models.SocialPost.is_public == True
                )
            ).group_by(models.SocialPost.symbol).order_by(
                desc('post_count + total_likes + total_comments')
            ).limit(limit).all()
            
            trending_symbols = []
            for symbol_data in symbol_activity:
                engagement_score = symbol_data.post_count + symbol_data.total_likes + symbol_data.total_comments
                trending_symbols.append({
                    "symbol": symbol_data.symbol,
                    "post_count": symbol_data.post_count,
                    "total_likes": symbol_data.total_likes,
                    "total_comments": symbol_data.total_comments,
                    "engagement_score": engagement_score
                })
            
            return {
                "symbols": trending_symbols,
                "time_period": time_period,
                "total": len(trending_symbols)
            }
            
        except Exception as e:
            logger.error(f"Error getting trending symbols: {e}")
            return {"error": str(e)}
    
    def search_posts(self, query: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Search posts by content or tags."""
        try:
            # Search in content and tags
            posts = self.db.query(models.SocialPost).filter(
                and_(
                    models.SocialPost.is_public == True,
                    or_(
                        models.SocialPost.content.ilike(f"%{query}%"),
                        models.SocialPost.tags.ilike(f"%{query}%")
                    )
                )
            ).order_by(desc(models.SocialPost.created_at)).offset(offset).limit(limit).all()
            
            # Format posts
            formatted_posts = []
            for post in posts:
                # Get user info
                user = self.db.query(models.User).filter(models.User.id == post.user_id).first()
                
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
                "query": query,
                "total": len(formatted_posts),
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Error searching posts: {e}")
            return {"error": str(e)}
    
    def get_user_followers(self, user_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get list of user's followers."""
        try:
            followers = self.db.query(models.SocialFollow).filter(
                models.SocialFollow.following_id == user_id
            ).offset(offset).limit(limit).all()
            
            formatted_followers = []
            for follow in followers:
                user = self.db.query(models.User).filter(models.User.id == follow.follower_id).first()
                if user:
                    formatted_followers.append({
                        "user_id": user.id,
                        "username": user.username,
                        "followed_at": follow.created_at.isoformat()
                    })
            
            return {
                "followers": formatted_followers,
                "total": len(formatted_followers),
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Error getting followers: {e}")
            return {"error": str(e)}
    
    def get_user_following(self, user_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get list of users that the user is following."""
        try:
            following = self.db.query(models.SocialFollow).filter(
                models.SocialFollow.follower_id == user_id
            ).offset(offset).limit(limit).all()
            
            formatted_following = []
            for follow in following:
                user = self.db.query(models.User).filter(models.User.id == follow.following_id).first()
                if user:
                    formatted_following.append({
                        "user_id": user.id,
                        "username": user.username,
                        "followed_at": follow.created_at.isoformat()
                    })
            
            return {
                "following": formatted_following,
                "total": len(formatted_following),
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Error getting following: {e}")
            return {"error": str(e)}
