"""
IPFS 上传服务 - 使用 Pinata
IPFS Upload Service using Pinata
"""
import os
import requests
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class PinataIPFSService:
    """Pinata IPFS 上传服务"""
    
    def __init__(self, api_key: str = None, secret_key: str = None):
        """
        初始化 Pinata 服务
        
        Args:
            api_key: Pinata API Key (从环境变量或参数获取)
            secret_key: Pinata Secret API Key (从环境变量或参数获取)
        """
        self.api_key = api_key or os.getenv("PINATA_API_KEY", "")
        self.secret_key = secret_key or os.getenv("PINATA_SECRET_KEY", "")
        self.base_url = "https://api.pinata.cloud"
        
        if not self.api_key or not self.secret_key:
            logger.warning("Pinata API credentials not configured")
    
    def _get_headers(self) -> Dict[str, str]:
        """获取 API 请求头"""
        return {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.secret_key
        }
    
    def test_authentication(self) -> bool:
        """测试 API 认证是否有效"""
        try:
            url = f"{self.base_url}/data/testAuthentication"
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                logger.info("✅ Pinata authentication successful")
                return True
            else:
                logger.error(f"❌ Pinata authentication failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Pinata authentication test error: {e}")
            return False
    
    def upload_file(
        self, 
        file_path: str,
        pin_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        上传文件到 IPFS (通过 Pinata)
        
        Args:
            file_path: 本地文件路径
            pin_name: PIN 名称 (可选)
            metadata: 元数据 (可选)
        
        Returns:
            响应数据包含 IpfsHash, PinSize, Timestamp 等
            示例: {'IpfsHash': 'Qm...', 'PinSize': 12345, 'Timestamp': '2024-...'}
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
        
        try:
            url = f"{self.base_url}/pinning/pinFileToIPFS"
            
            # 准备文件
            with open(file_path, 'rb') as file:
                files = {
                    'file': (os.path.basename(file_path), file)
                }
                
                # 准备 metadata (如果提供)
                pin_metadata = {}
                if pin_name:
                    pin_metadata['name'] = pin_name
                if metadata:
                    pin_metadata['keyvalues'] = metadata
                
                # 准备请求数据
                data = {}
                if pin_metadata:
                    import json
                    data['pinataMetadata'] = json.dumps(pin_metadata)
                
                # 发送请求
                response = requests.post(
                    url,
                    headers=self._get_headers(),
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ipfs_hash = result.get('IpfsHash')
                    logger.info(f"✅ File uploaded to IPFS: {ipfs_hash}")
                    logger.info(f"   Gateway URL: https://gateway.pinata.cloud/ipfs/{ipfs_hash}")
                    return result
                else:
                    logger.error(f"❌ IPFS upload failed: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"IPFS upload error: {e}")
            return None
    
    def upload_json(
        self,
        json_data: Dict[str, Any],
        pin_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        上传 JSON 数据到 IPFS
        
        Args:
            json_data: JSON 数据
            pin_name: PIN 名称 (可选)
        
        Returns:
            响应数据包含 IpfsHash 等
        """
        try:
            url = f"{self.base_url}/pinning/pinJSONToIPFS"
            
            payload = {
                "pinataContent": json_data
            }
            
            if pin_name:
                payload["pinataMetadata"] = {
                    "name": pin_name
                }
            
            response = requests.post(
                url,
                headers={**self._get_headers(), "Content-Type": "application/json"},
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                ipfs_hash = result.get('IpfsHash')
                logger.info(f"✅ JSON uploaded to IPFS: {ipfs_hash}")
                return result
            else:
                logger.error(f"❌ JSON upload failed: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"JSON upload error: {e}")
            return None
    
    def get_pinned_files(self, limit: int = 10) -> Optional[Dict[str, Any]]:
        """获取已固定的文件列表"""
        try:
            url = f"{self.base_url}/data/pinList"
            params = {"pageLimit": limit}
            
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get pinned files: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Get pinned files error: {e}")
            return None
    
    def unpin_file(self, ipfs_hash: str) -> bool:
        """从 Pinata 取消固定文件"""
        try:
            url = f"{self.base_url}/pinning/unpin/{ipfs_hash}"
            
            response = requests.delete(
                url,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                logger.info(f"✅ File unpinned: {ipfs_hash}")
                return True
            else:
                logger.error(f"❌ Unpin failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Unpin error: {e}")
            return False
    
    @staticmethod
    def get_gateway_url(ipfs_hash: str) -> str:
        """获取 IPFS 网关 URL"""
        return f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"


# 全局实例
_pinata_service = None


def get_ipfs_service() -> PinataIPFSService:
    """获取全局 IPFS 服务实例"""
    global _pinata_service
    if _pinata_service is None:
        _pinata_service = PinataIPFSService()
    return _pinata_service
