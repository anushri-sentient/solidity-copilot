# 🔗 Solidity Copilot

A Streamlit-based AI copilot for Solidity development, powered by Firework GPT OSS 120B.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp env_example.txt .env
   # Edit .env and add your Firework API key
   ```

3. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## Configuration

Set your Firework API key in `.env`:
```
FIREWORKS_API_KEY=your_actual_api_key_here
```

## Features

- 🤖 **AI-Powered**: Uses Firework GPT OSS 120B for intelligent Solidity help
- 🔄 **Three-Call Architecture**: Generate → Improve → Analyze Assumptions
- 🚀 **Quick Start Buttons**: 6 common contract types (Registry, Staking, Vault, Marketplace, Escrow, Rewards)
- 💬 **Interactive Chat**: Clean, responsive chat interface with flow visualization
- 🔒 **Expert Review**: Senior Solidity developer improves code quality
- 🔍 **Assumptions Transparency**: See what assumptions were made in the final code
- ⚡ **Gas Optimization**: Tips and techniques for optimizing gas usage
- 📚 **Expert Knowledge**: Comprehensive Solidity development guidance
- 🎨 **Modern UI**: Beautiful, responsive design with syntax highlighting

## Project Structure

```
solidity-copilot/
├── app.py              # Main Streamlit application
├── prompts.py          # Expert system prompts
├── requirements.txt    # Python dependencies
├── env_example.txt     # Environment variables template
└── README.md          # Documentation
```

## Example Questions

### 🏗️ Smart Contract Development
- "Write a secure ERC20 token with minting, burning, and access control"
- "Create a Merkle tree airdrop distributor with OpenZeppelin compatibility"
- "Build a staking contract with reward distribution and emergency pause"
- "Implement a DEX with liquidity pools and automated market making"

### 🔒 Security & Architecture
- "Design a multi-signature treasury with role-based permissions"
- "Create an upgradeable proxy contract with initialization patterns"
- "Build a DeFi lending protocol with collateral management"
- "Implement a gas-optimized NFT marketplace with royalty support"

### ⚡ Advanced Topics
- "How to implement gas-efficient Merkle proof verification?"
- "What are the best practices for Foundry testing?"
- "How to optimize storage patterns for gas efficiency?"
- "How to implement secure cross-contract token transfers?"

## Expert Features

The copilot includes comprehensive expertise in:

- **Smart Contract Development**: ERC20, ERC721, ERC1155, DeFi protocols
- **Security Best Practices**: Reentrancy protection, access control, vulnerability prevention
- **Gas Optimization**: Storage vs memory, efficient patterns, cost reduction
- **Testing Strategies**: Foundry integration, comprehensive test coverage
- **Advanced Patterns**: Merkle trees, airdrops, upgradeable contracts
- **OpenZeppelin Integration**: Proper usage of battle-tested libraries

## Logging

The app includes detailed logging to help with debugging:
- API request/response logging
- Error tracking and diagnostics
- Performance monitoring

Check the terminal where you run `streamlit run app.py` to see detailed logs.

The app will be available at `http://localhost:8501`