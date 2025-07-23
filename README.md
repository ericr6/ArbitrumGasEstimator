# Transaction Fee Estimation for Arbitrum from iExec Bellecour or Arbitrum chain 

A Python script that estimates L1 and L2 gas fees on Arbitrum for a given transaction observed on other blockchains. It currently supports transactions from iExec Bellecour, Sepolia Arbitrum, and Arbitrum, with the flexibility to add support for any EVM-compatible chain.

The script also converts fees into **USD** and, when analyzing non Arbitrum transaction, **estimates what the fees would cost on Arbitrum**.

More details:

https://docs.arbitrum.io/how-arbitrum-works/gas-fees#parent-chain-gas-pricing
https://medium.com/offchainlabs/understanding-arbitrum-2-dimensional-fees-fd1d582596c9

---

## **Features**
- Fetch transaction details from **Arbitrum Sepolia**, **Arbitrum** or **iExec Bellecour**.
- Calculate **L2 gas fees** from `gasUsed` and `gasPrice`.
- Estimate **L1 gas usage** based on calldata size and estimate L1 fees.
- Convert **L1 and L2 fees to USD** using the live ETH price from CoinGecko.
- Provides a **cost estimation as if the transaction were on Arbitrum** (for transaction not coming from Arbitrum)

---

## **1. Requirements**
- **Python 3.8+**
- **pip** (Python package manager)

- Use RPC queries and price data.

---

## **2. Installation**

### **Create a virtual environment (macOS)**
```bash
python3 -m venv env
```

### **Activate the virtual environment**
```bash
source env/bin/activate
```

###  Uninstall
Reminder: when you're done with the tool, deactivate the virtual environment:
```bash
deactivate
```

### **Install dependencies**
```bash
pip install -r requirements.txt
```

## **3. Usage**
```bash
python get_tx_fee_estimation.py TX_HASH NETWORK
```

 - TX_HASH : The hash of the transaction to analyze (e.g., 0x123abc...).
 - NETWORK : arbitrum or bellecour. If omitted, bellecour is the default.


### **Examples**

Analyze a Bellecour transaction:

```bash
python get_tx_fee_estimation.py 0x123abc... bellecour
```
Analyze an Arbitrum transaction:

```bash
python get_tx_fee_estimation.py 0x123abc... arbitrum
```
Tips: Useful to compare fee estimation with real Arbitrum fee. [https://arbiscan.io/](https://arbiscan.io/)

## **4. Example Output**

=== Transaction on BELLECOUR ===
  - Hash              : 0x123abc...

--- L2 ---
  - Gas Used (L2)     : 526432
  - Gas Price (L2)    : 0.10 gwei
  - L2 Fee            : 0.00005264 ETH ($0.19)

--- L1 (estimated) ---
  - Gas Used (L1)     : 1842
  - Gas Price (L1)    : 8.00 gwei
  - L1 Fee            : 0.00001474 ETH ($0.05)

=== TOTAL ===
  - TOTAL (L1+L2)     : 0.00006738 ETH ($0.24)

=== COST IF ON ARBITRUM ===
  - Gas Price (L2) Arb: 0.25 gwei
  - L2 Fee (Arbitrum) : 0.00013161 ETH ($0.48)
  - L1 Fee (Arbitrum) : 0.00001474 ETH ($0.05)
  - TOTAL (Arbitrum)  : 0.00014635 ETH ($0.53)


