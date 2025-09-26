import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> { }

export const Card: React.FC<CardProps> = ({ className = '', children, ...props }) => (
    <div
        className={`rounded-lg border border-gray-200 bg-white shadow-sm ${className}`.trim()}
        {...props}
    >
        {children}
    </div>
);

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className = '', children, ...props }) => (
    <div className={`border-b border-gray-200 px-4 py-3 ${className}`.trim()} {...props}>
        {children}
    </div>
);

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({ className = '', children, ...props }) => (
    <h3 className={`text-lg font-semibold leading-6 text-gray-900 ${className}`.trim()} {...props}>
        {children}
    </h3>
);

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className = '', children, ...props }) => (
    <div className={`px-4 py-3 ${className}`.trim()} {...props}>
        {children}
    </div>
);
