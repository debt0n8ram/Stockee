import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import {
    MessageSquare,
    Heart,
    Share2,
    MoreHorizontal,
    Send,
    Users,
    TrendingUp,
    Hash,
    AtSign,
    Image as ImageIcon,
    Smile,
    Plus,
    Search,
    Filter,
    Bell,
    UserPlus,
    Flag,
    ThumbsUp,
    MessageCircle,
    Eye,
    Clock,
    BarChart3
} from 'lucide-react';
import { apiService } from '../../services/api';

interface Post {
    id: number;
    content: string;
    post_type: string;
    symbol?: string;
    tags: string[];
    mentions: string[];
    hashtags: string[];
    images: string[];
    likes_count: number;
    comments_count: number;
    shares_count: number;
    views_count: number;
    created_at: string;
    user: {
        id: string;
        username: string;
        avatar?: string;
    };
    user_liked: boolean;
    recent_comments: Comment[];
}

interface Comment {
    id: number;
    content: string;
    user_id: string;
    created_at: string;
}

interface ChatRoom {
    room_id: number;
    name: string;
    description: string;
    role: string;
    member_count: number;
    is_public: boolean;
    joined_at: string;
}

interface ChatMessage {
    id: number;
    content: string;
    message_type: string;
    user_id: string;
    username: string;
    created_at: string;
}

