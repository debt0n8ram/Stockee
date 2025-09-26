import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import {
    TrendingUp,
    TrendingDown,
    Shield,
    Target,
    Clock,
    BarChart3,
    Info,
    AlertTriangle
} from 'lucide-react';
import { apiService } from '../../services/api';

interface AdvancedOrderFormProps {
    symbol: string;
    currentPrice: number;
    onOrderPlaced: (order: any) => void;
    onClose: () => void;
}

interface OrderType {
    type: string;
    name: string;
    description: string;
    parameters: string[];
    use_case: string;
}

export const AdvancedOrderForm: React.FC<AdvancedOrderFormProps> = ({
    symbol,
    currentPrice,
    onOrderPlaced,
    onClose
}) => {
    const [orderTypes, setOrderTypes] = useState<OrderType[]>([]);
    const [selectedOrderType, setSelectedOrderType] = useState<string>('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string>('');
    const [success, setSuccess] = useState<string>('');

    // Form state
    const [formData, setFormData] = useState({
        user_id: 'user1', // This should come from auth context
        symbol: symbol,
        quantity: '',
        side: 'sell',
        stop_price: '',
        limit_price: '',
        trail_amount: '',
        trail_type: 'percentage',
        entry_price: '',
        stop_loss_price: '',
        take_profit_price: '',
        total_quantity: '',
        visible_quantity: '',
        duration_minutes: '',
        price_type: 'market',
        message: ''
    });

    useEffect(() => {
        loadOrderTypes();
    }, []);

    const loadOrderTypes = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/advanced-orders/types/available`);
            const data = await response.json();
            if (response.ok) {
                setOrderTypes(data.order_types || []);
            }
        } catch (err) {
            console.error('Failed to load order types:', err);
        }
    };

    const handleInputChange = (field: string, value: string) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const validateForm = (): string | null => {
        if (!selectedOrderType) {
            return 'Please select an order type';
        }

        if (!formData.quantity || parseFloat(formData.quantity) <= 0) {
            return 'Please enter a valid quantity';
        }

        switch (selectedOrderType) {
            case 'stop_loss':
                if (!formData.stop_price || parseFloat(formData.stop_price) <= 0) {
                    return 'Please enter a valid stop price';
                }
                if (parseFloat(formData.stop_price) >= currentPrice) {
                    return 'Stop price must be below current price';
                }
                break;

            case 'take_profit':
                if (!formData.limit_price || parseFloat(formData.limit_price) <= 0) {
                    return 'Please enter a valid limit price';
                }
                if (parseFloat(formData.limit_price) <= currentPrice) {
                    return 'Limit price must be above current price';
                }
                break;

            case 'trailing_stop':
                if (!formData.trail_amount || parseFloat(formData.trail_amount) <= 0) {
                    return 'Please enter a valid trail amount';
                }
                break;

            case 'bracket':
                if (!formData.entry_price || !formData.stop_loss_price || !formData.take_profit_price) {
                    return 'Please enter all prices for bracket order';
                }
                const entry = parseFloat(formData.entry_price);
                const stop = parseFloat(formData.stop_loss_price);
                const profit = parseFloat(formData.take_profit_price);
                if (stop >= entry || profit <= entry) {
                    return 'Stop loss must be below entry, take profit must be above entry';
                }
                break;

            case 'oco':
                if (!formData.stop_price || !formData.limit_price) {
                    return 'Please enter both stop and limit prices';
                }
                if (parseFloat(formData.stop_price) >= currentPrice || parseFloat(formData.limit_price) <= currentPrice) {
                    return 'Stop price must be below current price, limit price must be above';
                }
                break;

            case 'iceberg':
                if (!formData.total_quantity || !formData.visible_quantity) {
                    return 'Please enter total and visible quantities';
                }
                if (parseFloat(formData.visible_quantity) >= parseFloat(formData.total_quantity)) {
                    return 'Visible quantity must be less than total quantity';
                }
                break;

            case 'twap':
            case 'vwap':
                if (!formData.duration_minutes || parseFloat(formData.duration_minutes) <= 0) {
                    return 'Please enter a valid duration';
                }
                break;
        }

        return null;
    };

    const handleSubmit = async () => {
        const validationError = validateForm();
        if (validationError) {
            setError(validationError);
            return;
        }

        setIsLoading(true);
        setError('');
        setSuccess('');

        try {
            let endpoint = '';
            let payload: any = {
                user_id: formData.user_id,
                symbol: formData.symbol,
                quantity: parseInt(formData.quantity),
                message: formData.message
            };

            switch (selectedOrderType) {
                case 'stop_loss':
                    endpoint = '/advanced-orders/stop-loss';
                    payload.stop_price = parseFloat(formData.stop_price);
                    break;

                case 'take_profit':
                    endpoint = '/advanced-orders/take-profit';
                    payload.limit_price = parseFloat(formData.limit_price);
                    break;

                case 'trailing_stop':
                    endpoint = '/advanced-orders/trailing-stop';
                    payload.trail_amount = parseFloat(formData.trail_amount);
                    payload.trail_type = formData.trail_type;
                    break;

                case 'bracket':
                    endpoint = '/advanced-orders/bracket';
                    payload.entry_price = parseFloat(formData.entry_price);
                    payload.stop_loss_price = parseFloat(formData.stop_loss_price);
                    payload.take_profit_price = parseFloat(formData.take_profit_price);
                    break;

                case 'oco':
                    endpoint = '/advanced-orders/oco';
                    payload.stop_price = parseFloat(formData.stop_price);
                    payload.limit_price = parseFloat(formData.limit_price);
                    break;

                case 'iceberg':
                    endpoint = '/advanced-orders/iceberg';
                    payload.total_quantity = parseInt(formData.total_quantity);
                    payload.visible_quantity = parseInt(formData.visible_quantity);
                    payload.price = parseFloat(formData.limit_price);
                    payload.order_type = 'limit';
                    break;

                case 'twap':
                    endpoint = '/advanced-orders/twap';
                    payload.duration_minutes = parseInt(formData.duration_minutes);
                    payload.price_type = formData.price_type;
                    if (formData.price_type === 'limit') {
                        payload.limit_price = parseFloat(formData.limit_price);
                    }
                    break;

                case 'vwap':
                    endpoint = '/advanced-orders/vwap';
                    payload.duration_minutes = parseInt(formData.duration_minutes);
                    payload.price_type = formData.price_type;
                    if (formData.price_type === 'limit') {
                        payload.limit_price = parseFloat(formData.limit_price);
                    }
                    break;
            }

            // Use axios directly for advanced orders
            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'Failed to place order');
            }

            setSuccess('Order placed successfully!');
            onOrderPlaced(data);

            // Reset form
            setFormData(prev => ({
                ...prev,
                quantity: '',
                stop_price: '',
                limit_price: '',
                trail_amount: '',
                entry_price: '',
                stop_loss_price: '',
                take_profit_price: '',
                total_quantity: '',
                visible_quantity: '',
                duration_minutes: '',
                message: ''
            }));

        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to place order');
        } finally {
            setIsLoading(false);
        }
    };

    const getOrderTypeIcon = (type: string) => {
        switch (type) {
            case 'stop_loss':
                return <Shield className="h-4 w-4" />;
            case 'take_profit':
                return <Target className="h-4 w-4" />;
            case 'trailing_stop':
                return <TrendingUp className="h-4 w-4" />;
            case 'bracket':
                return <BarChart3 className="h-4 w-4" />;
            case 'oco':
                return <AlertTriangle className="h-4 w-4" />;
            case 'iceberg':
                return <BarChart3 className="h-4 w-4" />;
            case 'twap':
            case 'vwap':
                return <Clock className="h-4 w-4" />;
            default:
                return <Info className="h-4 w-4" />;
        }
    };

    const renderOrderTypeForm = () => {
        switch (selectedOrderType) {
            case 'stop_loss':
                return (
                    <div className="space-y-4">
                        <div>
                            <Label htmlFor="stop_price">Stop Price</Label>
                            <Input
                                id="stop_price"
                                type="number"
                                step="0.01"
                                value={formData.stop_price}
                                onChange={(e) => handleInputChange('stop_price', e.target.value)}
                                placeholder="Enter stop price"
                            />
                            <p className="text-sm text-gray-500 mt-1">
                                Current price: ${currentPrice.toFixed(2)}
                            </p>
                        </div>
                    </div>
                );

            case 'take_profit':
                return (
                    <div className="space-y-4">
                        <div>
                            <Label htmlFor="limit_price">Limit Price</Label>
                            <Input
                                id="limit_price"
                                type="number"
                                step="0.01"
                                value={formData.limit_price}
                                onChange={(e) => handleInputChange('limit_price', e.target.value)}
                                placeholder="Enter limit price"
                            />
                            <p className="text-sm text-gray-500 mt-1">
                                Current price: ${currentPrice.toFixed(2)}
                            </p>
                        </div>
                    </div>
                );

            case 'trailing_stop':
                return (
                    <div className="space-y-4">
                        <div>
                            <Label htmlFor="trail_amount">Trail Amount</Label>
                            <Input
                                id="trail_amount"
                                type="number"
                                step="0.01"
                                value={formData.trail_amount}
                                onChange={(e) => handleInputChange('trail_amount', e.target.value)}
                                placeholder="Enter trail amount"
                            />
                        </div>
                        <div>
                            <Label htmlFor="trail_type">Trail Type</Label>
                            <Select value={formData.trail_type} onValueChange={(value) => handleInputChange('trail_type', value)}>
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="percentage">Percentage</SelectItem>
                                    <SelectItem value="dollar">Dollar Amount</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                );

            case 'bracket':
                return (
                    <div className="space-y-4">
                        <div>
                            <Label htmlFor="entry_price">Entry Price</Label>
                            <Input
                                id="entry_price"
                                type="number"
                                step="0.01"
                                value={formData.entry_price}
                                onChange={(e) => handleInputChange('entry_price', e.target.value)}
                                placeholder="Enter entry price"
                            />
                        </div>
                        <div>
                            <Label htmlFor="stop_loss_price">Stop Loss Price</Label>
                            <Input
                                id="stop_loss_price"
                                type="number"
                                step="0.01"
                                value={formData.stop_loss_price}
                                onChange={(e) => handleInputChange('stop_loss_price', e.target.value)}
                                placeholder="Enter stop loss price"
                            />
                        </div>
                        <div>
                            <Label htmlFor="take_profit_price">Take Profit Price</Label>
                            <Input
                                id="take_profit_price"
                                type="number"
                                step="0.01"
                                value={formData.take_profit_price}
                                onChange={(e) => handleInputChange('take_profit_price', e.target.value)}
                                placeholder="Enter take profit price"
                            />
                        </div>
                    </div>
                );

            case 'oco':
                return (
                    <div className="space-y-4">
                        <div>
                            <Label htmlFor="stop_price">Stop Price</Label>
                            <Input
                                id="stop_price"
                                type="number"
                                step="0.01"
                                value={formData.stop_price}
                                onChange={(e) => handleInputChange('stop_price', e.target.value)}
                                placeholder="Enter stop price"
                            />
                        </div>
                        <div>
                            <Label htmlFor="limit_price">Limit Price</Label>
                            <Input
                                id="limit_price"
                                type="number"
                                step="0.01"
                                value={formData.limit_price}
                                onChange={(e) => handleInputChange('limit_price', e.target.value)}
                                placeholder="Enter limit price"
                            />
                        </div>
                        <p className="text-sm text-gray-500">
                            Current price: ${currentPrice.toFixed(2)}
                        </p>
                    </div>
                );

            case 'iceberg':
                return (
                    <div className="space-y-4">
                        <div>
                            <Label htmlFor="total_quantity">Total Quantity</Label>
                            <Input
                                id="total_quantity"
                                type="number"
                                value={formData.total_quantity}
                                onChange={(e) => handleInputChange('total_quantity', e.target.value)}
                                placeholder="Enter total quantity"
                            />
                        </div>
                        <div>
                            <Label htmlFor="visible_quantity">Visible Quantity</Label>
                            <Input
                                id="visible_quantity"
                                type="number"
                                value={formData.visible_quantity}
                                onChange={(e) => handleInputChange('visible_quantity', e.target.value)}
                                placeholder="Enter visible quantity"
                            />
                        </div>
                        <div>
                            <Label htmlFor="limit_price">Price</Label>
                            <Input
                                id="limit_price"
                                type="number"
                                step="0.01"
                                value={formData.limit_price}
                                onChange={(e) => handleInputChange('limit_price', e.target.value)}
                                placeholder="Enter price"
                            />
                        </div>
                    </div>
                );

            case 'twap':
            case 'vwap':
                return (
                    <div className="space-y-4">
                        <div>
                            <Label htmlFor="duration_minutes">Duration (minutes)</Label>
                            <Input
                                id="duration_minutes"
                                type="number"
                                value={formData.duration_minutes}
                                onChange={(e) => handleInputChange('duration_minutes', e.target.value)}
                                placeholder="Enter duration in minutes"
                            />
                        </div>
                        <div>
                            <Label htmlFor="price_type">Price Type</Label>
                            <Select value={formData.price_type} onValueChange={(value) => handleInputChange('price_type', value)}>
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="market">Market</SelectItem>
                                    <SelectItem value="limit">Limit</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        {formData.price_type === 'limit' && (
                            <div>
                                <Label htmlFor="limit_price">Limit Price</Label>
                                <Input
                                    id="limit_price"
                                    type="number"
                                    step="0.01"
                                    value={formData.limit_price}
                                    onChange={(e) => handleInputChange('limit_price', e.target.value)}
                                    placeholder="Enter limit price"
                                />
                            </div>
                        )}
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <Card className="w-full max-w-2xl">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Advanced Order - {symbol}
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
                {error && (
                    <Alert variant="destructive">
                        <AlertTriangle className="h-4 w-4" />
                        <AlertDescription>{error}</AlertDescription>
                    </Alert>
                )}

                {success && (
                    <Alert>
                        <Target className="h-4 w-4" />
                        <AlertDescription>{success}</AlertDescription>
                    </Alert>
                )}

                <div>
                    <Label htmlFor="order_type">Order Type</Label>
                    <Select value={selectedOrderType} onValueChange={setSelectedOrderType}>
                        <SelectTrigger>
                            <SelectValue placeholder="Select order type" />
                        </SelectTrigger>
                        <SelectContent>
                            {orderTypes.map((orderType) => (
                                <SelectItem key={orderType.type} value={orderType.type}>
                                    <div className="flex items-center gap-2">
                                        {getOrderTypeIcon(orderType.type)}
                                        <span>{orderType.name}</span>
                                    </div>
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                {selectedOrderType && (
                    <div className="space-y-4">
                        <div>
                            <Label htmlFor="quantity">Quantity</Label>
                            <Input
                                id="quantity"
                                type="number"
                                value={formData.quantity}
                                onChange={(e) => handleInputChange('quantity', e.target.value)}
                                placeholder="Enter quantity"
                            />
                        </div>

                        {renderOrderTypeForm()}

                        <div>
                            <Label htmlFor="message">Message (Optional)</Label>
                            <Input
                                id="message"
                                value={formData.message}
                                onChange={(e) => handleInputChange('message', e.target.value)}
                                placeholder="Enter order message"
                            />
                        </div>
                    </div>
                )}

                {selectedOrderType && orderTypes.find(ot => ot.type === selectedOrderType) && (
                    <div className="p-4 bg-blue-50 rounded-lg">
                        <h4 className="font-medium text-blue-900 mb-2">Order Description</h4>
                        <p className="text-sm text-blue-700 mb-2">
                            {orderTypes.find(ot => ot.type === selectedOrderType)?.description}
                        </p>
                        <p className="text-sm text-blue-600">
                            <strong>Use case:</strong> {orderTypes.find(ot => ot.type === selectedOrderType)?.use_case}
                        </p>
                    </div>
                )}

                <div className="flex gap-2">
                    <Button
                        onClick={handleSubmit}
                        disabled={isLoading || !selectedOrderType}
                        className="flex-1"
                    >
                        {isLoading ? 'Placing Order...' : 'Place Order'}
                    </Button>
                    <Button variant="outline" onClick={onClose}>
                        Cancel
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
};
