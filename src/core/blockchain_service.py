"""
区块链服务 - 保存通话记录到以太坊区块链
Blockchain Service - Save call records to Ethereum
"""
import logging
import json
import os
from typing import Optional, Dict
from datetime import datetime

try:
    from web3 import Web3
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False

logger = logging.getLogger(__name__)


class BlockchainService:
    """以太坊区块链服务"""
    
    def __init__(self):
        """初始化区块链连接"""
        if not WEB3_AVAILABLE:
            logger.warning("⚠️ Web3.py 未安装，区块链功能不可用")
            self.available = False
            return
        
        # 从环境变量读取配置
        rpc_url = os.getenv("ETHEREUM_RPC_URL", "https://rpc.sepolia.org")
        contract_address = os.getenv("BLOCKCHAIN_CONTRACT_ADDRESS", "")
        private_key = os.getenv("BLOCKCHAIN_PRIVATE_KEY", "")
        
        if not contract_address or not private_key:
            logger.warning("⚠️ 未配置区块链合约地址或私钥，区块链功能不可用")
            self.available = False
            return
        
        try:
            self.web3 = Web3(Web3.HTTPProvider(rpc_url))
            
            if not self.web3.is_connected():
                logger.error("❌ 无法连接到以太坊节点")
                self.available = False
                return
            
            self.contract_address = contract_address
            self.private_key = private_key
            self.account = self.web3.eth.account.from_key(private_key)
            
            logger.info(f"✅ 区块链连接成功")
            logger.info(f"🔐 账户地址: {self.account.address}")
            logger.info(f"🌐 网络: {rpc_url}")
            self.available = True
            
        except Exception as e:
            logger.error(f"❌ 区块链初始化失败: {str(e)}")
            self.available = False
    
    def save_call_record(
        self,
        user_address: str,
        agent_name: str,
        ipfs_hash: str,
        duration_seconds: int,
        user_text: str = "",
        agent_response: str = ""
    ) -> Optional[Dict]:
        """
        保存通话记录到区块链
        
        Args:
            user_address: 用户的钱包地址
            agent_name: 代理名称
            ipfs_hash: IPFS哈希（指向通话数据）
            duration_seconds: 通话时长（秒）
            user_text: 用户说的话
            agent_response: 代理的回复
        
        Returns:
            包含交易哈希的字典，如果失败返回None
        """
        if not self.available:
            logger.warning("⚠️ 区块链服务不可用")
            return None
        
        try:
            # 构建简单的调用数据
            # 实际项目中应该有合约ABI和encode函数调用
            # 这里简化为直接记录到区块链
            
            call_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_address": user_address,
                "agent_name": agent_name,
                "ipfs_hash": ipfs_hash,
                "duration_seconds": duration_seconds,
                "user_text": user_text[:200],  # 限制长度
                "agent_response": agent_response[:200]
            }
            
            # 将数据编码为字节
            data_json = json.dumps(call_data)
            data_bytes = data_json.encode('utf-8')
            
            logger.info(f"📦 准备区块链交易")
            logger.info(f"💾 数据: {call_data}")
            
            # 构建交易
            nonce = self.web3.eth.get_transaction_count(self.account.address)
            
            tx = {
                'from': self.account.address,
                'to': Web3.to_checksum_address(self.contract_address),
                'value': 0,  # 不需要transfer ETH
                'gas': 100000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': nonce,
                'data': Web3.keccak(text=ipfs_hash),  # 简单的数据指纹
            }
            
            # 签署交易
            logger.info("🔏 签署交易...")
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
            
            # 发送交易
            logger.info("📤 发送交易到区块链...")
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash_str = tx_hash.hex()
            
            logger.info(f"✅ 交易已发送")
            logger.info(f"🔗 交易哈希: {tx_hash_str}")
            
            # 等待交易确认（简化版）
            logger.info("⏳ 等待交易确认...")
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt['status'] == 1:
                logger.info(f"✅ 交易确认成功")
                logger.info(f"📊 Gas使用: {receipt['gasUsed']}")
                
                return {
                    "tx_hash": tx_hash_str,
                    "block_number": receipt['blockNumber'],
                    "status": "success",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"❌ 交易失败")
                return {
                    "tx_hash": tx_hash_str,
                    "status": "failed",
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            logger.error(f"❌ 保存区块链记录失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None


# 全局实例
blockchain_service = None


def get_blockchain_service() -> Optional[BlockchainService]:
    """获取区块链服务实例"""
    global blockchain_service
    if blockchain_service is None:
        blockchain_service = BlockchainService()
    return blockchain_service
