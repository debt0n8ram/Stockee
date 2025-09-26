import React from 'react';

type AlertVariant = 'default' | 'destructive' | 'warning' | 'success';

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: AlertVariant;
}

const variantClasses: Record<AlertVariant, string> = {
    default: 'bg-blue-50 text-blue-800 border-blue-200',
    destructive: 'bg-red-50 text-red-800 border-red-200',
    warning: 'bg-yellow-50 text-yellow-800 border-yellow-200',
    success: 'bg-green-50 text-green-800 border-green-200'
};

export const Alert: React.FC<AlertProps> = ({ variant = 'default', className = '', children, ...props }) => (
    <div className={`rounded-md border px-4 py-3 text-sm ${variantClasses[variant]} ${className}`.trim()} {...props}>
        {children}
    </div>
);

export const AlertDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({ className = '', children, ...props }) => (
    <p className={`text-sm ${className}`.trim()} {...props}>
        {children}
    </p>
);
