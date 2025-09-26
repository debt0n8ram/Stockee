// WebSocket debugging utility
export const debugWebSocketMessage = (data: any, source: string) => {
    // Check if the data matches the problematic structure
    if (data && typeof data === 'object' &&
        'symbol' in data && 'price' in data && 'timestamp' in data && 'source' in data) {
        console.warn('🚨 POTENTIAL PROBLEMATIC WEBSOCKET DATA DETECTED:', {
            data,
            source,
            keys: Object.keys(data),
            timestamp: new Date().toISOString()
        });

        // Log stack trace to see where this is being called from
        console.trace('WebSocket data origin trace');
    }
};

// Wrapper for WebSocket message handlers
export const safeWebSocketHandler = (handler: (data: any) => void, source: string) => {
    return (data: any) => {
        debugWebSocketMessage(data, source);
        try {
            handler(data);
        } catch (error) {
            console.error(`Error in WebSocket handler (${source}):`, error);
            console.error('Data that caused error:', data);
        }
    };
};

// Safe object renderer - converts objects to strings to prevent React errors
export const safeRender = (value: any): string => {
    if (value === null || value === undefined) {
        return '';
    }

    if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
        return String(value);
    }

    if (typeof value === 'object') {
        console.warn('🚨 ATTEMPTED TO RENDER OBJECT:', value);
        return JSON.stringify(value);
    }

    return String(value);
};
