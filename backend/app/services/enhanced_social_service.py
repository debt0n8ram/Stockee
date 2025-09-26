import logging
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, desc, func, text
from collections import defaultdict
import asyncio
from app.db import models
from app.services.websocket_service import WebSocketManager

logger = logging.getLogger(__name__)

class EnhancedSocialService:
    """Enhanced social features service with real-time chat, following, and content moderation"""
    
    def __init__(self, db: Session):
        self.db = db
        self.websocket_manager = WebSocketManager()
        self.content_moderator = ContentModerator()
        self.chat_manager = ChatManager(db)
        
    # Enhanced Post Management
    def create_enhanced_post(self, user_id: str, content: str, post_type: str = "general", 
                           symbol: Optional[str] = None, tags: Optional[List[str]] = None,
                           images: Optional[List[str]] = None, mentions: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new social post with enhanced features"""
        try:
            # Content moderation
            moderation_result = self.content_moderator.moderate_content(content)
            if not moderation_result["approved"]:
                return {
                    "error": "Content violates community guidelines",
                    "reason": moderation_result["reason"],
                    "suggestions": moderation_result.get("suggestions", [])
                }
            
            # Extract mentions and hashtags
            extracted_mentions = self._extract_mentions(content)
            extracted_hashtags = self._extract_hashtags(content)
            
            # Create post
            post = models.SocialPost(
                user_id=user_id,
                content=content,
                post_type=post_type,
                symbol=symbol,
                tags=json.dumps(tags or []),
                mentions=json.dumps(extracted_mentions),
                hashtags=json.dumps(extracted_hashtags),
                images=json.dumps(images or []),
                likes_count=0,
                comments_count=0,
                shares_count=0,
                views_count=0,
                is_public=True,
                moderation_score=moderation_result["score"],
                created_at=datetime.now()
            )
            
            self.db.add(post)
            self.db.commit()
            self.db.refresh(post)
            
            # Notify mentioned users
            asyncio.create_task(self._notify_mentioned_users(post.id, extracted_mentions))
            
            # Update user activity
            self._update_user_activity(user_id, "post_created")
            
            # Broadcast to followers
            asyncio.create_task(self._broadcast_to_followers(user_id, "new_post", {
                "post_id": post.id,
                "content": content[:100] + "..." if len(content) > 100 else content,
                "symbol": symbol,
                "post_type": post_type
            }))
            
            return {
                "success": True,
                "post_id": post.id,
                "message": "Post created successfully",
                "moderation_score": moderation_result["score"]
            }
            
        except Exception as e:
            logger.error(f"Error creating enhanced post: {e}")
            return {"error": str(e)}
    
    def get_enhanced_feed(self, user_id: str, limit: int = 50, offset: int = 0, 
                         post_type: Optional[str] = None, symbol: Optional[str] = None,
                         algorithm: str = "chronological") -> Dict[str, Any]:
        """Get enhanced social feed with different algorithms"""
        try:
            # Get user preferences
            user_preferences = self._get_user_preferences(user_id)
            
            # Build base query
            if algorithm == "chronological":
                posts = self._get_chronological_feed(user_id, limit, offset, post_type, symbol)
            elif algorithm == "popular":
                posts = self._get_popular_feed(user_id, limit, offset, post_type, symbol)
            elif algorithm == "personalized":
                posts = self._get_personalized_feed(user_id, limit, offset, post_type, symbol, user_preferences)
            else:
                posts = self._get_chronological_feed(user_id, limit, offset, post_type, symbol)
            
            # Enhance posts with additional data
            enhanced_posts = []
            for post in posts:
                enhanced_post = self._enhance_post_data(post, user_id)
                enhanced_posts.append(enhanced_post)
            
            return {
                "posts": enhanced_posts,
                "total_count": len(enhanced_posts),
                "algorithm": algorithm,
                "has_more": len(enhanced_posts) == limit
            }
            
        except Exception as e:
            logger.error(f"Error getting enhanced feed: {e}")
            return {"error": str(e)}
    
    def _get_chronological_feed(self, user_id: str, limit: int, offset: int, 
                               post_type: Optional[str], symbol: Optional[str]) -> List[models.SocialPost]:
        """Get chronological feed"""
        following_ids = self._get_following_ids(user_id)
        following_ids.append(user_id)
        
        query = self.db.query(models.SocialPost).filter(
            models.SocialPost.user_id.in_(following_ids),
            models.SocialPost.is_public == True
        )
        
        if post_type:
            query = query.filter(models.SocialPost.post_type == post_type)
        if symbol:
            query = query.filter(models.SocialPost.symbol == symbol)
        
        return query.order_by(desc(models.SocialPost.created_at)).offset(offset).limit(limit).all()
    
    def _get_popular_feed(self, user_id: str, limit: int, offset: int, 
                         post_type: Optional[str], symbol: Optional[str]) -> List[models.SocialPost]:
        """Get popular feed based on engagement"""
        following_ids = self._get_following_ids(user_id)
        following_ids.append(user_id)
        
        query = self.db.query(models.SocialPost).filter(
            models.SocialPost.user_id.in_(following_ids),
            models.SocialPost.is_public == True,
            models.SocialPost.created_at >= datetime.now() - timedelta(days=7)  # Last 7 days
        )
        
        if post_type:
            query = query.filter(models.SocialPost.post_type == post_type)
        if symbol:
            query = query.filter(models.SocialPost.symbol == symbol)
        
        # Order by engagement score
        return query.order_by(
            desc(
                models.SocialPost.likes_count * 2 + 
                models.SocialPost.comments_count * 3 + 
                models.SocialPost.shares_count * 5 +
                models.SocialPost.views_count * 0.1
            )
        ).offset(offset).limit(limit).all()
    
    def _get_personalized_feed(self, user_id: str, limit: int, offset: int, 
                              post_type: Optional[str], symbol: Optional[str], 
                              preferences: Dict) -> List[models.SocialPost]:
        """Get personalized feed based on user preferences and behavior"""
        following_ids = self._get_following_ids(user_id)
        following_ids.append(user_id)
        
        # Get user's interaction history
        user_interactions = self._get_user_interactions(user_id)
        
        # Build personalized query
        query = self.db.query(models.SocialPost).filter(
            models.SocialPost.user_id.in_(following_ids),
            models.SocialPost.is_public == True
        )
        
        if post_type:
            query = query.filter(models.SocialPost.post_type == post_type)
        if symbol:
            query = query.filter(models.SocialPost.symbol == symbol)
        
        # Apply personalization filters
        if preferences.get("preferred_symbols"):
            query = query.filter(
                or_(
                    models.SocialPost.symbol.in_(preferences["preferred_symbols"]),
                    models.SocialPost.symbol.is_(None)
                )
            )
        
        # Order by personalization score
        posts = query.order_by(desc(models.SocialPost.created_at)).offset(offset).limit(limit * 2).all()
        
        # Apply personalization scoring
        personalized_posts = self._score_posts_for_user(posts, user_interactions, preferences)
        
        return personalized_posts[:limit]
    
    def _score_posts_for_user(self, posts: List[models.SocialPost], 
                             interactions: Dict, preferences: Dict) -> List[models.SocialPost]:
        """Score posts for personalization"""
        scored_posts = []
        
        for post in posts:
            score = 0
            
            # Base score from engagement
            score += post.likes_count * 0.1
            score += post.comments_count * 0.2
            score += post.shares_count * 0.3
            
            # Recency score
            hours_old = (datetime.now() - post.created_at).total_seconds() / 3600
            recency_score = max(0, 1 - (hours_old / 168))  # Decay over 1 week
            score += recency_score * 0.5
            
            # Symbol preference score
            if post.symbol and post.symbol in preferences.get("preferred_symbols", []):
                score += 1.0
            
            # Author preference score
            if post.user_id in interactions.get("frequently_interacted_authors", []):
                score += 0.8
            
            # Post type preference score
            if post.post_type in preferences.get("preferred_post_types", []):
                score += 0.3
            
            scored_posts.append((post, score))
        
        # Sort by score and return posts
        scored_posts.sort(key=lambda x: x[1], reverse=True)
        return [post for post, score in scored_posts]
    
    # Real-time Chat Features
    def create_chat_room(self, user_id: str, name: str, description: str = "", 
                        is_public: bool = True, max_members: int = 100) -> Dict[str, Any]:
        """Create a new chat room"""
        try:
            chat_room = models.ChatRoom(
                name=name,
                description=description,
                created_by=user_id,
                is_public=is_public,
                max_members=max_members,
                member_count=1,
                created_at=datetime.now()
            )
            
            self.db.add(chat_room)
            self.db.commit()
            self.db.refresh(chat_room)
            
            # Add creator as admin
            membership = models.ChatMembership(
                room_id=chat_room.id,
                user_id=user_id,
                role="admin",
                joined_at=datetime.now()
            )
            
            self.db.add(membership)
            self.db.commit()
            
            return {
                "success": True,
                "room_id": chat_room.id,
                "message": "Chat room created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating chat room: {e}")
            return {"error": str(e)}
    
    def send_chat_message(self, user_id: str, room_id: int, content: str, 
                         message_type: str = "text") -> Dict[str, Any]:
        """Send a message in a chat room"""
        try:
            # Check if user is member of the room
            membership = self.db.query(models.ChatMembership).filter(
                and_(
                    models.ChatMembership.room_id == room_id,
                    models.ChatMembership.user_id == user_id
                )
            ).first()
            
            if not membership:
                return {"error": "User is not a member of this chat room"}
            
            # Content moderation
            moderation_result = self.content_moderator.moderate_content(content)
            if not moderation_result["approved"]:
                return {
                    "error": "Message violates community guidelines",
                    "reason": moderation_result["reason"]
                }
            
            # Create message
            message = models.ChatMessage(
                room_id=room_id,
                user_id=user_id,
                content=content,
                message_type=message_type,
                moderation_score=moderation_result["score"],
                created_at=datetime.now()
            )
            
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            
            # Broadcast message to room members
            asyncio.create_task(self._broadcast_chat_message(room_id, message))
            
            return {
                "success": True,
                "message_id": message.id,
                "message": "Message sent successfully"
            }
            
        except Exception as e:
            logger.error(f"Error sending chat message: {e}")
            return {"error": str(e)}
    
    async def _broadcast_chat_message(self, room_id: int, message: models.ChatMessage):
        """Broadcast chat message to all room members"""
        try:
            # Get room members
            members = self.db.query(models.ChatMembership).filter(
                models.ChatMembership.room_id == room_id
            ).all()
            
            # Get user info
            user = self.db.query(models.User).filter(models.User.id == message.user_id).first()
            
            message_data = {
                "type": "chat_message",
                "room_id": room_id,
                "message_id": message.id,
                "user_id": message.user_id,
                "username": user.username if user else "Unknown",
                "content": message.content,
                "message_type": message.message_type,
                "timestamp": message.created_at.isoformat()
            }
            
            # Send to all members
            for member in members:
                await self.websocket_manager.send_to_user(member.user_id, message_data)
                
        except Exception as e:
            logger.error(f"Error broadcasting chat message: {e}")
    
    # Enhanced Following System
    def follow_user(self, follower_id: str, following_id: str) -> Dict[str, Any]:
        """Follow a user with enhanced features"""
        try:
            if follower_id == following_id:
                return {"error": "Cannot follow yourself"}
            
            # Check if already following
            existing_follow = self.db.query(models.SocialFollow).filter(
                and_(
                    models.SocialFollow.follower_id == follower_id,
                    models.SocialFollow.following_id == following_id
                )
            ).first()
            
            if existing_follow:
                return {"error": "Already following this user"}
            
            # Create follow relationship
            follow = models.SocialFollow(
                follower_id=follower_id,
                following_id=following_id,
                created_at=datetime.now()
            )
            
            self.db.add(follow)
            
            # Update follower counts
            self._update_follower_counts(following_id, 1)
            self._update_following_counts(follower_id, 1)
            
            self.db.commit()
            
            # Notify the followed user
            asyncio.create_task(self._notify_follow(follower_id, following_id))
            
            # Update user activity
            self._update_user_activity(follower_id, "user_followed")
            
            return {
                "success": True,
                "message": "Successfully followed user"
            }
            
        except Exception as e:
            logger.error(f"Error following user: {e}")
            return {"error": str(e)}
    
    def unfollow_user(self, follower_id: str, following_id: str) -> Dict[str, Any]:
        """Unfollow a user"""
        try:
            # Find and delete follow relationship
            follow = self.db.query(models.SocialFollow).filter(
                and_(
                    models.SocialFollow.follower_id == follower_id,
                    models.SocialFollow.following_id == following_id
                )
            ).first()
            
            if not follow:
                return {"error": "Not following this user"}
            
            self.db.delete(follow)
            
            # Update follower counts
            self._update_follower_counts(following_id, -1)
            self._update_following_counts(follower_id, -1)
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "Successfully unfollowed user"
            }
            
        except Exception as e:
            logger.error(f"Error unfollowing user: {e}")
            return {"error": str(e)}
    
    def get_user_suggestions(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get user suggestions based on mutual connections and interests"""
        try:
            # Get user's current following
            following = self.db.query(models.SocialFollow).filter(
                models.SocialFollow.follower_id == user_id
            ).all()
            following_ids = [f.following_id for f in following]
            following_ids.append(user_id)
            
            # Get mutual connections
            mutual_connections = self.db.query(
                models.SocialFollow.following_id,
                func.count(models.SocialFollow.follower_id).label('mutual_count')
            ).filter(
                and_(
                    models.SocialFollow.following_id.notin_(following_ids),
                    models.SocialFollow.follower_id.in_(
                        self.db.query(models.SocialFollow.following_id).filter(
                            models.SocialFollow.follower_id == user_id
                        )
                    )
                )
            ).group_by(models.SocialFollow.following_id).order_by(desc('mutual_count')).limit(limit).all()
            
            suggestions = []
            for suggestion in mutual_connections:
                user = self.db.query(models.User).filter(
                    models.User.id == suggestion.following_id
                ).first()
                
                if user:
                    suggestions.append({
                        "user_id": user.id,
                        "username": user.username,
                        "mutual_connections": suggestion.mutual_count,
                        "reason": f"{suggestion.mutual_count} mutual connections"
                    })
            
            return {
                "suggestions": suggestions,
                "total_count": len(suggestions)
            }
            
        except Exception as e:
            logger.error(f"Error getting user suggestions: {e}")
            return {"error": str(e)}
    
    # Content Moderation
    def moderate_content(self, content: str) -> Dict[str, Any]:
        """Moderate content for inappropriate material"""
        return self.content_moderator.moderate_content(content)
    
    def report_content(self, user_id: str, content_type: str, content_id: int, 
                      reason: str, description: str = "") -> Dict[str, Any]:
        """Report inappropriate content"""
        try:
            report = models.ContentReport(
                reporter_id=user_id,
                content_type=content_type,
                content_id=content_id,
                reason=reason,
                description=description,
                status="pending",
                created_at=datetime.now()
            )
            
            self.db.add(report)
            self.db.commit()
            
            return {
                "success": True,
                "report_id": report.id,
                "message": "Content reported successfully"
            }
            
        except Exception as e:
            logger.error(f"Error reporting content: {e}")
            return {"error": str(e)}
    
    # Utility Methods
    def _extract_mentions(self, content: str) -> List[str]:
        """Extract @mentions from content"""
        mentions = re.findall(r'@(\w+)', content)
        return list(set(mentions))
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract #hashtags from content"""
        hashtags = re.findall(r'#(\w+)', content)
        return list(set(hashtags))
    
    def _get_following_ids(self, user_id: str) -> List[str]:
        """Get list of user IDs that the user is following"""
        following = self.db.query(models.SocialFollow).filter(
            models.SocialFollow.follower_id == user_id
        ).all()
        return [f.following_id for f in following]
    
    def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences for personalization"""
        # This would typically come from a user preferences table
        # For now, return default preferences
        return {
            "preferred_symbols": [],
            "preferred_post_types": ["general", "analysis"],
            "preferred_authors": []
        }
    
    def _get_user_interactions(self, user_id: str) -> Dict[str, Any]:
        """Get user interaction history for personalization"""
        # This would analyze user's likes, comments, shares, etc.
        return {
            "frequently_interacted_authors": [],
            "preferred_content_types": [],
            "engagement_patterns": {}
        }
    
    def _enhance_post_data(self, post: models.SocialPost, user_id: str) -> Dict[str, Any]:
        """Enhance post data with additional information"""
        # Get user info
        user = self.db.query(models.User).filter(models.User.id == post.user_id).first()
        
        # Check if current user liked the post
        user_liked = self.db.query(models.SocialLike).filter(
            and_(
                models.SocialLike.post_id == post.id,
                models.SocialLike.user_id == user_id
            )
        ).first() is not None
        
        # Get recent comments
        comments = self.db.query(models.SocialComment).filter(
            models.SocialComment.post_id == post.id
        ).order_by(desc(models.SocialComment.created_at)).limit(3).all()
        
        return {
            "id": post.id,
            "content": post.content,
            "post_type": post.post_type,
            "symbol": post.symbol,
            "tags": json.loads(post.tags) if post.tags else [],
            "mentions": json.loads(post.mentions) if post.mentions else [],
            "hashtags": json.loads(post.hashtags) if post.hashtags else [],
            "images": json.loads(post.images) if post.images else [],
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "shares_count": post.shares_count,
            "views_count": post.views_count,
            "created_at": post.created_at.isoformat(),
            "user": {
                "id": user.id if user else None,
                "username": user.username if user else "Unknown",
                "avatar": getattr(user, 'avatar', None)
            },
            "user_liked": user_liked,
            "recent_comments": [
                {
                    "id": comment.id,
                    "content": comment.content,
                    "user_id": comment.user_id,
                    "created_at": comment.created_at.isoformat()
                }
                for comment in comments
            ]
        }
    
    def _update_user_activity(self, user_id: str, activity_type: str):
        """Update user activity tracking"""
        try:
            activity = models.UserActivity(
                user_id=user_id,
                activity_type=activity_type,
                timestamp=datetime.now()
            )
            self.db.add(activity)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error updating user activity: {e}")
    
    def _update_follower_counts(self, user_id: str, change: int):
        """Update follower count for a user"""
        try:
            user = self.db.query(models.User).filter(models.User.id == user_id).first()
            if user:
                current_count = getattr(user, 'followers_count', 0)
                user.followers_count = max(0, current_count + change)
                self.db.commit()
        except Exception as e:
            logger.error(f"Error updating follower count: {e}")
    
    def _update_following_counts(self, user_id: str, change: int):
        """Update following count for a user"""
        try:
            user = self.db.query(models.User).filter(models.User.id == user_id).first()
            if user:
                current_count = getattr(user, 'following_count', 0)
                user.following_count = max(0, current_count + change)
                self.db.commit()
        except Exception as e:
            logger.error(f"Error updating following count: {e}")
    
    async def _notify_mentioned_users(self, post_id: int, mentions: List[str]):
        """Notify users who were mentioned in a post"""
        try:
            for mention in mentions:
                user = self.db.query(models.User).filter(
                    models.User.username == mention
                ).first()
                
                if user:
                    notification = {
                        "type": "mention",
                        "post_id": post_id,
                        "message": f"You were mentioned in a post"
                    }
                    await self.websocket_manager.send_to_user(user.id, notification)
        except Exception as e:
            logger.error(f"Error notifying mentioned users: {e}")
    
    async def _notify_follow(self, follower_id: str, following_id: str):
        """Notify user when they are followed"""
        try:
            follower = self.db.query(models.User).filter(models.User.id == follower_id).first()
            
            notification = {
                "type": "follow",
                "follower_id": follower_id,
                "follower_username": follower.username if follower else "Unknown",
                "message": f"{follower.username if follower else 'Someone'} started following you"
            }
            
            await self.websocket_manager.send_to_user(following_id, notification)
        except Exception as e:
            logger.error(f"Error notifying follow: {e}")
    
    async def _broadcast_to_followers(self, user_id: str, event_type: str, data: Dict):
        """Broadcast event to user's followers"""
        try:
            followers = self.db.query(models.SocialFollow).filter(
                models.SocialFollow.following_id == user_id
            ).all()
            
            for follower in followers:
                await self.websocket_manager.send_to_user(follower.follower_id, {
                    "type": event_type,
                    "data": data
                })
        except Exception as e:
            logger.error(f"Error broadcasting to followers: {e}")


class ContentModerator:
    """Content moderation system"""
    
    def __init__(self):
        self.inappropriate_words = [
            "spam", "scam", "pump", "dump", "manipulation", "insider", "illegal"
        ]
        self.spam_patterns = [
            r"buy\s+now", r"sell\s+now", r"guaranteed\s+profit", r"get\s+rich\s+quick"
        ]
    
    def moderate_content(self, content: str) -> Dict[str, Any]:
        """Moderate content for inappropriate material"""
        try:
            content_lower = content.lower()
            
            # Check for inappropriate words
            for word in self.inappropriate_words:
                if word in content_lower:
                    return {
                        "approved": False,
                        "reason": f"Content contains inappropriate word: {word}",
                        "score": 0.0,
                        "suggestions": ["Please remove inappropriate language"]
                    }
            
            # Check for spam patterns
            for pattern in self.spam_patterns:
                if re.search(pattern, content_lower):
                    return {
                        "approved": False,
                        "reason": "Content appears to be spam",
                        "score": 0.2,
                        "suggestions": ["Avoid promotional language and guarantees"]
                    }
            
            # Check content length
            if len(content) < 10:
                return {
                    "approved": False,
                    "reason": "Content too short",
                    "score": 0.3,
                    "suggestions": ["Please provide more meaningful content"]
                }
            
            if len(content) > 1000:
                return {
                    "approved": False,
                    "reason": "Content too long",
                    "score": 0.4,
                    "suggestions": ["Please keep content under 1000 characters"]
                }
            
            # Calculate moderation score
            score = self._calculate_moderation_score(content)
            
            return {
                "approved": True,
                "reason": "Content approved",
                "score": score,
                "suggestions": []
            }
            
        except Exception as e:
            logger.error(f"Error moderating content: {e}")
            return {
                "approved": False,
                "reason": "Moderation error",
                "score": 0.0,
                "suggestions": []
            }
    
    def _calculate_moderation_score(self, content: str) -> float:
        """Calculate moderation score (0.0 to 1.0)"""
        score = 1.0
        
        # Penalize for excessive capitalization
        if len([c for c in content if c.isupper()]) > len(content) * 0.3:
            score -= 0.2
        
        # Penalize for excessive punctuation
        if content.count('!') > 3 or content.count('?') > 3:
            score -= 0.1
        
        # Penalize for repeated characters
        if re.search(r'(.)\1{4,}', content):
            score -= 0.3
        
        return max(0.0, min(1.0, score))


class ChatManager:
    """Chat room management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_chat_rooms(self, user_id: str) -> List[Dict[str, Any]]:
        """Get chat rooms for a user"""
        try:
            memberships = self.db.query(models.ChatMembership).filter(
                models.ChatMembership.user_id == user_id
            ).all()
            
            rooms = []
            for membership in memberships:
                room = self.db.query(models.ChatRoom).filter(
                    models.ChatRoom.id == membership.room_id
                ).first()
                
                if room:
                    rooms.append({
                        "room_id": room.id,
                        "name": room.name,
                        "description": room.description,
                        "role": membership.role,
                        "member_count": room.member_count,
                        "is_public": room.is_public,
                        "joined_at": membership.joined_at.isoformat()
                    })
            
            return rooms
            
        except Exception as e:
            logger.error(f"Error getting user chat rooms: {e}")
            return []
    
    def get_room_messages(self, room_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get messages for a chat room"""
        try:
            messages = self.db.query(models.ChatMessage).filter(
                models.ChatMessage.room_id == room_id
            ).order_by(desc(models.ChatMessage.created_at)).offset(offset).limit(limit).all()
            
            formatted_messages = []
            for message in messages:
                user = self.db.query(models.User).filter(models.User.id == message.user_id).first()
                
                formatted_messages.append({
                    "id": message.id,
                    "content": message.content,
                    "message_type": message.message_type,
                    "user_id": message.user_id,
                    "username": user.username if user else "Unknown",
                    "created_at": message.created_at.isoformat()
                })
            
            return formatted_messages
            
        except Exception as e:
            logger.error(f"Error getting room messages: {e}")
            return []
