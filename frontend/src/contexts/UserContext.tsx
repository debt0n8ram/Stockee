import React, { createContext, useContext, useState, ReactNode } from 'react';

interface User {
    id: string;
    name: string;
    email?: string;
}

interface UserContextType {
    user: User | null;
    setUser: (user: User | null) => void;
    login: (userId: string, userName?: string) => void;
    logout: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const useUser = () => {
    const context = useContext(UserContext);
    if (!context) {
        throw new Error('useUser must be used within a UserProvider');
    }
    return context;
};

interface UserProviderProps {
    children: ReactNode;
}

export const UserProvider: React.FC<UserProviderProps> = ({ children }) => {
    const [user, setUser] = useState<User | null>(() => {
        // Try to get user from localStorage on initialization
        const savedUser = localStorage.getItem('stockee_user');
        if (savedUser) {
            try {
                return JSON.parse(savedUser);
            } catch {
                return null;
            }
        }
        return null;
    });

    const login = (userId: string, userName?: string) => {
        const newUser: User = {
            id: userId,
            name: userName || `User ${userId}`,
        };
        setUser(newUser);
        localStorage.setItem('stockee_user', JSON.stringify(newUser));
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('stockee_user');
    };

    return (
        <UserContext.Provider value={{ user, setUser, login, logout }}>
            {children}
        </UserContext.Provider>
    );
};
