import React from 'react';

interface ProgressProps {
    value: number;
    className?: string;
}

export const Progress: React.FC<ProgressProps> = ({ value, className = '' }) => {
    const progress = Math.min(100, Math.max(0, value));

    return (
        <div className={`h-2 w-full rounded-full bg-gray-200 ${className}`.trim()}>
            <div
                className="h-full rounded-full bg-blue-600"
                style={{ width: `${progress}%` }}
            />
        </div>
    );
};
