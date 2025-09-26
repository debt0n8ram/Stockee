import React from 'react';
import { cn } from '../../utils/cn';

interface SwitchProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
    checked?: boolean;
    onCheckedChange?: (checked: boolean) => void;
    disabled?: boolean;
    className?: string;
}

export const Switch: React.FC<SwitchProps> = ({
    checked = false,
    onCheckedChange,
    disabled = false,
    className,
    ...props
}) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        onCheckedChange?.(e.target.checked);
    };

    return (
        <label className={cn('relative inline-flex items-center cursor-pointer', className)}>
            <input
                type="checkbox"
                checked={checked}
                onChange={handleChange}
                disabled={disabled}
                className="sr-only"
                {...props}
            />
            <div
                className={cn(
                    'relative w-11 h-6 bg-gray-200 rounded-full transition-colors duration-200 ease-in-out',
                    checked && 'bg-blue-600',
                    disabled && 'opacity-50 cursor-not-allowed'
                )}
            >
                <div
                    className={cn(
                        'absolute top-0.5 left-0.5 bg-white border border-gray-300 rounded-full h-5 w-5 transition-transform duration-200 ease-in-out',
                        checked && 'transform translate-x-5'
                    )}
                />
            </div>
        </label>
    );
};
