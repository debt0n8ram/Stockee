import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import asyncio
import aiohttp
from decimal import Decimal

from app.db import models

logger = logging.getLogger(__name__)

class CryptoAssetType(Enum):
    COIN = "coin"
    TOKEN = "token"
    STABLECOIN = "stablecoin"
    MEME = "meme"
    DEFI = "defi"
    NFT = "nft"

class DeFiProtocol(Enum):
    UNISWAP = "uniswap"
    PANCAKESWAP = "pancakeswap"
    SUSHISWAP = "sushiswap"
    CURVE = "curve"
    AAVE = "aave"
    COMPOUND = "compound"
    MAKERDAO = "makerdao"
    YEARN = "yearn"
    BALANCER = "balancer"
    SYNTHETIX = "synthetix"

class DeFiAction(Enum):
    SWAP = "swap"
    ADD_LIQUIDITY = "add_liquidity"
    REMOVE_LIQUIDITY = "remove_liquidity"
    STAKE = "stake"
    UNSTAKE = "unstake"
    LEND = "lend"
    BORROW = "borrow"
    REPAY = "repay"
    FARM = "farm"
    CLAIM_REWARDS = "claim_rewards"

@dataclass
class CryptoAsset:
    """Represents a cryptocurrency asset"""
    symbol: str
    name: str
    asset_type: CryptoAssetType
    contract_address: Optional[str] = None
    decimals: int = 18
    total_supply: Optional[float] = None
    circulating_supply: Optional[float] = None
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    price_change_24h: Optional[float] = None
    price_change_7d: Optional[float] = None

@dataclass
class DeFiPool:
    """Represents a DeFi liquidity pool"""
    protocol: DeFiProtocol
    pool_address: str
    token0: CryptoAsset
    token1: CryptoAsset
    reserve0: float
    reserve1: float
    total_supply: float
    fee: float
    apr: Optional[float] = None
    tvl: Optional[float] = None

@dataclass
class DeFiPosition:
    """Represents a DeFi position"""
    protocol: DeFiProtocol
    action: DeFiAction
    pool_address: str
    token0_amount: float
    token1_amount: float
    lp_tokens: float
    entry_price: float
    current_value: float
    unrealized_pnl: float = 0.0
    rewards: float = 0.0

@dataclass
class YieldFarming:
    """Represents yield farming opportunities"""
    protocol: DeFiProtocol
    pool_address: str
    token0: str
    token1: str
    apr: float
    tvl: float
    risk_level: str
    rewards_token: str
    lock_period: Optional[int] = None

