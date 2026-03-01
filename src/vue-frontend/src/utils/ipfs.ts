/**
 * IPFS 工具函数
 * IPFS Utility Functions
 */

/**
 * 获取 Pinata 网关 URL
 */
export function getPinataGatewayUrl(ipfsHash: string): string {
  return `https://gateway.pinata.cloud/ipfs/${ipfsHash}`;
}

/**
 * 获取公共 IPFS 网关 URL
 */
export function getPublicGatewayUrl(ipfsHash: string, gateway: 'ipfs.io' | 'cloudflare' | 'pinata' = 'pinata'): string {
  const gateways = {
    'ipfs.io': `https://ipfs.io/ipfs/${ipfsHash}`,
    'cloudflare': `https://cloudflare-ipfs.com/ipfs/${ipfsHash}`,
    'pinata': `https://gateway.pinata.cloud/ipfs/${ipfsHash}`
  };
  return gateways[gateway];
}

/**
 * 验证 IPFS CID 格式
 */
export function isValidIPFSHash(hash: string): boolean {
  // CIDv0: 以 Qm 开头，长度 46
  const cidv0Regex = /^Qm[a-zA-Z0-9]{44}$/;
  // CIDv1: 以 b 开头
  const cidv1Regex = /^b[a-z2-7]{58}$/i;
  
  return cidv0Regex.test(hash) || cidv1Regex.test(hash);
}

/**
 * 缩短 IPFS hash 显示
 */
export function shortenIPFSHash(hash: string, startChars: number = 6, endChars: number = 4): string {
  if (!hash || hash.length <= startChars + endChars) {
    return hash;
  }
  return `${hash.substring(0, startChars)}...${hash.substring(hash.length - endChars)}`;
}

/**
 * 复制 IPFS hash 到剪贴板
 */
export async function copyIPFSHash(hash: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(hash);
    return true;
  } catch (error) {
    console.error('Failed to copy IPFS hash:', error);
    return false;
  }
}

/**
 * 获取 IPFS 浏览器 URL (ipfs.io)
 */
export function getIPFSExplorerUrl(ipfsHash: string): string {
  return `https://ipfs.io/ipfs/${ipfsHash}`;
}

/**
 * 下载 IPFS 文件
 */
export function downloadFromIPFS(ipfsHash: string, filename: string = 'file') {
  const url = getPinataGatewayUrl(ipfsHash);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

export default {
  getPinataGatewayUrl,
  getPublicGatewayUrl,
  isValidIPFSHash,
  shortenIPFSHash,
  copyIPFSHash,
  getIPFSExplorerUrl,
  downloadFromIPFS
};
