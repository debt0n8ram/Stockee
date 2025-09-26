import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Search, TrendingUp, TrendingDown } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { apiService } from '../services/api';

export const Trading: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAsset, setSelectedAsset] = useState<any>(null);
  const [orderType, setOrderType] = useState<'buy' | 'sell'>('buy');
  const [quantity, setQuantity] = useState('');
  const [orderPriceType, setOrderPriceType] = useState<'market' | 'limit'>('market');
  const [limitPrice, setLimitPrice] = useState('');

  const queryClient = useQueryClient();

  // Helper function to safely extract price value
  const getPriceValue = (priceData: any): number | string => {
    if (priceData === null || priceData === undefined) {
      return 'N/A';
    }

    if (typeof priceData === 'number') {
      return priceData;
    }

    if (typeof priceData === 'object' && priceData.price !== undefined) {
      return priceData.price;
    }

    console.warn('🚨 UNEXPECTED PRICE DATA FORMAT:', priceData);
    return 'N/A';
  };

  // Helper function to safely extract numeric price value for calculations
  const getNumericPriceValue = (priceData: any): number => {
    const priceValue = getPriceValue(priceData);
    if (typeof priceValue === 'number') {
      return priceValue;
    }
    return 0;
  };

  const { data: searchResults, isLoading: searchLoading } = useQuery(
    ['search', searchQuery],
    () => apiService.searchAssets(searchQuery),
    { enabled: searchQuery.length > 2 }
  );

  const { data: currentPrice } = useQuery(
    ['price', selectedAsset?.symbol],
    () => apiService.getCurrentPrice(selectedAsset?.symbol),
    {
      enabled: !!selectedAsset?.symbol,
      onSuccess: (data) => {
        console.log('🚨 CURRENT PRICE DATA:', data);
        if (data && typeof data === 'object' && 'symbol' in data && 'price' in data && 'timestamp' in data) {
          console.warn('🚨 FULL PRICE OBJECT RECEIVED:', data);
        }
      }
    }
  );

  const executeOrderMutation = useMutation(
    (orderData: any) => {
      if (orderType === 'buy') {
        return apiService.buyStock('user1', orderData);
      } else {
        return apiService.sellStock('user1', orderData);
      }
    },
    {
      onSuccess: (response: any) => {
        if (response?.success) {
          toast.success(response?.message || 'Order executed successfully');
          queryClient.invalidateQueries('portfolio');
          queryClient.invalidateQueries('performance');
          setQuantity('');
          setLimitPrice('');
        } else {
          toast.error(response?.message || 'Order failed');
        }
      },
      onError: (error: any) => {
        toast.error(error?.message || 'Order failed');
      }
    }
  );

  const handleOrderSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedAsset || !quantity) {
      toast.error('Please select an asset and enter quantity');
      return;
    }

    const orderData = {
      symbol: selectedAsset.symbol,
      quantity: parseFloat(quantity),
      order_type: orderPriceType,
      limit_price: orderPriceType === 'limit' ? parseFloat(limitPrice) : undefined
    };

    executeOrderMutation.mutate(orderData);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Trading</h1>
        <p className="mt-2 text-gray-600">Buy and sell stocks and cryptocurrencies</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Asset Search */}
        <div className="lg:col-span-1">
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Search Assets</h3>

            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by symbol or name..."
                className="input-field pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            {searchLoading && (
              <div className="text-center py-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              </div>
            )}

            {searchResults && searchResults.length > 0 && (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {searchResults.map((asset: any) => (
                  <div
                    key={asset.symbol}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${selectedAsset?.symbol === asset.symbol
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                      }`}
                    onClick={() => setSelectedAsset(asset)}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium text-gray-900">{asset.symbol}</p>
                        <p className="text-sm text-gray-500">{asset.name}</p>
                      </div>
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                        {asset.asset_type}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Trading Form */}
        <div className="lg:col-span-2">
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Place Order</h3>

            {selectedAsset ? (
              <div className="space-y-4">
                {/* Selected Asset Info */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <h4 className="font-medium text-gray-900">{selectedAsset.symbol}</h4>
                      <p className="text-sm text-gray-600">{selectedAsset.name}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-gray-900">
                        ${getPriceValue(currentPrice)}
                      </p>
                      <p className="text-sm text-gray-500">Current Price</p>
                    </div>
                  </div>
                </div>

                {/* Order Form */}
                <form onSubmit={handleOrderSubmit} className="space-y-4">
                  {/* Order Type */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Order Type
                    </label>
                    <div className="flex space-x-4">
                      <label className="flex items-center">
                        <input
                          type="radio"
                          value="buy"
                          checked={orderType === 'buy'}
                          onChange={(e) => setOrderType(e.target.value as 'buy' | 'sell')}
                          className="mr-2"
                        />
                        <span className="flex items-center text-green-600">
                          <TrendingUp className="h-4 w-4 mr-1" />
                          Buy
                        </span>
                      </label>
                      <label className="flex items-center">
                        <input
                          type="radio"
                          value="sell"
                          checked={orderType === 'sell'}
                          onChange={(e) => setOrderType(e.target.value as 'buy' | 'sell')}
                          className="mr-2"
                        />
                        <span className="flex items-center text-red-600">
                          <TrendingDown className="h-4 w-4 mr-1" />
                          Sell
                        </span>
                      </label>
                    </div>
                  </div>

                  {/* Quantity */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Quantity
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      className="input-field"
                      value={quantity}
                      onChange={(e) => setQuantity(e.target.value)}
                      placeholder="Enter quantity"
                    />
                  </div>

                  {/* Price Type */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Price Type
                    </label>
                    <div className="flex space-x-4">
                      <label className="flex items-center">
                        <input
                          type="radio"
                          value="market"
                          checked={orderPriceType === 'market'}
                          onChange={(e) => setOrderPriceType(e.target.value as 'market' | 'limit')}
                          className="mr-2"
                        />
                        Market Order
                      </label>
                      <label className="flex items-center">
                        <input
                          type="radio"
                          value="limit"
                          checked={orderPriceType === 'limit'}
                          onChange={(e) => setOrderPriceType(e.target.value as 'market' | 'limit')}
                          className="mr-2"
                        />
                        Limit Order
                      </label>
                    </div>
                  </div>

                  {/* Limit Price */}
                  {orderPriceType === 'limit' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Limit Price
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        className="input-field"
                        value={limitPrice}
                        onChange={(e) => setLimitPrice(e.target.value)}
                        placeholder="Enter limit price"
                      />
                    </div>
                  )}

                  {/* Order Summary */}
                  {quantity && (
                    <div className="bg-blue-50 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-2">Order Summary</h4>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Action:</span>
                          <span className={orderType === 'buy' ? 'text-green-600' : 'text-red-600'}>
                            {orderType.toUpperCase()}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Asset:</span>
                          <span className="font-medium">{selectedAsset.symbol}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Quantity:</span>
                          <span className="font-medium">{quantity}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Price:</span>
                          <span className="font-medium">
                            {orderPriceType === 'market'
                              ? `$${getPriceValue(currentPrice)}`
                              : `$${limitPrice}`
                            }
                          </span>
                        </div>
                        <div className="flex justify-between font-medium">
                          <span className="text-gray-600">Total:</span>
                          <span>
                            ${((parseFloat(quantity) || 0) * (orderPriceType === 'market' ? getNumericPriceValue(currentPrice) : parseFloat(limitPrice) || 0)).toFixed(2)}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Submit Button */}
                  <button
                    type="submit"
                    disabled={executeOrderMutation.isPending || !quantity}
                    className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${executeOrderMutation.isPending || !quantity
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : orderType === 'buy'
                        ? 'bg-green-600 hover:bg-green-700 text-white'
                        : 'bg-red-600 hover:bg-red-700 text-white'
                      }`}
                  >
                    {executeOrderMutation.isPending ? 'Processing...' : `${orderType.toUpperCase()} ${selectedAsset.symbol}`}
                  </button>
                </form>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Search className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Select an asset to start trading</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
