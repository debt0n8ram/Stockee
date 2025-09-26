import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../services/api';

export const useSocialFeatures = () => {
    const [feed, setFeed] = useState([]);
    const [trendingPosts, setTrendingPosts] = useState([]);
    const [trendingSymbols, setTrendingSymbols] = useState([]);
    const [userProfile, setUserProfile] = useState(null);
    const [followers, setFollowers] = useState([]);
    const [following, setFollowing] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const createPost = useCallback(async (content, postType = 'general', symbol = null, tags = []) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.post('/social-features/posts', {
                content,
                post_type: postType,
                symbol,
                tags
            });
            // Refresh feed
            await getFeed();
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to create post');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getFeed = useCallback(async (limit = 50, offset = 0, postType = null, symbol = null) => {
        try {
            setIsLoading(true);
            setError(null);
            const params = { limit, offset };
            if (postType) params.post_type = postType;
            if (symbol) params.symbol = symbol;

            const response = await apiClient.get('/social-features/feed', { params });
            setFeed(response.data.posts);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get feed');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const likePost = useCallback(async (postId) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.post(`/social-features/posts/${postId}/like`);
            // Refresh feed to update like count
            await getFeed();
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to like post');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, [getFeed]);

    const commentOnPost = useCallback(async (postId, content) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.post(`/social-features/posts/${postId}/comment`, {
                content
            });
            // Refresh feed to update comment count
            await getFeed();
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to comment on post');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, [getFeed]);

    const followUser = useCallback(async (followingId) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.post('/social-features/follow', {
                following_id: followingId
            });
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to follow user');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getUserProfile = useCallback(async (userId) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get(`/social-features/users/${userId}/profile`);
            setUserProfile(response.data);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get user profile');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getTrendingPosts = useCallback(async (limit = 20, timePeriod = '24h') => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get('/social-features/trending/posts', {
                params: { limit, time_period: timePeriod }
            });
            setTrendingPosts(response.data.posts);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get trending posts');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getTrendingSymbols = useCallback(async (limit = 20, timePeriod = '24h') => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get('/social-features/trending/symbols', {
                params: { limit, time_period: timePeriod }
            });
            setTrendingSymbols(response.data.symbols);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get trending symbols');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const searchPosts = useCallback(async (query, limit = 50, offset = 0) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get('/social-features/search', {
                params: { query, limit, offset }
            });
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to search posts');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getUserFollowers = useCallback(async (userId, limit = 50, offset = 0) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get(`/social-features/users/${userId}/followers`, {
                params: { limit, offset }
            });
            setFollowers(response.data.followers);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get followers');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getUserFollowing = useCallback(async (userId, limit = 50, offset = 0) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get(`/social-features/users/${userId}/following`, {
                params: { limit, offset }
            });
            setFollowing(response.data.following);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get following');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getPostDetails = useCallback(async (postId) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get(`/social-features/posts/${postId}`);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get post details');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const deletePost = useCallback(async (postId) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.delete(`/social-features/posts/${postId}`);
            // Refresh feed
            await getFeed();
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to delete post');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, [getFeed]);

    const getUserPosts = useCallback(async (userId, limit = 50, offset = 0, postType = null) => {
        try {
            setIsLoading(true);
            setError(null);
            const params = { limit, offset };
            if (postType) params.post_type = postType;

            const response = await apiClient.get(`/social-features/users/${userId}/posts`, { params });
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get user posts');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Load initial data
    useEffect(() => {
        getFeed();
        getTrendingPosts();
        getTrendingSymbols();
    }, [getFeed, getTrendingPosts, getTrendingSymbols]);

    return {
        feed,
        trendingPosts,
        trendingSymbols,
        userProfile,
        followers,
        following,
        isLoading,
        error,
        createPost,
        getFeed,
        likePost,
        commentOnPost,
        followUser,
        getUserProfile,
        getTrendingPosts,
        getTrendingSymbols,
        searchPosts,
        getUserFollowers,
        getUserFollowing,
        getPostDetails,
        deletePost,
        getUserPosts
    };
};

export default useSocialFeatures;
