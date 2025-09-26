from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.crypto_trading_service import CryptoTradingService, DeFiProtocol, DeFiAction
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/crypto", tags=["crypto-trading"])

class CryptoPriceRequest(BaseModel):
    symbols: List[str]

class SwapQuoteRequest(BaseModel):
    token_in: str
    token_out: str
    amount_in: float
    protocol: str = "uniswap"

class DeFiPoolRequest(BaseModel):
    protocol: str
    limit: int = 50

class YieldFarmingRequest(BaseModel):
    min_apr: float = 5.0

@router.get("/prices")
async def get_crypto_prices(
    symbols: str = Query(..., description="Comma-separated list of crypto symbols"),
    db: Session = Depends(get_db)
):
    """Get current cryptocurrency prices"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        
        async with CryptoTradingService(db) as service:
            prices = await service.get_crypto_prices(symbol_list)
            
            return {
                "success": True,
                "prices": prices,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-data/{symbol}")
async def get_crypto_market_data(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive market data for a cryptocurrency"""
    try:
        async with CryptoTradingService(db) as service:
            market_data = await service.get_crypto_market_data(symbol.lower())
            
            if not market_data:
                raise HTTPException(status_code=404, detail=f"Market data not found for {symbol}")
            
            return {
                "success": True,
                "market_data": market_data
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/defi/pools")
async def get_defi_pools(
    protocol: str = Query("uniswap", description="DeFi protocol"),
    limit: int = Query(50, description="Number of pools to return"),
    db: Session = Depends(get_db)
):
    """Get DeFi liquidity pools"""
    try:
        try:
            protocol_enum = DeFiProtocol(protocol.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid protocol: {protocol}")
        
        async with CryptoTradingService(db) as service:
            pools = await service.get_defi_pools(protocol_enum, limit)
            
            # Convert pools to dict format
            pools_data = []
            for pool in pools:
                pools_data.append({
                    'protocol': pool.protocol.value,
                    'pool_address': pool.pool_address,
                    'token0': {
                        'symbol': pool.token0.symbol,
                        'name': pool.token0.name,
                        'decimals': pool.token0.decimals
                    },
                    'token1': {
                        'symbol': pool.token1.symbol,
                        'name': pool.token1.name,
                        'decimals': pool.token1.decimals
                    },
                    'reserve0': pool.reserve0,
                    'reserve1': pool.reserve1,
                    'total_supply': pool.total_supply,
                    'fee': pool.fee,
                    'apr': pool.apr,
                    'tvl': pool.tvl
                })
            
            return {
                "success": True,
                "pools": pools_data,
                "total_count": len(pools_data)
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/defi/yield-farming")
async def get_yield_farming_opportunities(
    min_apr: float = Query(5.0, description="Minimum APR percentage"),
    db: Session = Depends(get_db)
):
    """Get yield farming opportunities"""
    try:
        async with CryptoTradingService(db) as service:
            opportunities = await service.get_yield_farming_opportunities(min_apr)
            
            # Convert to dict format
            opportunities_data = []
            for opp in opportunities:
                opportunities_data.append({
                    'protocol': opp.protocol.value,
                    'pool_address': opp.pool_address,
                    'token0': opp.token0,
                    'token1': opp.token1,
                    'apr': opp.apr,
                    'tvl': opp.tvl,
                    'risk_level': opp.risk_level,
                    'rewards_token': opp.rewards_token,
                    'lock_period': opp.lock_period
                })
            
            return {
                "success": True,
                "opportunities": opportunities_data,
                "total_count": len(opportunities_data)
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/defi/swap-quote")
async def calculate_swap_quote(
    request: SwapQuoteRequest,
    db: Session = Depends(get_db)
):
    """Calculate swap quote for token exchange"""
    try:
        try:
            protocol_enum = DeFiProtocol(request.protocol.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid protocol: {request.protocol}")
        
        async with CryptoTradingService(db) as service:
            quote = await service.calculate_swap_quote(
                request.token_in,
                request.token_out,
                request.amount_in,
                protocol_enum
            )
            
            return {
                "success": quote.get('success', False),
                "quote": quote
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/defi/pool-analytics/{pool_address}")
async def get_liquidity_pool_analytics(
    pool_address: str,
    db: Session = Depends(get_db)
):
    """Get analytics for a specific liquidity pool"""
    try:
        async with CryptoTradingService(db) as service:
            analytics = await service.get_liquidity_pool_analytics(pool_address)
            
            if not analytics:
                raise HTTPException(status_code=404, detail=f"Pool analytics not found for {pool_address}")
            
            return {
                "success": True,
                "analytics": analytics
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio/analytics/{user_id}")
async def get_crypto_portfolio_analytics(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive crypto portfolio analytics"""
    try:
        async with CryptoTradingService(db) as service:
            analytics = await service.get_crypto_portfolio_analytics(user_id)
            
            if "error" in analytics:
                raise HTTPException(status_code=400, detail=analytics["error"])
            
            return {
                "success": True,
                "analytics": analytics
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/defi/positions/{user_id}")
async def get_defi_positions(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user's DeFi positions"""
    try:
        async with CryptoTradingService(db) as service:
            positions = await service.get_defi_positions(user_id)
            
            # Convert to dict format
            positions_data = []
            for pos in positions:
                positions_data.append({
                    'protocol': pos.protocol.value,
                    'action': pos.action.value,
                    'pool_address': pos.pool_address,
                    'token0_amount': pos.token0_amount,
                    'token1_amount': pos.token1_amount,
                    'lp_tokens': pos.lp_tokens,
                    'entry_price': pos.entry_price,
                    'current_value': pos.current_value,
                    'unrealized_pnl': pos.unrealized_pnl,
                    'rewards': pos.rewards
                })
            
            return {
                "success": True,
                "positions": positions_data,
                "total_count": len(positions_data)
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/defi/protocols")
async def get_available_defi_protocols():
    """Get list of available DeFi protocols"""
    return {
        "protocols": [
            {
                "name": "Uniswap",
                "value": "uniswap",
                "description": "Decentralized exchange for token swaps",
                "category": "DEX"
            },
            {
                "name": "PancakeSwap",
                "value": "pancakeswap",
                "description": "Decentralized exchange on BSC",
                "category": "DEX"
            },
            {
                "name": "SushiSwap",
                "value": "sushiswap",
                "description": "Decentralized exchange with yield farming",
                "category": "DEX"
            },
            {
                "name": "Curve",
                "value": "curve",
                "description": "Stablecoin and pegged asset exchange",
                "category": "DEX"
            },
            {
                "name": "Aave",
                "value": "aave",
                "description": "Decentralized lending and borrowing",
                "category": "Lending"
            },
            {
                "name": "Compound",
                "value": "compound",
                "description": "Decentralized lending protocol",
                "category": "Lending"
            },
            {
                "name": "MakerDAO",
                "value": "makerdao",
                "description": "Decentralized stablecoin protocol",
                "category": "Stablecoin"
            },
            {
                "name": "Yearn",
                "value": "yearn",
                "description": "Yield farming aggregator",
                "category": "Yield"
            },
            {
                "name": "Balancer",
                "value": "balancer",
                "description": "Automated market maker",
                "category": "DEX"
            },
            {
                "name": "Synthetix",
                "value": "synthetix",
                "description": "Synthetic asset protocol",
                "category": "Synthetic"
            }
        ]
    }

@router.get("/defi/actions")
async def get_available_defi_actions():
    """Get list of available DeFi actions"""
    return {
        "actions": [
            {
                "name": "Swap",
                "value": "swap",
                "description": "Exchange one token for another"
            },
            {
                "name": "Add Liquidity",
                "value": "add_liquidity",
                "description": "Provide liquidity to a pool"
            },
            {
                "name": "Remove Liquidity",
                "value": "remove_liquidity",
                "description": "Withdraw liquidity from a pool"
            },
            {
                "name": "Stake",
                "value": "stake",
                "description": "Stake tokens to earn rewards"
            },
            {
                "name": "Unstake",
                "value": "unstake",
                "description": "Unstake tokens and claim rewards"
            },
            {
                "name": "Lend",
                "value": "lend",
                "description": "Lend tokens to earn interest"
            },
            {
                "name": "Borrow",
                "value": "borrow",
                "description": "Borrow tokens against collateral"
            },
            {
                "name": "Repay",
                "value": "repay",
                "description": "Repay borrowed tokens"
            },
            {
                "name": "Farm",
                "value": "farm",
                "description": "Participate in yield farming"
            },
            {
                "name": "Claim Rewards",
                "value": "claim_rewards",
                "description": "Claim earned rewards"
            }
        ]
    }

@router.get("/market/trending")
async def get_trending_cryptocurrencies(
    limit: int = Query(20, description="Number of trending cryptos to return"),
    db: Session = Depends(get_db)
):
    """Get trending cryptocurrencies"""
    try:
        async with CryptoTradingService(db) as service:
            # Get trending cryptos from CoinGecko
            if not service.session:
                service.session = aiohttp.ClientSession()
            
            url = f"https://api.coingecko.com/api/v3/search/trending"
            
            async with service.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    trending = data.get('coins', [])[:limit]
                    
                    trending_data = []
                    for coin in trending:
                        coin_data = coin.get('item', {})
                        trending_data.append({
                            'id': coin_data.get('id', ''),
                            'name': coin_data.get('name', ''),
                            'symbol': coin_data.get('symbol', '').upper(),
                            'market_cap_rank': coin_data.get('market_cap_rank', 0),
                            'thumb': coin_data.get('thumb', ''),
                            'price_btc': coin_data.get('price_btc', 0.0)
                        })
                    
                    return {
                        "success": True,
                        "trending": trending_data
                    }
                else:
                    raise HTTPException(status_code=500, detail="Failed to fetch trending data")
                    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/categories")
async def get_crypto_categories():
    """Get cryptocurrency categories"""
    return {
        "categories": [
            {
                "name": "DeFi",
                "description": "Decentralized Finance protocols and tokens"
            },
            {
                "name": "Layer 1",
                "description": "Base layer blockchain protocols"
            },
            {
                "name": "Layer 2",
                "description": "Scaling solutions built on top of Layer 1"
            },
            {
                "name": "Stablecoins",
                "description": "Price-stable cryptocurrencies"
            },
            {
                "name": "Meme Coins",
                "description": "Community-driven meme cryptocurrencies"
            },
            {
                "name": "NFT",
                "description": "Non-fungible token related projects"
            },
            {
                "name": "Gaming",
                "description": "Blockchain gaming and metaverse projects"
            },
            {
                "name": "Privacy",
                "description": "Privacy-focused cryptocurrencies"
            },
            {
                "name": "Oracle",
                "description": "Blockchain oracle networks"
            },
            {
                "name": "Storage",
                "description": "Decentralized storage solutions"
            }
        ]
    }

@router.get("/education/defi-basics")
async def get_defi_education():
    """Get DeFi education content"""
    return {
        "education": {
            "basics": {
                "title": "DeFi Basics",
                "content": [
                    {
                        "concept": "Decentralized Exchanges (DEXs)",
                        "description": "Platforms that allow users to trade cryptocurrencies without intermediaries",
                        "examples": ["Uniswap", "SushiSwap", "PancakeSwap"]
                    },
                    {
                        "concept": "Liquidity Pools",
                        "description": "Pools of tokens that provide liquidity for trading and earn fees",
                        "examples": ["ETH/USDC", "BTC/WBTC", "DAI/USDC"]
                    },
                    {
                        "concept": "Yield Farming",
                        "description": "Earning rewards by providing liquidity or staking tokens",
                        "examples": ["Liquidity mining", "Staking rewards", "Governance tokens"]
                    },
                    {
                        "concept": "Lending & Borrowing",
                        "description": "Decentralized protocols for lending and borrowing cryptocurrencies",
                        "examples": ["Aave", "Compound", "MakerDAO"]
                    }
                ]
            },
            "risks": {
                "title": "DeFi Risks",
                "content": [
                    {
                        "risk": "Smart Contract Risk",
                        "description": "Code vulnerabilities that could lead to loss of funds",
                        "mitigation": "Audit protocols, use established platforms"
                    },
                    {
                        "risk": "Impermanent Loss",
                        "description": "Loss when providing liquidity due to price changes",
                        "mitigation": "Understand the concept, choose stable pairs"
                    },
                    {
                        "risk": "Liquidity Risk",
                        "description": "Difficulty exiting positions due to low liquidity",
                        "mitigation": "Check pool size, use established protocols"
                    },
                    {
                        "risk": "Regulatory Risk",
                        "description": "Potential regulatory changes affecting DeFi",
                        "mitigation": "Stay informed, diversify across jurisdictions"
                    }
                ]
            },
            "strategies": {
                "title": "DeFi Strategies",
                "content": [
                    {
                        "strategy": "Liquidity Provision",
                        "description": "Provide liquidity to earn trading fees",
                        "risk_level": "Medium",
                        "potential_return": "5-20% APY"
                    },
                    {
                        "strategy": "Yield Farming",
                        "description": "Stake tokens to earn additional rewards",
                        "risk_level": "High",
                        "potential_return": "10-100% APY"
                    },
                    {
                        "strategy": "Lending",
                        "description": "Lend tokens to earn interest",
                        "risk_level": "Low",
                        "potential_return": "2-10% APY"
                    },
                    {
                        "strategy": "Arbitrage",
                        "description": "Exploit price differences across platforms",
                        "risk_level": "Medium",
                        "potential_return": "Variable"
                    }
                ]
            }
        }
    }
