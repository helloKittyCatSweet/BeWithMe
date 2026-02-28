// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title BeWithMe
 * @dev 情感资产去中心化存证合约
 */
contract BeWithMe is Ownable {
    struct Memory {
        string ipfsHash;        // 记忆素材的 IPFS 哈希
        address guardianAddress; // 监护人（用户）地址
        bool isMemoryLocked;    // 记忆是否已锁定
        bool isValidated;       // 是否通过 AI 语义验证
        uint256 createdAt;      // 创建时间
    }

    // 记忆 ID => 记忆详情
    mapping(uint256 => Memory) public memories;
    uint256 public nextMemoryId;

    // 事件系统
    event MemoryMinted(uint256 indexed memoryId, string ipfsHash, address indexed guardian);
    event MemoryValidated(uint256 indexed memoryId);
    event MemoryAwakened(uint256 indexed memoryId, address indexed guardian);
    event MemoryLocked(uint256 indexed memoryId);
    event MemoryUnlocked(uint256 indexed memoryId);

    constructor() Ownable(msg.sender) {}

    /**
     * @dev 将用户上传的 IPFS 哈希上链，铸造一段数字记忆
     * @param _ipfsHash 存储在 IPFS 上的资源哈希
     */
    function mintMemory(string memory _ipfsHash) public returns (uint256) {
        uint256 memoryId = nextMemoryId++;
        
        memories[memoryId] = Memory({
            ipfsHash: _ipfsHash,
            guardianAddress: msg.sender,
            isMemoryLocked: true, // 默认锁定
            isValidated: false,
            createdAt: block.timestamp
        });

        emit MemoryMinted(memoryId, _ipfsHash, msg.sender);
        return memoryId;
    }

    /**
     * @dev 记录用户通过了 AI 语义验证的状态
     * @param _memoryId 记忆 ID
     */
    function validateMemory(uint256 _memoryId) public {
        require(memories[_memoryId].guardianAddress == msg.sender, "Only guardian can validate");
        
        memories[_memoryId].isValidated = true;
        emit MemoryValidated(_memoryId);
        
        // 如果验证通过，自动触发觉醒事件
        if (memories[_memoryId].isMemoryLocked) {
            memories[_memoryId].isMemoryLocked = false;
            emit MemoryAwakened(_memoryId, msg.sender);
        }
    }

    /**
     * @dev 手动锁定记忆
     */
    function lockMemory(uint256 _memoryId) public {
        require(memories[_memoryId].guardianAddress == msg.sender, "Only guardian can lock");
        memories[_memoryId].isMemoryLocked = true;
        emit MemoryLocked(_memoryId);
    }

    /**
     * @dev 手动解锁记忆（通常通过验证后自动解锁，也可以手动）
     */
    function unlockMemory(uint256 _memoryId) public {
        require(memories[_memoryId].guardianAddress == msg.sender, "Only guardian can unlock");
        require(memories[_memoryId].isValidated, "Memory must be validated by AI first");
        
        memories[_memoryId].isMemoryLocked = false;
        emit MemoryAwakened(_memoryId, msg.sender);
    }

    /**
     * @dev 获取记忆详情
     */
    function getMemory(uint256 _memoryId) public view returns (
        string memory ipfsHash,
        address guardianAddress,
        bool isMemoryLocked,
        bool isValidated,
        uint256 createdAt
    ) {
        Memory storage mem = memories[_memoryId];
        return (
            mem.ipfsHash,
            mem.guardianAddress,
            mem.isMemoryLocked,
            mem.isValidated,
            mem.createdAt
        );
    }
}