class CryptoTradingService:
    """Comprehensive cryptocurrency trading service with DeFi integration"""
    
    def __init__(self, db: Session):
        self.db = db
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_crypto_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get current cryptocurrency prices"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Map symbols to CoinGecko IDs
            symbol_to_id = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'XRP': 'ripple',
                'DOGE': 'dogecoin',
                'ADA': 'cardano',
                'SOL': 'solana',
                'BNB': 'binancecoin',
                'DOT': 'polkadot',
                'LTC': 'litecoin',
                'LINK': 'chainlink',
                'MATIC': 'matic-network',
                'AVAX': 'avalanche-2',
                'ATOM': 'cosmos',
                'UNI': 'uniswap',
                'AAVE': 'aave',
                'SUSHI': 'sushi',
                'CRV': 'curve-dao-token',
                'COMP': 'compound-governance-token',
                'MKR': 'maker',
                'YFI': 'yearn-finance'
            }
            
            # Convert symbols to CoinGecko IDs
            coin_ids = [symbol_to_id.get(symbol.upper(), symbol.lower()) for symbol in symbols]
            coin_ids_str = ','.join(coin_ids)
            
            # Use CoinGecko API for price data
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_ids_str}&vs_currencies=usd"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Map back to original symbols
                    result = {}
                    for symbol in symbols:
                        coin_id = symbol_to_id.get(symbol.upper(), symbol.lower())
                        if coin_id in data:
                            result[symbol] = data[coin_id].get('usd', 0.0)
                        else:
                            result[symbol] = 0.0
                    return result
                else:
                    logger.error(f"Failed to fetch crypto prices: {response.status}")
                    return {symbol: 0.0 for symbol in symbols}
                    
        except Exception as e:
            logger.error(f"Error fetching crypto prices: {e}")
            return {symbol: 0.0 for symbol in symbols}
    
    async def get_crypto_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive market data for a cryptocurrency"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Get detailed market data from CoinGecko
            url = f"https://api.coingecko.com/api/v3/coins/{symbol}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    market_data = data.get('market_data', {})
                    
                    return {
                        'symbol': symbol,
                        'name': data.get('name', ''),
                        'current_price': market_data.get('current_price', {}).get('usd', 0.0),
                        'market_cap': market_data.get('market_cap', {}).get('usd', 0.0),
                        'total_volume': market_data.get('total_volume', {}).get('usd', 0.0),
                        'price_change_24h': market_data.get('price_change_percentage_24h', 0.0),
                        'price_change_7d': market_data.get('price_change_percentage_7d', 0.0),
                        'price_change_30d': market_data.get('price_change_percentage_30d', 0.0),
                        'circulating_supply': market_data.get('circulating_supply', 0.0),
                        'total_supply': market_data.get('total_supply', 0.0),
                        'max_supply': market_data.get('max_supply', 0.0),
                        'ath': market_data.get('ath', {}).get('usd', 0.0),
                        'atl': market_data.get('atl', {}).get('usd', 0.0),
                        'market_cap_rank': market_data.get('market_cap_rank', 0),
                        'description': data.get('description', {}).get('en', ''),
                        'categories': data.get('categories', []),
                        'contract_address': self._extract_contract_address(data)
                    }
                else:
                    logger.error(f"Failed to fetch market data for {symbol}: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            return {}
    
    async def get_defi_pools(self, protocol: DeFiProtocol, limit: int = 50) -> List[DeFiPool]:
        """Get DeFi liquidity pools for a protocol"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            pools = []
            
            if protocol == DeFiProtocol.UNISWAP:
                # Use Uniswap subgraph API
                query = """
                {
                    pools(first: %d, orderBy: totalValueLockedUSD, orderDirection: desc) {
                        id
                        token0 {
                            symbol
                            name
                            decimals
                        }
                        token1 {
                            symbol
                            name
                            decimals
                        }
                        reserve0
                        reserve1
                        totalSupply
                        feeTier
                        totalValueLockedUSD
                    }
                }
                """ % limit
                
                url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
                
                async with self.session.post(url, json={'query': query}) as response:
                    if response.status == 200:
                        data = await response.json()
                        pools_data = data.get('data', {}).get('pools', [])
                        
                        for pool_data in pools_data:
                            pool = DeFiPool(
                                protocol=protocol,
                                pool_address=pool_data['id'],
                                token0=CryptoAsset(
                                    symbol=pool_data['token0']['symbol'],
                                    name=pool_data['token0']['name'],
                                    asset_type=CryptoAssetType.TOKEN,
                                    decimals=int(pool_data['token0']['decimals'])
                                ),
                                token1=CryptoAsset(
                                    symbol=pool_data['token1']['symbol'],
                                    name=pool_data['token1']['name'],
                                    asset_type=CryptoAssetType.TOKEN,
                                    decimals=int(pool_data['token1']['decimals'])
                                ),
                                reserve0=float(pool_data['reserve0']),
                                reserve1=float(pool_data['reserve1']),
                                total_supply=float(pool_data['totalSupply']),
                                fee=float(pool_data['feeTier']) / 10000,  # Convert from basis points
                                tvl=float(pool_data['totalValueLockedUSD'])
                            )
                            pools.append(pool)
            
            return pools
            
        except Exception as e:
            logger.error(f"Error fetching DeFi pools for {protocol}: {e}")
            return []
    
    async def get_yield_farming_opportunities(self, min_apr: float = 5.0) -> List[YieldFarming]:
        """Get yield farming opportunities across DeFi protocols"""
        try:
            opportunities = []
            
            # Get pools from multiple protocols
            protocols = [DeFiProtocol.UNISWAP, DeFiProtocol.SUSHISWAP, DeFiProtocol.CURVE]
            
            for protocol in protocols:
                pools = await self.get_defi_pools(protocol, 20)
                
                for pool in pools:
                    if pool.tvl and pool.tvl > 1000000:  # Only pools with > $1M TVL
                        # Calculate estimated APR (simplified)
                        estimated_apr = self._calculate_estimated_apr(pool)
                        
                        if estimated_apr >= min_apr:
                            opportunity = YieldFarming(
                                protocol=protocol,
                                pool_address=pool.pool_address,
                                token0=pool.token0.symbol,
                                token1=pool.token1.symbol,
                                apr=estimated_apr,
                                tvl=pool.tvl,
                                risk_level=self._assess_risk_level(pool),
                                rewards_token="LP",
                                lock_period=None
                            )
                            opportunities.append(opportunity)
            
            # Sort by APR descending
            opportunities.sort(key=lambda x: x.apr, reverse=True)
            
            return opportunities[:50]  # Return top 50
            
        except Exception as e:
            logger.error(f"Error fetching yield farming opportunities: {e}")
            return []
    
    async def calculate_swap_quote(self, 
                                  token_in: str, 
                                  token_out: str, 
                                  amount_in: float,
                                  protocol: DeFiProtocol = DeFiProtocol.UNISWAP) -> Dict[str, Any]:
        """Calculate swap quote for token exchange"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Use 1inch API for swap quotes
            url = f"https://api.1inch.io/v5.0/1/quote"
            params = {
                'fromTokenAddress': self._get_token_address(token_in),
                'toTokenAddress': self._get_token_address(token_out),
                'amount': int(amount_in * 10**18),  # Convert to wei
                'protocols': 'UNISWAP_V3,SUSHISWAP,CURVE'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        'from_token': token_in,
                        'to_token': token_out,
                        'amount_in': amount_in,
                        'amount_out': float(data['toTokenAmount']) / 10**18,
                        'price_impact': float(data.get('priceImpact', 0)) / 100,
                        'gas_estimate': int(data.get('estimatedGas', 0)),
                        'protocols_used': data.get('protocols', []),
                        'success': True
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Failed to get quote: {response.status}'
                    }
                    
        except Exception as e:
            logger.error(f"Error calculating swap quote: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_liquidity_pool_analytics(self, pool_address: str) -> Dict[str, Any]:
        """Get analytics for a specific liquidity pool"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Get pool data from Uniswap subgraph
            query = """
            {
                pool(id: "%s") {
                    id
                    token0 {
                        symbol
                        name
                        decimals
                    }
                    token1 {
                        symbol
                        name
                        decimals
                    }
                    reserve0
                    reserve1
                    totalSupply
                    feeTier
                    totalValueLockedUSD
                    volumeUSD
                    txCount
                    liquidity
                    sqrtPrice
                    tick
                }
            }
            """ % pool_address
            
            url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
            
            async with self.session.post(url, json={'query': query}) as response:
                if response.status == 200:
                    data = await response.json()
                    pool_data = data.get('data', {}).get('pool', {})
                    
                    if pool_data:
                        return {
                            'pool_address': pool_address,
                            'token0': pool_data['token0']['symbol'],
                            'token1': pool_data['token1']['symbol'],
                            'reserve0': float(pool_data['reserve0']),
                            'reserve1': float(pool_data['reserve1']),
                            'total_supply': float(pool_data['totalSupply']),
                            'fee_tier': float(pool_data['feeTier']) / 10000,
                            'tvl': float(pool_data['totalValueLockedUSD']),
                            'volume_24h': float(pool_data.get('volumeUSD', 0)),
                            'tx_count': int(pool_data.get('txCount', 0)),
                            'liquidity': float(pool_data.get('liquidity', 0)),
                            'current_price': self._calculate_pool_price(pool_data),
                            'price_range': self._calculate_price_range(pool_data)
                        }
                
                return {}
                
        except Exception as e:
            logger.error(f"Error getting pool analytics: {e}")
            return {}
    
    async def get_crypto_portfolio_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive crypto portfolio analytics"""
        try:
            # Get user's crypto holdings
            holdings = self._get_user_crypto_holdings(user_id)
            
            if not holdings:
                return {'error': 'No crypto holdings found'}
            
            # Get current prices
            symbols = [holding['symbol'] for holding in holdings]
            prices = await self.get_crypto_prices(symbols)
            
            # Calculate portfolio metrics
            total_value = 0.0
            total_cost = 0.0
            positions = []
            
            for holding in holdings:
                current_price = prices.get(holding['symbol'], 0.0)
                current_value = holding['quantity'] * current_price
                cost_basis = holding['quantity'] * holding['avg_price']
                unrealized_pnl = current_value - cost_basis
                
                total_value += current_value
                total_cost += cost_basis
                
                positions.append({
                    'symbol': holding['symbol'],
                    'quantity': holding['quantity'],
                    'avg_price': holding['avg_price'],
                    'current_price': current_price,
                    'current_value': current_value,
                    'cost_basis': cost_basis,
                    'unrealized_pnl': unrealized_pnl,
                    'pnl_percentage': (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
                })
            
            total_pnl = total_value - total_cost
            total_pnl_percentage = (total_pnl / total_cost * 100) if total_cost > 0 else 0
            
            return {
                'total_value': total_value,
                'total_cost': total_cost,
                'total_pnl': total_pnl,
                'total_pnl_percentage': total_pnl_percentage,
                'positions': positions,
                'diversification': self._calculate_diversification(positions),
                'risk_metrics': self._calculate_crypto_risk_metrics(positions)
            }
            
        except Exception as e:
            logger.error(f"Error calculating crypto portfolio analytics: {e}")
            return {'error': str(e)}
    
    async def get_defi_positions(self, user_id: str) -> List[DeFiPosition]:
        """Get user's DeFi positions"""
        try:
            # This would typically query on-chain data or a database
            # For now, return mock data
            positions = []
            
            # Mock DeFi positions
            mock_positions = [
                {
                    'protocol': DeFiProtocol.UNISWAP,
                    'action': DeFiAction.ADD_LIQUIDITY,
                    'pool_address': '0x123...',
                    'token0_amount': 1000.0,
                    'token1_amount': 0.5,
                    'lp_tokens': 500.0,
                    'entry_price': 2000.0,
                    'current_value': 2500.0
                }
            ]
            
            for pos_data in mock_positions:
                position = DeFiPosition(
                    protocol=pos_data['protocol'],
                    action=pos_data['action'],
                    pool_address=pos_data['pool_address'],
                    token0_amount=pos_data['token0_amount'],
                    token1_amount=pos_data['token1_amount'],
                    lp_tokens=pos_data['lp_tokens'],
                    entry_price=pos_data['entry_price'],
                    current_value=pos_data['current_value'],
                    unrealized_pnl=pos_data['current_value'] - pos_data['entry_price']
                )
                positions.append(position)
            
            return positions
            
        except Exception as e:
            logger.error(f"Error getting DeFi positions: {e}")
            return []
    
    def _extract_contract_address(self, coin_data: Dict) -> Optional[str]:
        """Extract contract address from coin data"""
        try:
            platforms = coin_data.get('platforms', {})
            if 'ethereum' in platforms:
                return platforms['ethereum']
            elif 'binance-smart-chain' in platforms:
                return platforms['binance-smart-chain']
            return None
        except:
            return None
    
    def _get_token_address(self, symbol: str) -> str:
        """Get token contract address by symbol"""
        # Common token addresses (simplified)
        token_addresses = {
            'ETH': '0x0000000000000000000000000000000000000000',
            'USDC': '0xA0b86a33E6441b8c4C8C0C4C0C4C0C4C0C4C0C4C',
            'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
            'WBTC': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
            'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F'
        }
        return token_addresses.get(symbol.upper(), '0x0000000000000000000000000000000000000000')
    
    def _calculate_estimated_apr(self, pool: DeFiPool) -> float:
        """Calculate estimated APR for a pool"""
        try:
            if not pool.tvl or pool.tvl <= 0:
                return 0.0
            
            # Simplified APR calculation based on TVL and volume
            # In practice, this would be more sophisticated
            base_apr = 5.0  # Base 5% APR
            volume_multiplier = min(2.0, pool.tvl / 10000000)  # Up to 2x for high TVL
            return base_apr * volume_multiplier
            
        except:
            return 0.0
    
    def _assess_risk_level(self, pool: DeFiPool) -> str:
        """Assess risk level for a DeFi pool"""
        try:
            if pool.tvl and pool.tvl > 100000000:  # > $100M TVL
                return "Low"
            elif pool.tvl and pool.tvl > 10000000:  # > $10M TVL
                return "Medium"
            else:
                return "High"
        except:
            return "High"
    
    def _calculate_pool_price(self, pool_data: Dict) -> float:
        """Calculate current price from pool data"""
        try:
            reserve0 = float(pool_data['reserve0'])
            reserve1 = float(pool_data['reserve1'])
            
            if reserve0 > 0 and reserve1 > 0:
                return reserve1 / reserve0
            return 0.0
        except:
            return 0.0
    
    def _calculate_price_range(self, pool_data: Dict) -> Dict[str, float]:
        """Calculate price range for a pool"""
        try:
            # Simplified price range calculation
            current_price = self._calculate_pool_price(pool_data)
            return {
                'min_price': current_price * 0.9,
                'max_price': current_price * 1.1,
                'current_price': current_price
            }
        except:
            return {'min_price': 0.0, 'max_price': 0.0, 'current_price': 0.0}
    
    def _get_user_crypto_holdings(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's crypto holdings from database"""
        try:
            # This would query the database for user's crypto holdings
            # For now, return mock data
            return [
                {
                    'symbol': 'BTC',
                    'quantity': 0.5,
                    'avg_price': 45000.0
                },
                {
                    'symbol': 'ETH',
                    'quantity': 2.0,
                    'avg_price': 3000.0
                },
                {
                    'symbol': 'USDC',
                    'quantity': 5000.0,
                    'avg_price': 1.0
                }
            ]
        except:
            return []
    
    def _calculate_diversification(self, positions: List[Dict]) -> Dict[str, Any]:
        """Calculate portfolio diversification metrics"""
        try:
            if not positions:
                return {}
            
            total_value = sum(pos['current_value'] for pos in positions)
            
            # Calculate concentration
            concentrations = []
            for pos in positions:
                concentration = pos['current_value'] / total_value
                concentrations.append(concentration)
            
            # Calculate Herfindahl-Hirschman Index
            hhi = sum(c**2 for c in concentrations)
            
            # Calculate effective number of assets
            effective_assets = 1 / hhi if hhi > 0 else 0
            
            return {
                'hhi': hhi,
                'effective_assets': effective_assets,
                'concentration_risk': 'High' if hhi > 0.25 else 'Medium' if hhi > 0.15 else 'Low',
                'top_holdings': sorted(positions, key=lambda x: x['current_value'], reverse=True)[:3]
            }
            
        except:
            return {}
    
    def _calculate_crypto_risk_metrics(self, positions: List[Dict]) -> Dict[str, Any]:
        """Calculate crypto-specific risk metrics"""
        try:
            if not positions:
                return {}
            
            # Calculate volatility (simplified)
            returns = [pos['pnl_percentage'] / 100 for pos in positions]
            volatility = np.std(returns) if len(returns) > 1 else 0.0
            
            # Calculate VaR (simplified)
            var_95 = np.percentile(returns, 5) if len(returns) > 1 else 0.0
            
            # Calculate max drawdown (simplified)
            cumulative_returns = np.cumprod([1 + r for r in returns])
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdowns = (cumulative_returns - running_max) / running_max
            max_drawdown = np.min(drawdowns) if len(drawdowns) > 0 else 0.0
            
            return {
                'volatility': volatility,
                'var_95': var_95,
                'max_drawdown': max_drawdown,
                'risk_level': 'High' if volatility > 0.5 else 'Medium' if volatility > 0.2 else 'Low'
            }
            
        except:
            return {}
