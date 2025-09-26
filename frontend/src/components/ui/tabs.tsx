import React, { createContext, useContext, useState } from 'react';

type TabsContextValue = {
    value: string;
    setValue: (value: string) => void;
};

const TabsContext = createContext<TabsContextValue | null>(null);

interface TabsProps {
    defaultValue?: string;
    value?: string;
    onValueChange?: (value: string) => void;
    className?: string;
    children: React.ReactNode;
}

export const Tabs: React.FC<TabsProps> = ({
    defaultValue,
    value: controlledValue,
    onValueChange,
    className = '',
    children
}) => {
    const [internalValue, setInternalValue] = useState(defaultValue || '');

    const value = controlledValue !== undefined ? controlledValue : internalValue;
    const setValue = (newValue: string) => {
        if (controlledValue === undefined) {
            setInternalValue(newValue);
        }
        onValueChange?.(newValue);
    };

    return (
        <TabsContext.Provider value={{ value, setValue }}>
            <div className={className}>{children}</div>
        </TabsContext.Provider>
    );
};

export const TabsList: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className = '', children, ...props }) => (
    <div className={`inline-flex items-center rounded-md border border-gray-200 bg-white p-1 ${className}`.trim()} {...props}>
        {children}
    </div>
);

interface TabsTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    value: string;
}

export const TabsTrigger: React.FC<TabsTriggerProps> = ({ value, className = '', children, ...props }) => {
    const context = useContext(TabsContext);

    if (!context) {
        throw new Error('TabsTrigger must be used within Tabs');
    }

    const isActive = context.value === value;

    return (
        <button
            type="button"
            onClick={() => context.setValue(value)}
            className={`rounded-sm px-3 py-1 text-sm font-medium transition ${isActive ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'} ${className}`.trim()}
            {...props}
        >
            {children}
        </button>
    );
};

export const TabsContent: React.FC<{ value: string; className?: string; children: React.ReactNode }> = ({
    value,
    className = '',
    children
}) => {
    const context = useContext(TabsContext);

    if (!context) {
        throw new Error('TabsContent must be used within Tabs');
    }

    if (context.value !== value) {
        return null;
    }

    return (
        <div className={`mt-4 ${className}`.trim()}>
            {children}
        </div>
    );
};