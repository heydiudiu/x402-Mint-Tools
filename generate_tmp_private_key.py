# pip install web3 eth-account mnemonic
from eth_account import Account
from mnemonic import Mnemonic

Account.enable_unaudited_hdwallet_features()  # 启用HD钱包功能


# 生成钱包数量
wallet_num = 10
mnemo = Mnemonic("english")

for i in range(wallet_num):
    mnemonic_words = mnemo.generate(strength=128)  # 生成12个助记词
    account = Account.from_mnemonic(mnemonic_words)

    print(f"序号{i} 私钥: {account.key.hex()} 地址: {account.address} 助记词: {mnemonic_words}")
