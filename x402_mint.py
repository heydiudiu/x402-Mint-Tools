# pip install web3 eth-account requests loguru
import base64
import json
import os
import re
import threading
import time

import requests
from eth_account import Account
from eth_account.messages import encode_typed_data
from loguru import logger

# 忽略 SSL 警告
requests.packages.urllib3.disable_warnings()


class X402Mint():
    def __init__(self, private_key: str, mint_endpoint: str, to_address: str, amount: int = 1, chain_id: int = 8453, ):
        """

        :param private_key: 私钥
        :param mint_endpoint: 目标接口地址
        :param to_address:  目标收款人地址
        :param amount:      转账金额，默认为1，即 1USDC
        :param chain_id:    链 ID，默认 Base 链 —— 8453
        """
        self.private_key = private_key
        self.mint_endpoint = mint_endpoint
        self.chain_id = chain_id
        self.to_address = to_address
        self.amount = amount
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        self.headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'content-type': 'application/json',
            'x-proxy-target': 'https://api.ping.observer/mint-v3',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        logger.info(f"初始化成功，当前地址: {self.address}")
        # 打印配置信息
        logger.debug("配置信息:\n"
                     f"私钥: {self.private_key}\n"
                     f"收款地址: {self.to_address}\n"
                     f"转账金额: {self.amount} USDC\n"
                     f"链 ID: {self.chain_id}\n"
                     f"当前地址: {self.address}\n"
                     )

    def _log_with_address(self, message: str, level: str = "info"):
        getattr(logger, level)(f"{self.address} ->  {message}")

    def mint(self):
        """

        :param to_address:  目标收款人地址
        :param amount: 转账金额，默认为1，即 1USDC
        :return:
        """

        self._log_with_address("准备签名", level="debug")

        nonce = "0x" + os.urandom(32).hex()  # 随机数，防重放攻击
        current_time = int(time.time())  # 当前时间
        # 签名内容
        typed_data = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"}
                ],
                "TransferWithAuthorization": [
                    {"name": "from", "type": "address"},
                    {"name": "to", "type": "address"},
                    {"name": "value", "type": "uint256"},
                    {"name": "validAfter", "type": "uint256"},
                    {"name": "validBefore", "type": "uint256"},
                    {"name": "nonce", "type": "bytes32"}
                ]
            },
            "primaryType": "TransferWithAuthorization",
            "domain": {
                "name": "USD Coin",
                "version": "2",
                # Base 的chain id 为8453
                # 后续如果有其他链，可自行更换，详细可参考 https://chainlist.org/chain/8453
                "chainId": self.chain_id,
                "verifyingContract": "0x833589fcd6edb6E08f4c7C32D4f71b54bda02913"  # USDC 合约地址
            },
            "message": {
                "from": self.address,  # 自己的地此，即付款人
                "to": self.to_address,
                "value": self.amount * 1000000,  # 转账金额
                "validAfter": current_time,  # 当前时间，即在当前时间之后都有效
                "validBefore": current_time + 900,  # 900s 有效期，即当前时间及900s之后，该签名都有效
                "nonce": nonce
            }
        }

        encoded_data = encode_typed_data(full_message=typed_data)
        # 对消息签名
        signed = self.account.sign_message(encoded_data)

        signature = signed.signature.hex()
        if not signature.startswith('0x'):
            signature = '0x' + signature

        self._log_with_address(f"签名结果: {signature}", level="debug")

        # 构造 X-Payment 请求头原文
        payment_payload = {
            "x402Version": 1,
            "scheme": "exact",
            "network": "base",
            "payload": {
                "signature": signature,
                "authorization": {
                    "from": self.address,
                    "to": self.to_address,
                    "value": str(self.amount * 1000000),  # 这里用字符串
                    "validAfter": str(current_time),
                    "validBefore": str(current_time + 900),
                    "nonce": nonce
                }
            }
        }

        x_payment = base64.b64encode(json.dumps(payment_payload).encode()).decode()
        self._log_with_address(f"X-Payment Header: {x_payment}", level="debug")

        # 提交请求
        headers = self.headers.copy()
        headers['x-payment'] = x_payment

        url = f'https://www.x402scan.com/api/proxy?url={self.mint_endpoint}&share_data=true'
        for _ in range(3):
            try:
                response = requests.get(
                    url=url,
                    headers=headers,
                    verify=False
                )
                break
            except Exception as e:
                self._log_with_address("发送请求异常，1s后准备重试...", level="warning")
                time.sleep(1)
                if _ == 2:
                    self._log_with_address("请求失败，达到最大重试次数，放弃本次请求", level="error")
                    return
        self._log_with_address(f"提交请求成功, 返回状态码: {response.status_code}")
        self._log_with_address(f"请求返回: {response.text}")

        # 尝试解析错误信息
        try:
            if response.json().get("error"):
                self._log_with_address(f"Mint失败, 返回信息: {response.json()['error']}", level="error")
                return
        except:
            pass

        if response.status_code == 200:
            self._log_with_address(f"Mint成功！返回信息: {response.text}", level="success")
            return True

        sleep_time = re.findall('Please wait (.*?) seconds before', response.text)
        if sleep_time:
            try:
                sleep_time = int(sleep_time[0])
                logger.warning(f"[429] - 等待时间: {sleep_time} 秒后重试")
                time.sleep(sleep_time)
            except:
                logger.info(f"mint结果返回: {response.text}")
                return

    def main(self, mint_num: int = 1):
        num = 0
        while num < mint_num:
            num += 1
            try:
                self.mint()
            except Exception as e:
                print(f"请求错误: {e}")
            time.sleep(1)


if __name__ == '__main__':
    # 每个地址尝试 mint 的次数
    TRY_TO_MINT_NUM = 100
    # 每次mint金额，单位 USDC
    SINGLE_MINT_AMOUNT = 1
    # 目标收款地址（项目方地址），从 x402scan 获取
    TO_ADDRESS = "Target Wallet Address"
    # 目标 mint 接口地址，从 x402scan 获取
    MINT_ENDPOINT = "https://api.ping.observer/mint-v3"  # 请从 x402scan 获取最新的接口地址，这儿以 Ping 为例

    # 私钥列表
    PRIVATE_KEY_LIST = [
        "57cd166f4134c9b674a59082a25fdbe6efca30b17f178b5f01ba2e20b45d9e9a",  # 你的私钥1
        # "private_key_2",  # 你的私钥2
        # "private_key_3",  # 你的私钥3
    ]
    for n, pk in enumerate(PRIVATE_KEY_LIST):
        threading.Thread(target=X402Mint(private_key=pk, mint_endpoint=MINT_ENDPOINT, to_address=TO_ADDRESS.lower(),
                                         amount=SINGLE_MINT_AMOUNT).main,
                         args=(TRY_TO_MINT_NUM,)).start()
        print(f"mint线程已启动 -> 编号: {n}")
