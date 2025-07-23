import sys
import requests
from web3 import Web3

def compute_l1_gas_and_fee(input_data_hex, gas_price_l1, overhead=1400, safety_factor=1.1):
    """
    Estimate L1 gas used and L1 fee based on calldata size and security margins.
    """
    data = input_data_hex[2:]  # remove '0x'
    bytes_data = [data[i:i+2] for i in range(0, len(data), 2)]
    nb_non_null = sum(1 for b in bytes_data if b != '00')
    nb_null = len(bytes_data) - nb_non_null

    l1_gas_used = (nb_non_null * 16) + (nb_null * 4) + overhead
    l1_gas_used = int(l1_gas_used * safety_factor)

    l1_fee_wei = l1_gas_used * gas_price_l1
    l1_fee_eth = l1_fee_wei / 1e18
    return l1_gas_used, l1_fee_eth

def get_gas_price_arbitrum():
    """ Get current L2 gas price on Arbitrum mainnet. """
    w3_arb = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
    return w3_arb.eth.gas_price  # in wei

import requests

import requests

def get_eth_price_usd():
    """Fetch current ETH price in USD, with Binance fallback."""
    coingecko_url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    binance_url = "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"

    try:
        response = requests.get(coingecko_url, timeout=10)
        response.raise_for_status()
        price = response.json().get("ethereum", {}).get("usd")
        if price is not None:
            return float(price)
    except requests.RequestException as e:
        print(f"CoinGecko API failed: {e}")

    try:
        response = requests.get(binance_url, timeout=10)
        response.raise_for_status()
        return float(response.json().get("price"))
    except requests.RequestException as e:
        print(f"Binance API failed: {e}")
        raise RuntimeError("Failed to fetch ETH price from both APIs")



# ---------------------------
# CONFIGURATION
# ---------------------------
if len(sys.argv) < 2:
    print("Usage: python get_tx_fee_estimation.py <TX_HASH> [arbitrum|bellecour|arbitrum-sepolia]")
    sys.exit(1)

TX_HASH = sys.argv[1]
NETWORK = sys.argv[2].lower() if len(sys.argv) > 2 else "bellecour"

# RPC endpoints
if NETWORK == "arbitrum":
    RPC_URL_L2 = "https://arb1.arbitrum.io/rpc"
elif NETWORK == "bellecour":
    RPC_URL_L2 = "https://bellecour.iex.ec"
elif NETWORK == "arbitrum-sepolia":
    RPC_URL_L2 = "https://sepolia-rollup.arbitrum.io/rpc"
else:
    print("Unknown network. Choose 'arbitrum', 'bellecour', or 'arbitrum-sepolia'.")
    sys.exit(1)

RPC_URL_ETH = "https://ethereum.publicnode.com"

# ---------------------------
# CONNECT TO RPC NODES
# ---------------------------
w3_l2 = Web3(Web3.HTTPProvider(RPC_URL_L2))
w3_eth = Web3(Web3.HTTPProvider(RPC_URL_ETH))

if not w3_l2.is_connected():
    raise Exception(f"Failed to connect to {NETWORK} RPC ({RPC_URL_L2}).")
if not w3_eth.is_connected():
    raise Exception(f"Failed to connect to Ethereum RPC ({RPC_URL_ETH}).")

# ---------------------------
# FETCH TRANSACTION DATA
# ---------------------------
tx = w3_l2.eth.get_transaction(TX_HASH)
receipt = w3_l2.eth.get_transaction_receipt(TX_HASH)

# ---------------------------
# L2 GAS & FEE
# ---------------------------
gas_used_L2 = receipt.gasUsed
gas_price_L2 = tx.gasPrice
L2_fee_eth = (gas_used_L2 * gas_price_L2) / 1e18

# ---------------------------
# L1 GAS & FEE (estimated)
# ---------------------------
gas_price_L1 = w3_eth.eth.gas_price
l1_gas_used_est, L1_fee_eth = compute_l1_gas_and_fee(tx["input"], gas_price_L1)

# ---------------------------
# ETH PRICE IN USD
# ---------------------------
eth_price_usd = get_eth_price_usd()

# Convert to USD
L2_fee_usd = L2_fee_eth * eth_price_usd
L1_fee_usd = L1_fee_eth * eth_price_usd
total_fee_eth = L1_fee_eth + L2_fee_eth
total_fee_usd = total_fee_eth * eth_price_usd

# ---------------------------
# ARBITRUM MAINNET ESTIMATION (for bellecour or arbitrum-sepolia)
# ---------------------------
if NETWORK in ["bellecour", "arbitrum-sepolia"]:
    arb_gas_price_L2 = get_gas_price_arbitrum()
    L2_fee_eth_arb = (gas_used_L2 * arb_gas_price_L2) / 1e18
    L2_fee_usd_arb = L2_fee_eth_arb * eth_price_usd
    L1_fee_eth_arb = (l1_gas_used_est * gas_price_L1) / 1e18
    L1_fee_usd_arb = L1_fee_eth_arb * eth_price_usd
    total_fee_eth_arb = L1_fee_eth_arb + L2_fee_eth_arb
    total_fee_usd_arb = total_fee_eth_arb * eth_price_usd
else:
    arb_gas_price_L2 = None

# ---------------------------
# DISPLAY RESULTS
# ---------------------------
print(f"=== Transaction on {NETWORK.upper()} ===")
print(f"  - Hash              : {TX_HASH}")

print(f"\n--- L2 ---")
print(f"  - Gas Used (L2)     : {gas_used_L2}")
print(f"  - Gas Price (L2)    : {gas_price_L2 / 1e9:.2f} gwei")
print(f"  - L2 Fee            : {L2_fee_eth:.8f} ETH (${L2_fee_usd:.4f})")

print(f"\n--- L1 (estimated) ---")
print(f"  - Gas Used (L1)     : {l1_gas_used_est}")
print(f"  - Gas Price (L1)    : {gas_price_L1 / 1e9:.2f} gwei")
print(f"  - L1 Fee            : {L1_fee_eth:.8f} ETH (${L1_fee_usd:.4f})")

print(f"\n=== TOTAL ===")
print(f"  - TOTAL (L1+L2)     : {total_fee_eth:.8f} ETH (${total_fee_usd:.4f})")

if NETWORK in ["bellecour", "arbitrum-sepolia"]:
    print("\n=== COST IF ON ARBITRUM MAINNET ===")
    print(f"  - Gas Price (L2) Arb: {arb_gas_price_L2 / 1e9:.2f} gwei")
    print(f"  - L2 Fee (Arbitrum) : {L2_fee_eth_arb:.8f} ETH (${L2_fee_usd_arb:.4f})")
    print(f"  - L1 Fee (Arbitrum) : {L1_fee_eth_arb:.8f} ETH (${L1_fee_usd_arb:.4f})")
    print(f"  - TOTAL (Arbitrum)  : {total_fee_eth_arb:.8f} ETH (${total_fee_usd_arb:.4f})")
