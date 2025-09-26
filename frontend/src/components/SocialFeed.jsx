import React, { useState, useEffect } from 'react';
import useSocialFeatures from '../hooks/useSocialFeatures';
import { formatCurrency, formatPercentage } from '../utils/formatters';

const SocialFeed = ({ className = '' }) => {
    const {
        feed,
        trendingPosts,
        trendingSymbols,
        isLoading,
        error,
        createPost,
        likePost,
        commentOnPost,
        followUser,
        getFeed,
        getTrendingPosts,
        getTrendingSymbols
    } = useSocialFeatures();

    const [activeTab, setActiveTab] = useState('feed');
    const [newPost, setNewPost] = useState({
        content: '',
        postType: 'general',
        symbol: '',
        tags: []
    });
    const [newComment, setNewComment] = useState('');
    const [commentingOn, setCommentingOn] = useState(null);

    const handleCreatePost = async () => {
        try {
            await createPost(
                newPost.content,
                newPost.postType,
                newPost.symbol || null,
                newPost.tags
            );
            setNewPost({
                content: '',
                postType: 'general',
                symbol: '',
                tags: []
            });
        } catch (err) {
            console.error('Failed to create post:', err);
        }
    };

    const handleLikePost = async (postId) => {
        try {
            await likePost(postId);
        } catch (err) {
            console.error('Failed to like post:', err);
        }
    };

    const handleCommentOnPost = async (postId) => {
        try {
            await commentOnPost(postId, newComment);
            setNewComment('');
            setCommentingOn(null);
        } catch (err) {
            console.error('Failed to comment on post:', err);
        }
    };

    const handleFollowUser = async (userId) => {
        try {
            await followUser(userId);
        } catch (err) {
            console.error('Failed to follow user:', err);
        }
    };

    const renderFeed = () => (
        <div className="space-y-6">
            {/* Create Post Form */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Create New Post</h4>
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Content
                        </label>
                        <textarea
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            rows="3"
                            value={newPost.content}
                            onChange={(e) => setNewPost(prev => ({ ...prev, content: e.target.value }))}
                            placeholder="What's on your mind?"
                        />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Post Type
                            </label>
                            <select
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                value={newPost.postType}
                                onChange={(e) => setNewPost(prev => ({ ...prev, postType: e.target.value }))}
                            >
                                <option value="general">General</option>
                                <option value="trade">Trade</option>
                                <option value="analysis">Analysis</option>
                                <option value="news">News</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Symbol (optional)
                            </label>
                            <input
                                type="text"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                value={newPost.symbol}
                                onChange={(e) => setNewPost(prev => ({ ...prev, symbol: e.target.value }))}
                                placeholder="e.g., AAPL"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Tags (comma-separated)
                            </label>
                            <input
                                type="text"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                value={newPost.tags.join(', ')}
                                onChange={(e) => setNewPost(prev => ({
                                    ...prev,
                                    tags: e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag)
                                }))}
                                placeholder="e.g., trading, analysis"
                            />
                        </div>
                    </div>

                    <button
                        onClick={handleCreatePost}
                        disabled={isLoading || !newPost.content.trim()}
                        className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                        {isLoading ? 'Posting...' : 'Post'}
                    </button>
                </div>
            </div>

            {/* Feed Posts */}
            <div className="space-y-4">
                {feed.map(post => (
                    <div key={post.id} className="bg-white p-6 rounded-lg shadow-sm border">
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center">
                                <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                                    <span className="text-sm font-medium text-gray-700">
                                        {post.username.charAt(0).toUpperCase()}
                                    </span>
                                </div>
                                <div className="ml-3">
                                    <h5 className="font-medium text-gray-900">{post.username}</h5>
                                    <p className="text-sm text-gray-600">
                                        {new Date(post.created_at).toLocaleString()}
                                    </p>
                                </div>
                            </div>

                            {post.symbol && (
                                <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                                    {post.symbol}
                                </span>
                            )}
                        </div>

                        <div className="mb-4">
                            <p className="text-gray-900">{post.content}</p>
                            {post.tags.length > 0 && (
                                <div className="mt-2 flex flex-wrap gap-1">
                                    {post.tags.map(tag => (
                                        <span key={tag} className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
                                            #{tag}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4">
                                <button
                                    onClick={() => handleLikePost(post.id)}
                                    className={`flex items-center space-x-1 ${post.user_liked ? 'text-red-600' : 'text-gray-600 hover:text-red-600'
                                        }`}
                                >
                                    <svg className="w-5 h-5" fill={post.user_liked ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                                    </svg>
                                    <span className="text-sm">{post.likes_count}</span>
                                </button>

                                <button
                                    onClick={() => setCommentingOn(commentingOn === post.id ? null : post.id)}
                                    className="flex items-center space-x-1 text-gray-600 hover:text-blue-600"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                                    </svg>
                                    <span className="text-sm">{post.comments_count}</span>
                                </button>

                                <button className="flex items-center space-x-1 text-gray-600 hover:text-green-600">
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                                    </svg>
                                    <span className="text-sm">{post.shares_count}</span>
                                </button>
                            </div>

                            <button
                                onClick={() => handleFollowUser(post.user_id)}
                                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                            >
                                Follow
                            </button>
                        </div>

                        {/* Comments Section */}
                        {commentingOn === post.id && (
                            <div className="mt-4 pt-4 border-t border-gray-200">
                                <div className="space-y-3">
                                    {post.comments.map(comment => (
                                        <div key={comment.id} className="flex items-start space-x-3">
                                            <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                                                <span className="text-xs font-medium text-gray-700">
                                                    {comment.username.charAt(0).toUpperCase()}
                                                </span>
                                            </div>
                                            <div className="flex-1">
                                                <div className="flex items-center space-x-2">
                                                    <span className="text-sm font-medium text-gray-900">{comment.username}</span>
                                                    <span className="text-xs text-gray-600">
                                                        {new Date(comment.created_at).toLocaleString()}
                                                    </span>
                                                </div>
                                                <p className="text-sm text-gray-700 mt-1">{comment.content}</p>
                                            </div>
                                        </div>
                                    ))}

                                    <div className="flex space-x-3">
                                        <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                                            <span className="text-xs font-medium text-gray-700">Y</span>
                                        </div>
                                        <div className="flex-1">
                                            <textarea
                                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                                rows="2"
                                                value={newComment}
                                                onChange={(e) => setNewComment(e.target.value)}
                                                placeholder="Write a comment..."
                                            />
                                            <div className="mt-2 flex justify-end">
                                                <button
                                                    onClick={() => handleCommentOnPost(post.id)}
                                                    disabled={!newComment.trim()}
                                                    className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
                                                >
                                                    Comment
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                ))}

                {feed.length === 0 && (
                    <div className="text-center text-gray-500 py-8">
                        No posts yet. Be the first to post!
                    </div>
                )}
            </div>
        </div>
    );

    const renderTrendingPosts = () => (
        <div className="space-y-4">
            {trendingPosts.map(post => (
                <div key={post.id} className="bg-white p-4 rounded-lg shadow-sm border">
                    <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center">
                            <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                                <span className="text-xs font-medium text-gray-700">
                                    {post.username.charAt(0).toUpperCase()}
                                </span>
                            </div>
                            <div className="ml-2">
                                <h5 className="text-sm font-medium text-gray-900">{post.username}</h5>
                                <p className="text-xs text-gray-600">
                                    {new Date(post.created_at).toLocaleString()}
                                </p>
                            </div>
                        </div>

                        <div className="text-right">
                            <div className="text-sm font-medium text-gray-900">
                                {post.engagement_score} engagement
                            </div>
                        </div>
                    </div>

                    <p className="text-sm text-gray-700 mb-2">{post.content}</p>

                    <div className="flex items-center justify-between text-xs text-gray-600">
                        <div className="flex items-center space-x-3">
                            <span>{post.likes_count} likes</span>
                            <span>{post.comments_count} comments</span>
                            <span>{post.shares_count} shares</span>
                        </div>
                        {post.symbol && (
                            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                {post.symbol}
                            </span>
                        )}
                    </div>
                </div>
            ))}

            {trendingPosts.length === 0 && (
                <div className="text-center text-gray-500 py-8">
                    No trending posts at the moment.
                </div>
            )}
        </div>
    );

    const renderTrendingSymbols = () => (
        <div className="space-y-4">
            {trendingSymbols.map(symbol => (
                <div key={symbol.symbol} className="bg-white p-4 rounded-lg shadow-sm border">
                    <div className="flex items-center justify-between">
                        <div>
                            <h5 className="font-medium text-gray-900">{symbol.symbol}</h5>
                            <p className="text-sm text-gray-600">
                                {symbol.engagement_score} engagement score
                            </p>
                        </div>

                        <div className="text-right">
                            <div className="text-sm text-gray-600">
                                {symbol.post_count} posts
                            </div>
                            <div className="text-sm text-gray-600">
                                {symbol.total_likes} likes
                            </div>
                        </div>
                    </div>
                </div>
            ))}

            {trendingSymbols.length === 0 && (
                <div className="text-center text-gray-500 py-8">
                    No trending symbols at the moment.
                </div>
            )}
        </div>
    );

    if (error) {
        return (
            <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
                <div className="flex">
                    <div className="text-red-600">
                        <strong>Error:</strong> {error}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={`space-y-6 ${className}`}>
            <div className="bg-white rounded-lg shadow-sm border">
                <div className="border-b border-gray-200">
                    <nav className="flex space-x-8 px-6">
                        {[
                            { id: 'feed', label: 'Feed' },
                            { id: 'trending_posts', label: 'Trending Posts' },
                            { id: 'trending_symbols', label: 'Trending Symbols' }
                        ].map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === tab.id
                                        ? 'border-blue-500 text-blue-600'
                                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                {tab.label}
                            </button>
                        ))}
                    </nav>
                </div>

                <div className="p-6">
                    {activeTab === 'feed' && renderFeed()}
                    {activeTab === 'trending_posts' && renderTrendingPosts()}
                    {activeTab === 'trending_symbols' && renderTrendingSymbols()}
                </div>
            </div>
        </div>
    );
};

export default SocialFeed;
