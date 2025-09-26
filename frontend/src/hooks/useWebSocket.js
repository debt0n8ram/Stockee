import { useState, useEffect, useRef, useCallback } from 'react';

export const useWebSocket = (url, options = {}) => {
    const [socket, setSocket] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState(null);
    const [lastMessage, setLastMessage] = useState(null);
    const [connectionStats, setConnectionStats] = useState(null);

    const reconnectTimeoutRef = useRef(null);
    const reconnectAttemptsRef = useRef(0);
    const maxReconnectAttempts = options.maxReconnectAttempts || 5;
    const reconnectInterval = options.reconnectInterval || 3000;

    const messageHandlers = useRef(new Map());
    const subscriptions = useRef(new Set());

    const connect = useCallback(() => {
        try {
            const ws = new WebSocket(url);

            ws.onopen = () => {
                console.log('WebSocket connected');
                setIsConnected(true);
                setError(null);
                reconnectAttemptsRef.current = 0;

                // Re-subscribe to previous subscriptions
                subscriptions.current.forEach(subscription => {
                    ws.send(JSON.stringify(subscription));
                });
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    // Debug: Check for problematic data structure
                    if (data && typeof data === 'object' &&
                        'symbol' in data && 'price' in data && 'timestamp' in data && 'source' in data) {
                        console.warn('🚨 PROBLEMATIC WEBSOCKET DATA DETECTED IN useWebSocket:', {
                            data,
                            url,
                            timestamp: new Date().toISOString()
                        });
                        console.trace('WebSocket data origin trace');
                    }

                    setLastMessage(data);

                    // Handle specific message types
                    if (data.type && messageHandlers.current.has(data.type)) {
                        const handler = messageHandlers.current.get(data.type);
                        handler(data);
                    }

                    // Handle connection stats
                    if (data.type === 'connection_established') {
                        setConnectionStats({
                            user_id: data.user_id,
                            timestamp: data.timestamp
                        });
                    }
                } catch (err) {
                    console.error('Error parsing WebSocket message:', err);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                setError('WebSocket connection error');
            };

            ws.onclose = (event) => {
                console.log('WebSocket disconnected:', event.code, event.reason);
                setIsConnected(false);
                setSocket(null);

                // Attempt to reconnect if not a normal closure
                if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
                    reconnectAttemptsRef.current++;
                    console.log(`Attempting to reconnect (${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`);

                    reconnectTimeoutRef.current = setTimeout(() => {
                        connect();
                    }, reconnectInterval);
                }
            };

            setSocket(ws);
        } catch (err) {
            console.error('Error creating WebSocket connection:', err);
            setError('Failed to create WebSocket connection');
        }
    }, [url, maxReconnectAttempts, reconnectInterval]);

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }

        if (socket) {
            socket.close(1000, 'User disconnected');
        }

        setIsConnected(false);
        setSocket(null);
        setError(null);
    }, [socket]);

    const sendMessage = useCallback((message) => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify(message));
            return true;
        } else {
            console.warn('WebSocket is not connected');
            return false;
        }
    }, [socket]);

    const subscribe = useCallback((type, data = {}) => {
        const subscription = { type, ...data };
        subscriptions.current.add(subscription);

        if (isConnected) {
            sendMessage(subscription);
        }
    }, [isConnected, sendMessage]);

    const unsubscribe = useCallback((type, data = {}) => {
        const subscription = { type, ...data };
        subscriptions.current.delete(subscription);

        if (isConnected) {
            sendMessage(subscription);
        }
    }, [isConnected, sendMessage]);

    const addMessageHandler = useCallback((type, handler) => {
        messageHandlers.current.set(type, handler);
    }, []);

    const removeMessageHandler = useCallback((type) => {
        messageHandlers.current.delete(type);
    }, []);

    // Price subscription helpers
    const subscribeToPrice = useCallback((symbol) => {
        subscribe('subscribe_price', { symbol });
    }, [subscribe]);

    const unsubscribeFromPrice = useCallback((symbol) => {
        unsubscribe('unsubscribe_price', { symbol });
    }, [unsubscribe]);

    // Portfolio subscription helpers
    const subscribeToPortfolio = useCallback(() => {
        subscribe('subscribe_portfolio');
    }, [subscribe]);

    const unsubscribeFromPortfolio = useCallback(() => {
        unsubscribe('unsubscribe_portfolio');
    }, [unsubscribe]);

    // Alerts subscription helpers
    const subscribeToAlerts = useCallback(() => {
        subscribe('subscribe_alerts');
    }, [subscribe]);

    const unsubscribeFromAlerts = useCallback(() => {
        unsubscribe('unsubscribe_alerts');
    }, [unsubscribe]);

    // Market status subscription helpers
    const subscribeToMarketStatus = useCallback(() => {
        subscribe('subscribe_market_status');
    }, [subscribe]);

    const unsubscribeFromMarketStatus = useCallback(() => {
        unsubscribe('unsubscribe_market_status');
    }, [unsubscribe]);

    // Ping/pong for connection health
    const ping = useCallback(() => {
        sendMessage({ type: 'ping' });
    }, [sendMessage]);

    // Initialize connection
    useEffect(() => {
        if (options.autoConnect !== false) {
            connect();
        }

        return () => {
            disconnect();
        };
    }, [connect, disconnect, options.autoConnect]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
        };
    }, []);

    return {
        socket,
        isConnected,
        error,
        lastMessage,
        connectionStats,
        connect,
        disconnect,
        sendMessage,
        subscribe,
        unsubscribe,
        addMessageHandler,
        removeMessageHandler,
        subscribeToPrice,
        unsubscribeFromPrice,
        subscribeToPortfolio,
        unsubscribeFromPortfolio,
        subscribeToAlerts,
        unsubscribeFromAlerts,
        subscribeToMarketStatus,
        unsubscribeFromMarketStatus,
        ping
    };
};

export default useWebSocket;
