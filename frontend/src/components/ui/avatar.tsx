import React from 'react';
import { cn } from '../../utils/cn';

interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
    src?: string;
    alt?: string;
    fallback?: string;
    size?: 'sm' | 'md' | 'lg' | 'xl';
}

const sizeClasses = {
    sm: 'h-8 w-8 text-sm',
    md: 'h-10 w-10 text-base',
    lg: 'h-12 w-12 text-lg',
    xl: 'h-16 w-16 text-xl'
};

export const Avatar: React.FC<AvatarProps> = ({
    src,
    alt = '',
    fallback,
    size = 'md',
    className,
    ...props
}) => {
    const [imageError, setImageError] = React.useState(false);

    const handleImageError = () => {
        setImageError(true);
    };

    return (
        <div
            className={cn(
                'relative flex items-center justify-center rounded-full bg-gray-100 text-gray-600 font-medium',
                sizeClasses[size],
                className
            )}
            {...props}
        >
            {src && !imageError ? (
                <img
                    src={src}
                    alt={alt}
                    className="h-full w-full rounded-full object-cover"
                    onError={handleImageError}
                />
            ) : (
                <span className="text-gray-600">
                    {fallback || alt?.charAt(0)?.toUpperCase() || '?'}
                </span>
            )}
        </div>
    );
};

export const AvatarImage: React.FC<{ src?: string; alt?: string; className?: string }> = ({
    src,
    alt = '',
    className
}) => {
    const [imageError, setImageError] = React.useState(false);

    const handleImageError = () => {
        setImageError(true);
    };

    if (!src || imageError) {
        return null;
    }

    return (
        <img
            src={src}
            alt={alt}
            className={cn('h-full w-full rounded-full object-cover', className)}
            onError={handleImageError}
        />
    );
};

export const AvatarFallback: React.FC<{ children: React.ReactNode; className?: string }> = ({
    children,
    className
}) => {
    return (
        <span className={cn('text-gray-600 font-medium', className)}>
            {children}
        </span>
    );
};
