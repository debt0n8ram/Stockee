import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import models

class TestSocialFeatures:
    """Test social features functionality."""
    
    def test_create_post(self, client: TestClient, test_user):
        """Test creating a new social post."""
        response = client.post(
            "/api/social-features/posts",
            json={
                "content": "Test post content",
                "post_type": "general",
                "symbol": "AAPL",
                "tags": ["test", "trading"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "post_id" in data
    
    def test_create_post_without_symbol(self, client: TestClient, test_user):
        """Test creating a post without symbol."""
        response = client.post(
            "/api/social-features/posts",
            json={
                "content": "Test post without symbol",
                "post_type": "general",
                "tags": ["test"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
    
    def test_create_post_without_tags(self, client: TestClient, test_user):
        """Test creating a post without tags."""
        response = client.post(
            "/api/social-features/posts",
            json={
                "content": "Test post without tags",
                "post_type": "general",
                "symbol": "AAPL"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
    
    def test_create_post_empty_content(self, client: TestClient, test_user):
        """Test creating a post with empty content."""
        response = client.post(
            "/api/social-features/posts",
            json={
                "content": "",
                "post_type": "general"
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_create_post_long_content(self, client: TestClient, test_user):
        """Test creating a post with very long content."""
        long_content = "x" * 10000  # Very long content
        response = client.post(
            "/api/social-features/posts",
            json={
                "content": long_content,
                "post_type": "general"
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_get_feed(self, client: TestClient, test_user, test_social_post):
        """Test getting social feed."""
        response = client.get("/api/social-features/feed")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert "total" in data
    
    def test_get_feed_with_limit(self, client: TestClient, test_user, test_social_post):
        """Test getting social feed with limit."""
        response = client.get("/api/social-features/feed?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert len(data["posts"]) <= 5
    
    def test_get_feed_with_offset(self, client: TestClient, test_user, test_social_post):
        """Test getting social feed with offset."""
        response = client.get("/api/social-features/feed?offset=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
    
    def test_get_feed_filtered_by_post_type(self, client: TestClient, test_user, test_social_post):
        """Test getting social feed filtered by post type."""
        response = client.get("/api/social-features/feed?post_type=general")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
    
    def test_get_feed_filtered_by_symbol(self, client: TestClient, test_user, test_social_post):
        """Test getting social feed filtered by symbol."""
        response = client.get("/api/social-features/feed?symbol=AAPL")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
    
    def test_like_post(self, client: TestClient, test_user, test_social_post):
        """Test liking a post."""
        response = client.post(f"/api/social-features/posts/{test_social_post.id}/like")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["action"] in ["liked", "unliked"]
    
    def test_like_nonexistent_post(self, client: TestClient, test_user):
        """Test liking a nonexistent post."""
        response = client.post("/api/social-features/posts/99999/like")
        assert response.status_code == 400
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_comment_on_post(self, client: TestClient, test_user, test_social_post):
        """Test commenting on a post."""
        response = client.post(
            f"/api/social-features/posts/{test_social_post.id}/comment",
            json={
                "content": "Test comment"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "comment_id" in data
    
    def test_comment_on_nonexistent_post(self, client: TestClient, test_user):
        """Test commenting on a nonexistent post."""
        response = client.post(
            "/api/social-features/posts/99999/comment",
            json={
                "content": "Test comment"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_comment_empty_content(self, client: TestClient, test_user, test_social_post):
        """Test commenting with empty content."""
        response = client.post(
            f"/api/social-features/posts/{test_social_post.id}/comment",
            json={
                "content": ""
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_follow_user(self, client: TestClient, test_user):
        """Test following a user."""
        response = client.post(
            "/api/social-features/follow",
            json={
                "following_id": "other_user_123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["action"] in ["followed", "unfollowed"]
    
    def test_follow_self(self, client: TestClient, test_user):
        """Test following yourself."""
        response = client.post(
            "/api/social-features/follow",
            json={
                "following_id": test_user["id"]
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "cannot follow yourself" in data["detail"].lower()
    
    def test_get_user_profile(self, client: TestClient, test_user, test_social_post):
        """Test getting user profile."""
        response = client.get(f"/api/social-features/users/{test_user['id']}/profile")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "username" in data
        assert "followers_count" in data
        assert "following_count" in data
        assert "posts_count" in data
    
    def test_get_nonexistent_user_profile(self, client: TestClient, test_user):
        """Test getting nonexistent user profile."""
        response = client.get("/api/social-features/users/nonexistent/profile")
        assert response.status_code == 400
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_get_trending_posts(self, client: TestClient, test_user, test_social_post):
        """Test getting trending posts."""
        response = client.get("/api/social-features/trending/posts")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert "time_period" in data
    
    def test_get_trending_posts_with_limit(self, client: TestClient, test_user, test_social_post):
        """Test getting trending posts with limit."""
        response = client.get("/api/social-features/trending/posts?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert len(data["posts"]) <= 5
    
    def test_get_trending_posts_with_time_period(self, client: TestClient, test_user, test_social_post):
        """Test getting trending posts with time period."""
        response = client.get("/api/social-features/trending/posts?time_period=7d")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert data["time_period"] == "7d"
    
    def test_get_trending_symbols(self, client: TestClient, test_user, test_social_post):
        """Test getting trending symbols."""
        response = client.get("/api/social-features/trending/symbols")
        assert response.status_code == 200
        data = response.json()
        assert "symbols" in data
        assert "time_period" in data
    
    def test_get_trending_symbols_with_limit(self, client: TestClient, test_user, test_social_post):
        """Test getting trending symbols with limit."""
        response = client.get("/api/social-features/trending/symbols?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "symbols" in data
        assert len(data["symbols"]) <= 10
    
    def test_search_posts(self, client: TestClient, test_user, test_social_post):
        """Test searching posts."""
        response = client.get("/api/social-features/search?query=test")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert "query" in data
    
    def test_search_posts_with_limit(self, client: TestClient, test_user, test_social_post):
        """Test searching posts with limit."""
        response = client.get("/api/social-features/search?query=test&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert len(data["posts"]) <= 5
    
    def test_search_posts_empty_query(self, client: TestClient, test_user, test_social_post):
        """Test searching posts with empty query."""
        response = client.get("/api/social-features/search?query=")
        assert response.status_code == 422  # Validation error
    
    def test_get_user_followers(self, client: TestClient, test_user, test_social_follow):
        """Test getting user followers."""
        response = client.get(f"/api/social-features/users/{test_user['id']}/followers")
        assert response.status_code == 200
        data = response.json()
        assert "followers" in data
        assert "total" in data
    
    def test_get_user_following(self, client: TestClient, test_user, test_social_follow):
        """Test getting user following."""
        response = client.get(f"/api/social-features/users/{test_user['id']}/following")
        assert response.status_code == 200
        data = response.json()
        assert "following" in data
        assert "total" in data
    
    def test_get_post_details(self, client: TestClient, test_user, test_social_post):
        """Test getting post details."""
        response = client.get(f"/api/social-features/posts/{test_social_post.id}")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "content" in data
        assert "user_id" in data
        assert "comments" in data
    
    def test_get_nonexistent_post_details(self, client: TestClient, test_user):
        """Test getting nonexistent post details."""
        response = client.get("/api/social-features/posts/99999")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_delete_post(self, client: TestClient, test_user, test_social_post):
        """Test deleting a post."""
        response = client.delete(f"/api/social-features/posts/{test_social_post.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
    
    def test_delete_nonexistent_post(self, client: TestClient, test_user):
        """Test deleting a nonexistent post."""
        response = client.delete("/api/social-features/posts/99999")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_get_user_posts(self, client: TestClient, test_user, test_social_post):
        """Test getting posts by a specific user."""
        response = client.get(f"/api/social-features/users/{test_user['id']}/posts")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert "total" in data
    
    def test_get_user_posts_with_limit(self, client: TestClient, test_user, test_social_post):
        """Test getting user posts with limit."""
        response = client.get(f"/api/social-features/users/{test_user['id']}/posts?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert len(data["posts"]) <= 5
    
    def test_get_user_posts_filtered_by_type(self, client: TestClient, test_user, test_social_post):
        """Test getting user posts filtered by type."""
        response = client.get(f"/api/social-features/users/{test_user['id']}/posts?post_type=general")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
