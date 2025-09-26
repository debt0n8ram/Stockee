import React from 'react';

// Safe render wrapper to catch object rendering errors
export const SafeRender: React.FC<{ children: any }> = ({ children }) => {
    // Check if children is an object that shouldn't be rendered directly
    if (children && typeof children === 'object' && !React.isValidElement(children)) {
        console.error('🚨 ATTEMPTED TO RENDER OBJECT DIRECTLY:', children);
        console.trace('Object rendering trace');

        // Convert object to string representation
        return <span style={{ color: 'red', fontFamily: 'monospace' }}>
            [Object: {JSON.stringify(children)}]
        </span>;
    }

    return children;
};

// Hook to safely render any value
export const useSafeRender = (value: any) => {
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
