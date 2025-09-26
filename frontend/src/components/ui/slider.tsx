import React from 'react';
import { cn } from '../../utils/cn';

interface SliderProps {
    value?: number[];
    onValueChange?: (value: number[]) => void;
    min?: number;
    max?: number;
    step?: number;
    className?: string;
    disabled?: boolean;
}

export const Slider: React.FC<SliderProps> = ({
    value = [0],
    onValueChange,
    min = 0,
    max = 100,
    step = 1,
    className,
    disabled = false,
}) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newValue = parseFloat(e.target.value);
        onValueChange?.([newValue]);
    };

    return (
        <div className={cn('relative', className)}>
            <input
                type="range"
                min={min}
                max={max}
                step={step}
                value={value[0]}
                onChange={handleChange}
                disabled={disabled}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                style={{
                    background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${((value[0] - min) / (max - min)) * 100}%, #e5e7eb ${((value[0] - min) / (max - min)) * 100}%, #e5e7eb 100%)`
                }}
            />
        </div>
    );
};
