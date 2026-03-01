# Blockchain Integration - Quick Start Guide

## What's New

The BeWithMe system now includes complete blockchain integration for saving voice clones, family relationships, and digital agents on-chain. This guide helps you test the implementation.

## Features Added

### 1. Voice Clone to Blockchain ✅
- Clone a voice in VoiceClone component
- Once cloned, "🔗 Save to Blockchain" button appears (requires wallet connection)
- Click to save voice metadata to blockchain
- Transaction hash displayed on success

### 2. Family Relationship NFT ✅
- Register and verify family relationship
- "🔗 Save to Blockchain" button available after verification
- Mint as NFT on blockchain
- Relationship data immutable on-chain

### 3. Digital Agent to Blockchain ✅
- Create digital agent with personality and memories
- "🔗 Save to Blockchain" button available after creation
- Save agent configuration to blockchain
- Transaction hash confirmed

### 4. User Profile & Blockchain Status ✅
- Access UserProfile component
- Connect MetaMask wallet
- View blockchain status and contract information
- Check wallet balance
- Manage API credentials

## Testing Steps

### Prerequisites
1. **MetaMask Installed**: [Download MetaMask](https://metamask.io/)
2. **Test Network**: Configure MetaMask for a test network (Sepolia recommended)
3. **Test ETH**: Get test ETH from faucet for gas fees
4. **Backend Running**: Start backend server

### Step 1: Start the Application
```bash
cd /home/kitty/BeWithMe

# Terminal 1: Backend
python -m src.api.main

# Terminal 2: Frontend
cd src/vue-frontend
npm install
npm run dev
```

### Step 2: Connect Wallet
1. Open application in browser (usually http://localhost:5173)
2. Navigate to UserProfile component
3. Click "Connect MetaMask"
4. Approve connection in MetaMask popup
5. Confirm wallet address shows in profile

### Step 3: Clone Voice and Save to Blockchain
1. Go to VoiceClone component
2. Select verified family relationship
3. Name the voice (e.g., "Grandma's Voice")
4. Upload sample audio (30 seconds, MP3 or WAV)
5. Click "Clone Voice" and wait for completion
6. Once cloned, "🔗 Save to Blockchain" button appears
7. Click the button
8. MetaMask popup appears requesting transaction signature
9. Confirm the transaction
10. Success message shows with transaction hash

### Step 4: Verify on Block Explorer
1. Copy transaction hash from success message
2. Go to [Sepolia Etherscan](https://sepolia.etherscan.io/) or equivalent
3. Paste transaction hash in search
4. Verify transaction is "Success" (usually takes 1-2 minutes)
5. View contract interaction details

### Step 5: Test Relationship Minting
1. Go to FamilyVerification component
2. Register a new relationship
3. Wait for admin verification (in dev, may auto-verify)
4. Click "🔗 Save to Blockchain"
5. Approve MetaMask transaction
6. Verify on block explorer

### Step 6: Test Agent Creation
1. Go to AgentCreation component
2. Fill in agent details (name, personality, memories)
3. Click "Create Agent"
4. Once created, "🔗 Save to Blockchain" button appears
5. Click to save agent configuration
6. Approve in MetaMask
7. Check transaction hash confirmation

### Step 7: Check Block Chain Memories
1. Navigate to any blockchain endpoint: `/blockchain/memories/{wallet_address}`
2. Example: `/blockchain/memories/0xYourWalletAddress`
3. Should return list of saved memories from blockchain

## Expected Responses

### Successful Voice Clone Save
```json
{
  "success": true,
  "message": "音色已成功保存到区块链",
  "tx_hash": "0x1234567890abcdef...",
  "ipfs_hash": "QmAbcDef123..."
}
```

### Successful Relationship Save
```json
{
  "success": true,
  "message": "关系已成功保存到区块链",
  "tx_hash": "0x1234567890abcdef...",
  "ipfs_hash": "QmAbcDef123..."
}
```

### Successful Agent Save
```json
{
  "success": true,
  "message": "代理已成功保存到区块链",
  "tx_hash": "0x1234567890abcdef...",
  "ipfs_hash": "QmAbcDef123..."
}
```

## Common Issues & Solutions

### "Connect wallet first"
- **Cause**: Wallet not connected
- **Solution**: Click "Connect MetaMask" in UserProfile component

### Transaction pending for too long
- **Cause**: Network congestion or low gas price
- **Solution**: Wait 2-3 minutes, or check gas price and retry

### "Invalid wallet address"
- **Cause**: Incorrect wallet format
- **Solution**: Ensure MetaMask is properly connected, wallet should start with "0x"

### IPFS hash not uploading
- **Cause**: IPFS service not configured
- **Solution**: For now, using mock hashes is fine for testing

### Database field not found error
- **Cause**: Database migration not applied
- **Solution**: Run migration:
```bash
alembic upgrade head
```

## API Testing with curl

### Test Voice Save
```bash
curl -X POST http://localhost:8000/voice/save-to-blockchain \
  -H "Content-Type: application/json" \
  -d '{
    "voice_id": "test_voice_123",
    "voice_name": "Test Voice",
    "ipfs_hash": "QmTest123",
    "user_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f42bE5"
  }'
```

### Test Relationship Save
```bash
curl -X POST http://localhost:8000/relationships/save-to-blockchain \
  -H "Content-Type: application/json" \
  -d '{
    "relationship_id": 1,
    "ipfs_hash": "QmRelation123",
    "user_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f42bE5"
  }'
```

### Test Agent Save
```bash
curl -X POST http://localhost:8000/conversation/save-agent-to-blockchain \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "Digital Grandma",
    "ipfs_hash": "QmAgent123",
    "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f42bE5"
  }'
```

### Get Blockchain Memories
```bash
curl http://localhost:8000/blockchain/memories/0x742d35Cc6634C0532925a3b844Bc9e7595f42bE5
```

### Check Wallet Balance
```bash
curl http://localhost:8000/blockchain/balance/0x742d35Cc6634C0532925a3b844Bc9e7595f42bE5
```

## Development Notes

### Mock Implementation
- IPFS hashes are currently mocked (QmTest123, etc.)
- Real IPFS integration coming in next phase
- Smart contract interactions are ready for real deployment

### Next Steps for Production
1. Deploy smart contract to mainnet
2. Integrate real IPFS service (Pinata/Infura)
3. Apply database migrations
4. Update contract address in frontend
5. Set up monitoring and alerts
6. Security audit of smart contract

## Files to Review

- Frontend components: `src/vue-frontend/src/components/`
  - AgentCreation.vue
  - VoiceClone.vue
  - FamilyVerification.vue
  - UserProfile.vue

- Backend routes: `src/api/routes/`
  - voice.py
  - relationships.py
  - conversation.py
  - blockchain.py (NEW)

- Database: `src/database/crud/agent_profile.py` (NEW)

## Support

For issues or questions:
1. Check BLOCKCHAIN_INTEGRATION.md for architecture details
2. Review BLOCKCHAIN_DEPLOYMENT.md for deployment guide
3. Check console logs in browser (F12 Developer Tools)
4. Check backend logs in terminal

---

**Happy testing! 🚀**
