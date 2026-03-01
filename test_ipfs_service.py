"""
测试 Pinata IPFS 服务
Test Pinata IPFS Service
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.ipfs_service import PinataIPFSService
from src.config import PINATA_API_KEY, PINATA_SECRET_KEY


def main():
    print("=" * 60)
    print("🔗 Testing Pinata IPFS Service")
    print("=" * 60)
    
    # 创建服务实例
    ipfs_service = PinataIPFSService(
        api_key=PINATA_API_KEY,
        secret_key=PINATA_SECRET_KEY
    )
    
    # 测试认证
    print("\n1️⃣ Testing Authentication...")
    if ipfs_service.test_authentication():
        print("   ✅ Authentication successful!")
    else:
        print("   ❌ Authentication failed!")
        return
    
    # 测试上传 JSON
    print("\n2️⃣ Testing JSON Upload...")
    test_data = {
        "test": "BeWithMe IPFS Test",
        "timestamp": "2024-01-01",
        "description": "This is a test upload to IPFS via Pinata"
    }
    
    result = ipfs_service.upload_json(
        json_data=test_data,
        pin_name="bewithme_test_json"
    )
    
    if result:
        print(f"   ✅ JSON uploaded successfully!")
        print(f"   IPFS Hash: {result.get('IpfsHash')}")
        print(f"   Gateway URL: {ipfs_service.get_gateway_url(result.get('IpfsHash'))}")
    else:
        print("   ❌ JSON upload failed!")
    
    # 获取已固定文件列表
    print("\n3️⃣ Getting Pinned Files List...")
    pinned_files = ipfs_service.get_pinned_files(limit=5)
    
    if pinned_files:
        rows = pinned_files.get('rows', [])
        print(f"   ✅ Found {len(rows)} pinned files (showing max 5):")
        for idx, file in enumerate(rows[:5], 1):
            print(f"   {idx}. {file.get('ipfs_pin_hash')} - {file.get('metadata', {}).get('name', 'Unnamed')}")
    else:
        print("   ❌ Failed to get pinned files!")
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
