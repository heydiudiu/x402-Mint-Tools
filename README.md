# X402 Mint Tools

## 🚀 导航栏 / Navigation
- [中文文档 (Chinese)](README.md)
- [English Documentation](README_EN.md)

## ⚠️ 重要提醒
**使用前请先将代码提交给 AI 审核，确保安全！建议先用新钱包测试！**

## 🛠 工具说明

### 1. `x402_mint.py` - 主要工具
自动化 X402 协议 mint 操作，支持多钱包批量处理

### 2. `generate_tmp_private_key.py` - 钱包生成器
生成测试钱包私钥和地址

### 3. `x402_monitor.py` - 监控工具 (TODO)
监控 X402 资源状态 (待开发)

## 📦 安装依赖
```bash
pip install web3 eth-account requests loguru mnemonic
```

## 🚀 快速开始

### 1. 生成测试钱包
```bash
python generate_tmp_private_key.py
```

### 2. 配置参数 (编辑 x402_mint.py)
```python
TRY_TO_MINT_NUM = 100                                      # mint 次数
SINGLE_MINT_AMOUNT = 1                                     # 每次金额 (USDC)
TO_ADDRESS = "Target Wallet Address"   # 收款地址
MINT_ENDPOINT = "https://api.ping.observer/mint-v3"        # API 接口
PRIVATE_KEY_LIST = ["your_private_key"]                    # 私钥列表
```

### 3. 运行
```bash
python x402_mint.py
```

## 📋 TODO
- [ ] 完善 X402 资源监控功能
- [ ] 添加更多链支持
- [ ] 优化错误处理和重试机制