import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { UserProvider, useUser } from './contexts/UserContext';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Trading } from './pages/Trading';
import { Portfolio } from './pages/Portfolio';
import { Analytics } from './pages/Analytics';
import { AIAssistant } from './pages/AIAssistant';
import { MarketData } from './pages/MarketData';
import { Bank } from './pages/Bank';
import { AIPredictions } from './pages/AIPredictions';
import MarketScreener from './pages/MarketScreener';
import { BacktestingDashboard } from './components/backtesting/BacktestingDashboard';
import { OptionsTradingInterface } from './components/options/OptionsTradingInterface';
import { CryptoTradingInterface } from './components/crypto/CryptoTradingInterface';
import { Competition } from './pages/Competition';
import { ErrorBoundary } from './components/ErrorBoundary';
import TradingEducation from './pages/Education/TradingEducation';
import DataVisualization from './pages/DataVisualization';
import './styles/themes.css';

// Global error handler
window.addEventListener('error', (event) => {
    console.error('🚨 GLOBAL ERROR CAUGHT:', event.error);
    if (event.error && event.error.message && event.error.message.includes('Objects are not valid as a React child')) {
        console.error('🚨 OBJECT RENDERING ERROR DETECTED:', {
            error: event.error.message,
            stack: event.error.stack,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno
        });
    }
});

// Global unhandled promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
    console.error('🚨 UNHANDLED PROMISE REJECTION:', event.reason);
});

// Wrapper components that get userId from context
const BacktestingWrapper: React.FC = () => {
    const { user } = useUser();
    return <BacktestingDashboard userId={user?.id || 'demo-user'} />;
};

const OptionsWrapper: React.FC = () => {
    const { user } = useUser();
    return <OptionsTradingInterface userId={user?.id || 'demo-user'} />;
};

const CryptoWrapper: React.FC = () => {
    const { user } = useUser();
    return <CryptoTradingInterface userId={user?.id || 'demo-user'} />;
};

// Component that provides user ID to child components
const AppRoutes: React.FC = () => {
    return (
        <Layout>
            <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/trading" element={
                    <ErrorBoundary>
                        <Trading />
                    </ErrorBoundary>
                } />
                <Route path="/portfolio" element={<Portfolio />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/ai" element={<AIAssistant />} />
                <Route path="/market" element={<MarketData />} />
                <Route path="/screener" element={<MarketScreener />} />
                <Route path="/bank" element={<Bank />} />
                <Route path="/predictions" element={<AIPredictions />} />
                <Route path="/backtesting" element={<BacktestingWrapper />} />
                <Route path="/options" element={<OptionsWrapper />} />
                <Route path="/crypto" element={<CryptoWrapper />} />
                <Route path="/competition" element={<Competition />} />
                <Route path="/education" element={<TradingEducation />} />
                <Route path="/visualization" element={<DataVisualization />} />
            </Routes>
        </Layout>
    );
};

function App() {
    return (
        <UserProvider>
            <ThemeProvider>
                <ErrorBoundary>
                    <AppRoutes />
                </ErrorBoundary>
            </ThemeProvider>
        </UserProvider>
    );
}

export default App;
