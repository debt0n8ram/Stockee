import React from 'react';

interface SelectProps {
    value?: string;
    onValueChange?: (value: string) => void;
    children: React.ReactNode;
}

export const Select: React.FC<SelectProps> = ({ value, onValueChange, children }) => {
    const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        onValueChange?.(event.target.value);
    };

    return (
        <select
            value={value}
            onChange={handleChange}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm transition focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
            {children}
        </select>
    );
};

export const SelectTrigger: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className }) => <>{children}</>;
export const SelectValue: React.FC<{ placeholder?: string }> = ({ placeholder }) => <option value="">{placeholder || 'Select an option'}</option>;
export const SelectContent: React.FC<{ children: React.ReactNode }> = ({ children }) => <>{children}</>;
export const SelectItem: React.FC<{ value: string; children: React.ReactNode }> = ({ value, children }) => (
    <option value={value}>{children}</option>
);
