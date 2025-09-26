import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { Textarea } from '../ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import {
  Heart,
  MessageCircle,
  Share2,
  TrendingUp,
  TrendingDown,
  Star,
  Filter,
  Search,
  Plus,
  Users,
  Trophy,
  Target,
  BarChart3,
  Clock,
  MoreHorizontal
} from 'lucide-react';
// Simple date formatting function to avoid date-fns dependency
const formatDate = (date: Date, format?: string) => {
  if (format === 'HH:mm:ss') {
    return date.toLocaleTimeString();
  } else if (format === 'MMM dd, HH:mm') {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) + ', ' + date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  } else if (format === 'MMM dd, yyyy HH:mm:ss') {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) + ' ' + date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  } else if (format === 'HH:mm') {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  } else if (format === 'MMM dd, yyyy') {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
};

interface SocialPost {
  id: string;
  user: {
    id: string;
    username: string;
    displayName: string;
    avatar: string;
    verified: boolean;
    followers: number;
    following: number;
    totalReturn: number;
    winRate: number;
    rank: number;
  };
  content: string;
  type: 'trade' | 'analysis' | 'news' | 'general';
  symbols: string[];
  images?: string[];
  likes: number;
  comments: number;
  shares: number;
  isLiked: boolean;
  isBookmarked: boolean;
  timestamp: string;
  tags: string[];
  trade?: {
    symbol: string;
    action: 'buy' | 'sell';
    quantity: number;
    price: number;
    pnl?: number;
    pnlPercent?: number;
  };
  analysis?: {
    title: string;
    summary: string;
    target: number;
    stopLoss: number;
    confidence: number;
  };
}

interface LeaderboardUser {
  id: string;
  username: string;
  displayName: string;
  avatar: string;
  rank: number;
  totalReturn: number;
  winRate: number;
  followers: number;
  verified: boolean;
}

interface SocialTradingFeedProps {
  className?: string;
}