export const EnhancedSocialFeed: React.FC = () => {
    const [posts, setPosts] = useState<Post[]>([]);
    const [chatRooms, setChatRooms] = useState<ChatRoom[]>([]);
    const [selectedRoom, setSelectedRoom] = useState<ChatRoom | null>(null);
    const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string>('');
    const [success, setSuccess] = useState<string>('');

    // Form states
    const [newPostContent, setNewPostContent] = useState('');
    const [newPostType, setNewPostType] = useState('general');
    const [newPostSymbol, setNewPostSymbol] = useState('');
    const [newPostTags, setNewPostTags] = useState<string[]>([]);
    const [newPostImages, setNewPostImages] = useState<string[]>([]);

    // Chat states
    const [newMessage, setNewMessage] = useState('');
    const [newRoomName, setNewRoomName] = useState('');
    const [newRoomDescription, setNewRoomDescription] = useState('');
    const [isPublicRoom, setIsPublicRoom] = useState(true);

    // Feed algorithm
    const [feedAlgorithm, setFeedAlgorithm] = useState('chronological');
    const [postTypeFilter, setPostTypeFilter] = useState<string>('');
    const [symbolFilter, setSymbolFilter] = useState<string>('');

    // WebSocket for real-time updates
    const wsRef = useRef<WebSocket | null>(null);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        loadFeed();
        loadChatRooms();
        connectWebSocket();

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [feedAlgorithm, postTypeFilter, symbolFilter]);

    const connectWebSocket = () => {
        try {
            const ws = new WebSocket(`ws://localhost:8000/api/enhanced-social/chat/rooms/1/ws?user_id=user1`);

            ws.onopen = () => {
                setIsConnected(true);
                console.log('WebSocket connected');
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            };

            ws.onclose = () => {
                setIsConnected(false);
                console.log('WebSocket disconnected');
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                setIsConnected(false);
            };

            wsRef.current = ws;
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
        }
    };

    const handleWebSocketMessage = (data: any) => {
        switch (data.type) {
            case 'chat_message':
                setChatMessages(prev => [...prev, {
                    id: data.message_id || data.id || Date.now(),
                    content: data.content || data.message || 'No message content',
                    message_type: data.message_type || 'text',
                    user_id: data.user?.id || data.user_id || 'unknown',
                    username: data.user?.username || data.username || 'Unknown',
                    created_at: data.timestamp || data.created_at || new Date().toISOString()
                }]);
                break;
            case 'new_post':
                loadFeed(); // Refresh feed
                break;
            case 'user_joined':
                setSuccess(`${data.username} joined the room`);
                break;
            case 'user_typing':
                // Handle typing indicator
                break;
            default:
                console.log('Unknown WebSocket message:', data);
        }
    };

    const loadFeed = async () => {
        setIsLoading(true);
        try {
            const params = new URLSearchParams({
                algorithm: feedAlgorithm,
                limit: '50',
                offset: '0'
            });

            if (postTypeFilter) params.append('post_type', postTypeFilter);
            if (symbolFilter) params.append('symbol', symbolFilter);

            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/enhanced-social/feed?${params}`);
            const data = await response.json();
            setPosts(data.posts || []);
        } catch (err: any) {
            setError(err.message || 'Failed to load feed');
        } finally {
            setIsLoading(false);
        }
    };

    const loadChatRooms = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/enhanced-social/chat/rooms`);
            const data = await response.json();
            setChatRooms(data.rooms || []);
        } catch (err: any) {
            console.error('Failed to load chat rooms:', err);
        }
    };

    const loadChatMessages = async (roomId: number) => {
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/enhanced-social/chat/rooms/${roomId}/messages`);
            const data = await response.json();
            setChatMessages(data.messages || []);
        } catch (err: any) {
            setError('Failed to load chat messages');
        }
    };

    const handleCreatePost = async () => {
        if (!newPostContent.trim()) {
            setError('Please enter post content');
            return;
        }

        setIsLoading(true);
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/enhanced-social/posts`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: newPostContent,
                    post_type: newPostType,
                    symbol: newPostSymbol || undefined,
                    tags: newPostTags,
                    images: newPostImages
                })
            });

            const data = await response.json();
            if (response.ok && data.success) {
                setSuccess('Post created successfully!');
                setNewPostContent('');
                setNewPostSymbol('');
                setNewPostTags([]);
                setNewPostImages([]);
                loadFeed();
            } else {
                setError(data.error || 'Failed to create post');
            }
        } catch (err: any) {
            setError(err.message || 'Failed to create post');
        } finally {
            setIsLoading(false);
        }
    };

    const handleCreateChatRoom = async () => {
        if (!newRoomName.trim()) {
            setError('Please enter room name');
            return;
        }

        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/enhanced-social/chat/rooms`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: newRoomName,
                    description: newRoomDescription,
                    is_public: isPublicRoom,
                    max_members: 100
                })
            });

            const data = await response.json();
            if (response.ok && data.success) {
                setSuccess('Chat room created successfully!');
                setNewRoomName('');
                setNewRoomDescription('');
                loadChatRooms();
            } else {
                setError(data.error || 'Failed to create chat room');
            }
        } catch (err: any) {
            setError(err.message || 'Failed to create chat room');
        }
    };

    const handleSendMessage = async () => {
        if (!newMessage.trim() || !selectedRoom) {
            return;
        }

        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/enhanced-social/chat/rooms/${selectedRoom.room_id}/messages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: newMessage,
                    message_type: 'text'
                })
            });

            const data = await response.json();
            if (response.ok && data.success) {
                setNewMessage('');
                loadChatMessages(selectedRoom.room_id);
            } else {
                setError(data.error || 'Failed to send message');
            }
        } catch (err: any) {
            setError(err.message || 'Failed to send message');
        }
    };

    const handleLikePost = async (postId: number) => {
        try {
            // This would call a like/unlike endpoint
            // For now, just update local state
            setPosts(prev => prev.map(post =>
                post.id === postId
                    ? {
                        ...post,
                        user_liked: !post.user_liked,
                        likes_count: post.user_liked ? post.likes_count - 1 : post.likes_count + 1
                    }
                    : post
            ));
        } catch (err) {
            console.error('Failed to like post:', err);
        }
    };

    const handleFollowUser = async (userId: string) => {
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/enhanced-social/follow`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    following_id: userId
                })
            });

            const data = await response.json();
            if (response.ok && data.success) {
                setSuccess('Successfully followed user');
            } else {
                setError(data.error || 'Failed to follow user');
            }
        } catch (err: any) {
            setError(err.message || 'Failed to follow user');
        }
    };

    const handleReportContent = async (contentType: string, contentId: number, reason: string) => {
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/enhanced-social/report`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content_type: contentType,
                    content_id: contentId,
                    reason: reason,
                    description: ''
                })
            });

            const data = await response.json();
            if (response.ok && data.success) {
                setSuccess('Content reported successfully');
            } else {
                setError(data.error || 'Failed to report content');
            }
        } catch (err: any) {
            setError(err.message || 'Failed to report content');
        }
    };

    const formatTimeAgo = (timestamp: string) => {
        const now = new Date();
        const postTime = new Date(timestamp);
        const diffInSeconds = Math.floor((now.getTime() - postTime.getTime()) / 1000);

        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        return `${Math.floor(diffInSeconds / 86400)}d ago`;
    };

    const renderPost = (post: Post) => (
        <Card key={post.id} className="mb-4">
            <CardContent className="p-4">
                <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium">
                        {post.user.username.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                            <span className="font-medium">{post.user.username}</span>
                            {post.symbol && (
                                <Badge variant="outline" className="text-xs">
                                    {post.symbol}
                                </Badge>
                            )}
                            <span className="text-sm text-gray-500">{formatTimeAgo(post.created_at)}</span>
                            <Button variant="ghost" size="sm" className="ml-auto">
                                <MoreHorizontal className="h-4 w-4" />
                            </Button>
                        </div>

                        <div className="mb-3">
                            <p className="text-gray-800">{post.content}</p>

                            {/* Render hashtags and mentions */}
                            <div className="flex flex-wrap gap-1 mt-2">
                                {post.hashtags.map((hashtag, index) => (
                                    <Badge key={index} variant="secondary" className="text-xs">
                                        <Hash className="h-3 w-3 mr-1" />
                                        {hashtag}
                                    </Badge>
                                ))}
                                {post.mentions.map((mention, index) => (
                                    <Badge key={index} variant="outline" className="text-xs">
                                        <AtSign className="h-3 w-3 mr-1" />
                                        {mention}
                                    </Badge>
                                ))}
                            </div>

                            {/* Render images */}
                            {post.images.length > 0 && (
                                <div className="grid grid-cols-2 gap-2 mt-3">
                                    {post.images.map((image, index) => (
                                        <img
                                            key={index}
                                            src={image}
                                            alt={`Post image ${index + 1}`}
                                            className="w-full h-32 object-cover rounded"
                                        />
                                    ))}
                                </div>
                            )}
                        </div>

                        <div className="flex items-center gap-4 text-sm text-gray-500">
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleLikePost(post.id)}
                                className={post.user_liked ? "text-red-500" : ""}
                            >
                                <Heart className={`h-4 w-4 mr-1 ${post.user_liked ? "fill-current" : ""}`} />
                                {post.likes_count}
                            </Button>

                            <Button variant="ghost" size="sm">
                                <MessageCircle className="h-4 w-4 mr-1" />
                                {post.comments_count}
                            </Button>

                            <Button variant="ghost" size="sm">
                                <Share2 className="h-4 w-4 mr-1" />
                                {post.shares_count}
                            </Button>

                            <Button variant="ghost" size="sm">
                                <Eye className="h-4 w-4 mr-1" />
                                {post.views_count}
                            </Button>

                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleFollowUser(post.user.id)}
                            >
                                <UserPlus className="h-4 w-4 mr-1" />
                                Follow
                            </Button>

                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleReportContent('post', post.id, 'inappropriate')}
                            >
                                <Flag className="h-4 w-4 mr-1" />
                                Report
                            </Button>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Enhanced Social Feed</h1>
                    <p className="text-gray-600">Connect with the trading community</p>
                </div>
                <div className="flex items-center gap-2">
                    <Badge variant={isConnected ? "default" : "secondary"}>
                        {isConnected ? "Connected" : "Disconnected"}
                    </Badge>
                </div>
            </div>

            {/* Alerts */}
            {error && (
                <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            )}

            {success && (
                <Alert>
                    <AlertDescription>{success}</AlertDescription>
                </Alert>
            )}

            <Tabs defaultValue="feed" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="feed">Social Feed</TabsTrigger>
                    <TabsTrigger value="chat">Chat Rooms</TabsTrigger>
                    <TabsTrigger value="trending">Trending</TabsTrigger>
                </TabsList>

                {/* Social Feed Tab */}
                <TabsContent value="feed" className="space-y-4">
                    {/* Create Post */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <MessageSquare className="h-5 w-5" />
                                Create Post
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <Label htmlFor="post-content">What's on your mind?</Label>
                                <Input
                                    id="post-content"
                                    value={newPostContent}
                                    onChange={(e) => setNewPostContent(e.target.value)}
                                    placeholder="Share your thoughts, analysis, or market insights..."
                                    className="mt-1"
                                />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <Label htmlFor="post-type">Post Type</Label>
                                    <Select value={newPostType} onValueChange={setNewPostType}>
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="general">General</SelectItem>
                                            <SelectItem value="analysis">Analysis</SelectItem>
                                            <SelectItem value="news">News</SelectItem>
                                            <SelectItem value="question">Question</SelectItem>
                                            <SelectItem value="tip">Trading Tip</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div>
                                    <Label htmlFor="post-symbol">Symbol (Optional)</Label>
                                    <Input
                                        id="post-symbol"
                                        value={newPostSymbol}
                                        onChange={(e) => setNewPostSymbol(e.target.value.toUpperCase())}
                                        placeholder="AAPL, TSLA, etc."
                                    />
                                </div>

                                <div className="flex items-end">
                                    <Button
                                        onClick={handleCreatePost}
                                        disabled={isLoading || !newPostContent.trim()}
                                        className="w-full"
                                    >
                                        {isLoading ? "Posting..." : "Post"}
                                    </Button>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Feed Filters */}
                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center gap-4">
                                <div className="flex items-center gap-2">
                                    <Label>Algorithm:</Label>
                                    <Select value={feedAlgorithm} onValueChange={setFeedAlgorithm}>
                                        <SelectTrigger className="w-40">
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="chronological">Chronological</SelectItem>
                                            <SelectItem value="popular">Popular</SelectItem>
                                            <SelectItem value="personalized">Personalized</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="flex items-center gap-2">
                                    <Label>Type:</Label>
                                    <Select value={postTypeFilter} onValueChange={setPostTypeFilter}>
                                        <SelectTrigger className="w-32">
                                            <SelectValue placeholder="All" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="">All</SelectItem>
                                            <SelectItem value="general">General</SelectItem>
                                            <SelectItem value="analysis">Analysis</SelectItem>
                                            <SelectItem value="news">News</SelectItem>
                                            <SelectItem value="question">Question</SelectItem>
                                            <SelectItem value="tip">Trading Tip</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="flex items-center gap-2">
                                    <Label>Symbol:</Label>
                                    <Input
                                        value={symbolFilter}
                                        onChange={(e) => setSymbolFilter(e.target.value.toUpperCase())}
                                        placeholder="Filter by symbol"
                                        className="w-32"
                                    />
                                </div>

                                <Button variant="outline" onClick={loadFeed}>
                                    <Search className="h-4 w-4 mr-2" />
                                    Refresh
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Posts Feed */}
                    <div className="space-y-4">
                        {isLoading ? (
                            <div className="flex items-center justify-center py-8">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                            </div>
                        ) : posts.length === 0 ? (
                            <Card>
                                <CardContent className="p-8 text-center">
                                    <MessageSquare className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                                    <p className="text-gray-600">No posts found</p>
                                    <p className="text-sm text-gray-500">Be the first to share something!</p>
                                </CardContent>
                            </Card>
                        ) : (
                            posts.map(renderPost)
                        )}
                    </div>
                </TabsContent>

                {/* Chat Rooms Tab */}
                <TabsContent value="chat" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Chat Rooms List */}
                        <div className="space-y-4">
                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2">
                                        <Users className="h-5 w-5" />
                                        Chat Rooms
                                    </CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <Button
                                        onClick={handleCreateChatRoom}
                                        className="w-full"
                                        variant="outline"
                                    >
                                        <Plus className="h-4 w-4 mr-2" />
                                        Create Room
                                    </Button>

                                    <div className="space-y-2">
                                        {chatRooms.map((room) => (
                                            <div
                                                key={room.room_id}
                                                className={`p-3 border rounded cursor-pointer transition-colors ${selectedRoom?.room_id === room.room_id
                                                    ? 'bg-blue-50 border-blue-200'
                                                    : 'hover:bg-gray-50'
                                                    }`}
                                                onClick={() => {
                                                    setSelectedRoom(room);
                                                    loadChatMessages(room.room_id);
                                                }}
                                            >
                                                <div className="flex items-center justify-between">
                                                    <div>
                                                        <h4 className="font-medium">{room.name}</h4>
                                                        <p className="text-sm text-gray-600">{room.description}</p>
                                                    </div>
                                                    <Badge variant="outline">
                                                        {room.member_count}
                                                    </Badge>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        </div>

                        {/* Chat Messages */}
                        <div className="lg:col-span-2">
                            {selectedRoom ? (
                                <Card className="h-96 flex flex-col">
                                    <CardHeader>
                                        <CardTitle className="flex items-center gap-2">
                                            <MessageSquare className="h-5 w-5" />
                                            {selectedRoom.name}
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent className="flex-1 flex flex-col">
                                        <div className="flex-1 overflow-y-auto space-y-2 mb-4">
                                            {chatMessages.map((message) => (
                                                <div key={message.id} className="flex items-start gap-2">
                                                    <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-xs font-medium">
                                                        {message.username.charAt(0).toUpperCase()}
                                                    </div>
                                                    <div className="flex-1">
                                                        <div className="flex items-center gap-2">
                                                            <span className="font-medium text-sm">{message.username}</span>
                                                            <span className="text-xs text-gray-500">{formatTimeAgo(message.created_at)}</span>
                                                        </div>
                                                        <p className="text-sm text-gray-800">{message.content}</p>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>

                                        <div className="flex gap-2">
                                            <Input
                                                value={newMessage}
                                                onChange={(e) => setNewMessage(e.target.value)}
                                                placeholder="Type a message..."
                                                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                                            />
                                            <Button onClick={handleSendMessage}>
                                                <Send className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </CardContent>
                                </Card>
                            ) : (
                                <Card className="h-96 flex items-center justify-center">
                                    <div className="text-center">
                                        <MessageSquare className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                                        <p className="text-gray-600">Select a chat room to start messaging</p>
                                    </div>
                                </Card>
                            )}
                        </div>
                    </div>
                </TabsContent>

                {/* Trending Tab */}
                <TabsContent value="trending" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <TrendingUp className="h-5 w-5" />
                                Trending Content
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <h3 className="font-medium mb-3">Trending Symbols</h3>
                                    <div className="space-y-2">
                                        {['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL'].map((symbol, index) => (
                                            <div key={symbol} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                                                <div className="flex items-center gap-2">
                                                    <Badge variant="outline">{symbol}</Badge>
                                                    <span className="text-sm text-gray-600">{50 - index * 5} posts</span>
                                                </div>
                                                <TrendingUp className="h-4 w-4 text-green-500" />
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div>
                                    <h3 className="font-medium mb-3">Popular Hashtags</h3>
                                    <div className="space-y-2">
                                        {['#trading', '#stocks', '#crypto', '#analysis', '#tips'].map((hashtag, index) => (
                                            <div key={hashtag} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                                                <div className="flex items-center gap-2">
                                                    <Hash className="h-4 w-4 text-blue-500" />
                                                    <span className="text-sm">{hashtag}</span>
                                                </div>
                                                <span className="text-sm text-gray-600">{100 - index * 10} posts</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
};
