import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
    BarChart3,
    TrendingUp,
    Wallet,
    Brain,
    Search,
    Menu,
    X,
    DollarSign,
    CreditCard,
    Target,
    Filter,
    TestTube,
    Zap,
    Coins,
    Trophy,
    BookOpen,
    Eye
} from 'lucide-react';
import ThemeToggle from './ThemeToggle';
import LiveTicker from './LiveTicker';

interface LayoutProps {
    children: React.ReactNode;
}

const navigation = [
    { name: 'Dashboard', href: '/', icon: BarChart3 },
    { name: 'Trading', href: '/trading', icon: TrendingUp },
    { name: 'Portfolio', href: '/portfolio', icon: Wallet },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'AI Assistant', href: '/ai', icon: Brain },
    { name: 'Market Data', href: '/market', icon: Search },
    { name: 'Market Screener', href: '/screener', icon: Filter },
    { name: 'Data Visualization', href: '/visualization', icon: Eye },
    { name: 'Backtesting', href: '/backtesting', icon: TestTube },
    { name: 'Options Trading', href: '/options', icon: Zap },
    { name: 'Cryptocurrency', href: '/crypto', icon: Coins },
    { name: 'AI Competition', href: '/competition', icon: Trophy },
    { name: 'Trading Education', href: '/education', icon: BookOpen },
    { name: 'Bank', href: '/bank', icon: CreditCard },
    { name: 'AI Predictions', href: '/predictions', icon: Target },
];

export const Layout: React.FC<LayoutProps> = ({ children }) => {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const location = useLocation();

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Mobile sidebar */}
            <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
                <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
                <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-white shadow-xl">
                    <div className="flex h-16 items-center justify-between px-4">
                        <div className="flex items-center">
                            <DollarSign className="h-8 w-8 text-blue-600" />
                            <span className="ml-2 text-xl font-bold text-gray-900">Stockee</span>
                        </div>
                        <button
                            onClick={() => setSidebarOpen(false)}
                            className="text-gray-400 hover:text-gray-600"
                        >
                            <X className="h-6 w-6" />
                        </button>
                    </div>
                    <nav className="flex-1 px-4 py-4">
                        {navigation.map((item) => {
                            const isActive = location.pathname === item.href;
                            return (
                                <Link
                                    key={item.name}
                                    to={item.href}
                                    className={`flex items-center px-3 py-2 text-sm font-medium rounded-md mb-1 ${isActive
                                        ? 'bg-blue-100 text-blue-700'
                                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                        }`}
                                    onClick={() => setSidebarOpen(false)}
                                >
                                    <item.icon className="mr-3 h-5 w-5" />
                                    {item.name}
                                </Link>
                            );
                        })}
                    </nav>
                </div>
            </div>

            {/* Desktop sidebar */}
            <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
                <div className="flex flex-col flex-grow bg-white border-r border-gray-200">
                    <div className="flex h-16 items-center px-4">
                        <DollarSign className="h-8 w-8 text-blue-600" />
                        <span className="ml-2 text-xl font-bold text-gray-900">Stockee</span>
                    </div>
                    <nav className="flex-1 px-4 py-4">
                        {navigation.map((item) => {
                            const isActive = location.pathname === item.href;
                            return (
                                <Link
                                    key={item.name}
                                    to={item.href}
                                    className={`flex items-center px-3 py-2 text-sm font-medium rounded-md mb-1 ${isActive
                                        ? 'bg-blue-100 text-blue-700'
                                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                        }`}
                                >
                                    <item.icon className="mr-3 h-5 w-5" />
                                    {item.name}
                                </Link>
                            );
                        })}
                    </nav>
                </div>
            </div>

            {/* Main content */}
            <div className="lg:pl-64">
                {/* Top bar */}
                <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
                    <button
                        type="button"
                        className="-m-2.5 p-2.5 text-gray-700 lg:hidden"
                        onClick={() => setSidebarOpen(true)}
                    >
                        <Menu className="h-6 w-6" />
                    </button>
                    <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
                        <div className="flex flex-1"></div>
                        <div className="flex items-center gap-x-4 lg:gap-x-6">
                            <div className="text-sm font-medium text-gray-700">
                                Welcome to Stockee
                            </div>
                            <ThemeToggle />
                        </div>
                    </div>
                </div>

                {/* Page content */}
                <main className="py-6">
                    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                        <LiveTicker />
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
};