export const SocialTradingFeed: React.FC<SocialTradingFeedProps> = ({ className = '' }) => {
  const [posts, setPosts] = useState<SocialPost[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardUser[]>([]);
  const [newPost, setNewPost] = useState('');
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>([]);
  const [postType, setPostType] = useState<'general' | 'trade' | 'analysis'>('general');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('feed');
  const [filter, setFilter] = useState<'all' | 'trades' | 'analysis' | 'following'>('all');

  // Load social feed data
  useEffect(() => {
    loadSocialFeed();
    loadLeaderboard();
  }, [filter]);

  const loadSocialFeed = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`/api/social/feed?filter=${filter}&limit=20`);
      const data = await response.json();
      setPosts(data.data || []);
    } catch (error) {
      console.error('Error loading social feed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadLeaderboard = async () => {
    try {
      const response = await fetch('/api/social/leaderboard?limit=10');
      const data = await response.json();
      setLeaderboard(data.data || []);
    } catch (error) {
      console.error('Error loading leaderboard:', error);
    }
  };

  const createPost = async () => {
    if (!newPost.trim()) return;

    try {
      const response = await fetch('/api/social/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: newPost,
          type: postType,
          symbols: selectedSymbols,
          tags: extractTags(newPost)
        })
      });

      if (response.ok) {
        setNewPost('');
        setSelectedSymbols([]);
        loadSocialFeed();
      }
    } catch (error) {
      console.error('Error creating post:', error);
    }
  };

  const likePost = async (postId: string) => {
    try {
      const response = await fetch(`/api/social/posts/${postId}/like`, {
        method: 'POST'
      });

      if (response.ok) {
        setPosts(prev => prev.map(post =>
          post.id === postId
            ? {
              ...post,
              isLiked: !post.isLiked,
              likes: post.isLiked ? post.likes - 1 : post.likes + 1
            }
            : post
        ));
      }
    } catch (error) {
      console.error('Error liking post:', error);
    }
  };

  const followUser = async (userId: string) => {
    try {
      const response = await fetch(`/api/social/users/${userId}/follow`, {
        method: 'POST'
      });

      if (response.ok) {
        loadSocialFeed();
      }
    } catch (error) {
      console.error('Error following user:', error);
    }
  };

  const extractTags = (text: string): string[] => {
    const tagRegex = /#(\w+)/g;
    const matches = text.match(tagRegex);
    return matches ? matches.map(tag => tag.substring(1)) : [];
  };

  const extractSymbols = (text: string): string[] => {
    const symbolRegex = /\$([A-Z]{1,5})/g;
    const matches = text.match(symbolRegex);
    return matches ? matches.map(symbol => symbol.substring(1)) : [];
  };

  const getPostTypeIcon = (type: string) => {
    switch (type) {
      case 'trade': return <TrendingUp className="h-4 w-4" />;
      case 'analysis': return <BarChart3 className="h-4 w-4" />;
      case 'news': return <Target className="h-4 w-4" />;
      default: return <MessageCircle className="h-4 w-4" />;
    }
  };

  const getPostTypeColor = (type: string) => {
    switch (type) {
      case 'trade': return 'bg-green-100 text-green-800';
      case 'analysis': return 'bg-blue-100 text-blue-800';
      case 'news': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Social Trading</h2>
          <p className="text-muted-foreground">
            Connect with traders, share insights, and learn from the community
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Search className="h-4 w-4 mr-2" />
            Search
          </Button>
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="feed">Feed</TabsTrigger>
          <TabsTrigger value="leaderboard">Leaderboard</TabsTrigger>
          <TabsTrigger value="discover">Discover</TabsTrigger>
        </TabsList>

        <TabsContent value="feed" className="space-y-4">
          {/* Create Post */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Plus className="h-5 w-5" />
                <span>Share Your Thoughts</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex space-x-2">
                  <Button
                    variant={postType === 'general' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setPostType('general')}
                  >
                    General
                  </Button>
                  <Button
                    variant={postType === 'trade' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setPostType('trade')}
                  >
                    Trade
                  </Button>
                  <Button
                    variant={postType === 'analysis' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setPostType('analysis')}
                  >
                    Analysis
                  </Button>
                </div>

                <Textarea
                  value={newPost}
                  onChange={(e) => {
                    setNewPost(e.target.value);
                    setSelectedSymbols(extractSymbols(e.target.value));
                  }}
                  placeholder="Share your trading insights, analysis, or market thoughts..."
                  className="min-h-[100px]"
                />

                {selectedSymbols.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {selectedSymbols.map((symbol) => (
                      <Badge key={symbol} variant="outline">
                        ${symbol}
                      </Badge>
                    ))}
                  </div>
                )}

                <div className="flex justify-between items-center">
                  <div className="text-sm text-muted-foreground">
                    {newPost.length}/500 characters
                  </div>
                  <Button onClick={createPost} disabled={!newPost.trim()}>
                    Post
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Feed Filter */}
          <div className="flex space-x-2">
            <Button
              variant={filter === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('all')}
            >
              All
            </Button>
            <Button
              variant={filter === 'trades' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('trades')}
            >
              Trades
            </Button>
            <Button
              variant={filter === 'analysis' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('analysis')}
            >
              Analysis
            </Button>
            <Button
              variant={filter === 'following' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('following')}
            >
              Following
            </Button>
          </div>

          {/* Posts Feed */}
          <div className="space-y-4">
            {posts.map((post) => (
              <Card key={post.id}>
                <CardContent className="p-4">
                  <div className="flex items-start space-x-3">
                    <Avatar className="h-10 w-10">
                      <AvatarImage src={post.user.avatar} />
                      <AvatarFallback>{post.user.username[0].toUpperCase()}</AvatarFallback>
                    </Avatar>

                    <div className="flex-1 space-y-3">
                      {/* User Info */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div>
                            <div className="flex items-center space-x-1">
                              <span className="font-medium">{post.user.displayName}</span>
                              {post.user.verified && (
                                <Badge variant="outline" className="text-xs">
                                  <Star className="h-3 w-3 mr-1" />
                                  Verified
                                </Badge>
                              )}
                              <span className="text-sm text-muted-foreground">
                                @{post.user.username}
                              </span>
                            </div>
                            <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                              <span>{post.user.followers.toLocaleString()} followers</span>
                              <span>•</span>
                              <span>{post.user.totalReturn.toFixed(1)}% return</span>
                              <span>•</span>
                              <span>{post.user.winRate.toFixed(1)}% win rate</span>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center space-x-2">
                          <Badge className={getPostTypeColor(post.type)}>
                            {getPostTypeIcon(post.type)}
                            <span className="ml-1 capitalize">{post.type}</span>
                          </Badge>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>

                      {/* Post Content */}
                      <div className="space-y-3">
                        <p className="text-sm whitespace-pre-wrap">{post.content}</p>

                        {/* Trade Details */}
                        {post.trade && (
                          <div className="bg-muted p-3 rounded-lg">
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="font-medium">
                                  {post.trade.action.toUpperCase()} {post.trade.quantity} shares of {post.trade.symbol}
                                </p>
                                <p className="text-sm text-muted-foreground">
                                  Entry: ${post.trade.price.toFixed(2)}
                                </p>
                              </div>
                              {post.trade.pnl && (
                                <div className={`text-right ${post.trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                  <p className="font-medium">
                                    {post.trade.pnl >= 0 ? '+' : ''}${post.trade.pnl.toFixed(2)}
                                  </p>
                                  <p className="text-sm">
                                    {post.trade.pnlPercent >= 0 ? '+' : ''}{post.trade.pnlPercent.toFixed(2)}%
                                  </p>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Analysis Details */}
                        {post.analysis && (
                          <div className="bg-muted p-3 rounded-lg">
                            <h4 className="font-medium mb-2">{post.analysis.title}</h4>
                            <p className="text-sm text-muted-foreground mb-2">{post.analysis.summary}</p>
                            <div className="grid grid-cols-3 gap-4 text-sm">
                              <div>
                                <p className="text-muted-foreground">Target</p>
                                <p className="font-medium">${post.analysis.target.toFixed(2)}</p>
                              </div>
                              <div>
                                <p className="text-muted-foreground">Stop Loss</p>
                                <p className="font-medium">${post.analysis.stopLoss.toFixed(2)}</p>
                              </div>
                              <div>
                                <p className="text-muted-foreground">Confidence</p>
                                <p className="font-medium">{post.analysis.confidence}%</p>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Symbols */}
                        {post.symbols.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {post.symbols.map((symbol) => (
                              <Badge key={symbol} variant="outline">
                                ${symbol}
                              </Badge>
                            ))}
                          </div>
                        )}

                        {/* Tags */}
                        {post.tags.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {post.tags.map((tag) => (
                              <Badge key={tag} variant="secondary">
                                #{tag}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Post Actions */}
                      <div className="flex items-center justify-between pt-2 border-t">
                        <div className="flex items-center space-x-4">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => likePost(post.id)}
                            className={post.isLiked ? 'text-red-600' : ''}
                          >
                            <Heart className={`h-4 w-4 mr-1 ${post.isLiked ? 'fill-current' : ''}`} />
                            {post.likes}
                          </Button>
                          <Button variant="ghost" size="sm">
                            <MessageCircle className="h-4 w-4 mr-1" />
                            {post.comments}
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Share2 className="h-4 w-4 mr-1" />
                            {post.shares}
                          </Button>
                        </div>

                        <div className="flex items-center space-x-2">
                          <span className="text-xs text-muted-foreground">
                            {formatDate(new Date(post.timestamp), 'MMM dd, HH:mm')}
                          </span>
                          <Button variant="ghost" size="sm">
                            <Clock className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="leaderboard" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Trophy className="h-5 w-5" />
                <span>Top Traders</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {leaderboard.map((user, index) => (
                  <div key={user.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground text-sm font-bold">
                        {user.rank}
                      </div>
                      <Avatar className="h-10 w-10">
                        <AvatarImage src={user.avatar} />
                        <AvatarFallback>{user.username[0].toUpperCase()}</AvatarFallback>
                      </Avatar>
                      <div>
                        <div className="flex items-center space-x-1">
                          <span className="font-medium">{user.displayName}</span>
                          {user.verified && (
                            <Star className="h-4 w-4 text-yellow-500" />
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">@{user.username}</p>
                      </div>
                    </div>

                    <div className="text-right">
                      <p className="font-medium text-green-600">
                        +{user.totalReturn.toFixed(1)}%
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {user.winRate.toFixed(1)}% win rate
                      </p>
                    </div>

                    <div className="text-right">
                      <p className="text-sm text-muted-foreground">
                        {user.followers.toLocaleString()} followers
                      </p>
                      <Button variant="outline" size="sm">
                        Follow
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="discover" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Trending Symbols */}
            <Card>
              <CardHeader>
                <CardTitle>Trending Symbols</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL'].map((symbol) => (
                    <div key={symbol} className="flex items-center justify-between">
                      <span className="font-medium">${symbol}</span>
                      <Badge variant="outline">+5.2%</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Popular Tags */}
            <Card>
              <CardHeader>
                <CardTitle>Popular Tags</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {['#trading', '#analysis', '#stocks', '#crypto', '#earnings', '#news'].map((tag) => (
                    <Badge key={tag} variant="secondary" className="cursor-pointer">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Suggested Users */}
            <Card>
              <CardHeader>
                <CardTitle>Suggested Users</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {leaderboard.slice(0, 3).map((user) => (
                    <div key={user.id} className="flex items-center space-x-3">
                      <Avatar className="h-8 w-8">
                        <AvatarImage src={user.avatar} />
                        <AvatarFallback>{user.username[0].toUpperCase()}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <p className="text-sm font-medium">{user.displayName}</p>
                        <p className="text-xs text-muted-foreground">
                          +{user.totalReturn.toFixed(1)}% return
                        </p>
                      </div>
                      <Button variant="outline" size="sm">
                        Follow
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};
