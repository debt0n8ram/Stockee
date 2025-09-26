import React from 'react';

interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> { }

export const Label: React.FC<LabelProps> = ({ className = '', children, ...props }) => (
    <label className={`block text-sm font-medium text-gray-700 ${className}`.trim()} {...props}>
        {children}
    </label>
);
