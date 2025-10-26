# X402 Mint Tools

## ⚠️ Important Notice
**Submit code to AI for security review before use! Test with new wallets first!**

## 🛠 Tools Overview

### 1. `x402_mint.py` - Main Tool
Automated X402 protocol mint operations with multi-wallet batch processing

### 2. `generate_tmp_private_key.py` - Wallet Generator
Generate test wallet private keys and addresses

### 3. `x402_monitor.py` - Monitor Tool (TODO)
Monitor X402 resource status (under development)

## 📦 Install Dependencies
```bash
pip install web3 eth-account requests loguru mnemonic
```

## 🚀 Quick Start

### 1. Generate Test Wallets
```bash
python generate_tmp_private_key.py
```

### 2. Configure Parameters (edit x402_mint.py)
```python
TRY_TO_MINT_NUM = 100                                      # mint attempts
SINGLE_MINT_AMOUNT = 1                                     # amount per mint (USDC)
TO_ADDRESS = "Target Wallet Address"   # recipient address
MINT_ENDPOINT = "https://api.ping.observer/mint-v3"        # API endpoint
PRIVATE_KEY_LIST = ["your_private_key"]                    # private key list
```

### 3. Run
```bash
python x402_mint.py
```

## 🔧 Configuration Details

### Required Parameters
- `TRY_TO_MINT_NUM`: Number of mint attempts per wallet
- `SINGLE_MINT_AMOUNT`: USDC amount per mint operation
- `TO_ADDRESS`: Target recipient address (get from x402scan)
- `MINT_ENDPOINT`: API endpoint URL (get from x402scan)
- `PRIVATE_KEY_LIST`: List of private keys for your wallets

### Security Best Practices
1. **Never expose private keys** in public repositories
2. **Use test wallets first** before production use
3. **Start with small amounts** to verify functionality
4. **Review all code** with AI before execution
5. **Monitor transaction logs** for any issues

## 📋 TODO
- [ ] Complete X402 resource monitoring functionality
- [ ] Add support for more chains
- [ ] Improve error handling and retry mechanisms
- [ ] Add transaction status tracking
- [ ] Implement configuration file support