# File Guard

Blockchain-based file integrity verification system using **Solidity → Foundry → Anvil → web3.py → FastAPI**.

## Overview

File Guard allows users to securely upload files and anchor their SHA-256 hashes on the blockchain for tamper-proof verification. Each file's hash is stored immutably on-chain, providing cryptographic proof of file integrity.

## Features

- **Secure File Upload** - Streaming upload with SHA-256 hash calculation
- **Blockchain Anchoring** - Automatic hash storage on Ethereum-compatible blockchain
- **Integrity Verification** - Compare current file hash with on-chain record
- **User Authentication** - JWT-based auth with refresh tokens
- **Activity Logging** - Track all file operations and blockchain transactions
- **RESTful API** - Complete FastAPI backend with OpenAPI documentation

## Technology Stack

### Backend
- **FastAPI** 0.111.0 - Modern async Python web framework
- **MongoDB** - Document database for file metadata
- **web3.py** 7.3.0 - Async Ethereum client
- **Pydantic** - Data validation and settings management

### Blockchain
- **Solidity** 0.8.20 - Smart contract language
- **Foundry** - Fast Ethereum development toolkit
- **Anvil** - Local Ethereum node for development
- **FileIntegrity.sol** - Custom smart contract for hash anchoring

### Development Tools
- **Poetry/pip** - Python dependency management
- **pytest** - Testing framework
- **Docker** - Containerization (optional)

## Project Structure

```
file-guard/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── blockchain/  # web3.py integration
│   │   ├── core/        # Config, security, logging
│   │   ├── models/      # MongoDB models
│   │   ├── services/    # Business logic
│   │   └── main.py
│   └── tests/
│       ├── unit/        # Unit tests
│       └── integration/ # Integration tests
├── contracts/           # Smart contracts
│   ├── src/            # Solidity source
│   ├── test/           # Contract tests
│   └── script/         # Deploy scripts
├── docs/               # Documentation
├── scripts/            # Utility scripts
│   └── blockchain/     # Blockchain operations
└── foundry.toml        # Foundry configuration
```

## Quick Start

### Prerequisites

```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Install Python dependencies
cd backend
pip install -r requirements.txt
```

### Setup

1. **Start MongoDB**
```bash
mongod
```

2. **Start Anvil (Local Blockchain)**
```bash
anvil
```

3. **Deploy Smart Contract**
```bash
# Copy a private key from Anvil output
export DEPLOY_PRIVATE_KEY=0xYourPrivateKeyFromAnvil
./scripts/blockchain/deploy_contract.sh
```

4. **Configure Backend**
```bash
cd backend
cp .env.example .env
# Edit .env and add blockchain settings from deployment output
```

5. **Start Backend**
```bash
uvicorn app.main:app --reload
```

6. **Access API Documentation**
```
http://localhost:8000/api/v1/docs
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token

### Files
- `POST /api/v1/files/upload` - Upload file (automatically anchors hash)
- `GET /api/v1/files` - List user's files
- `GET /api/v1/files/{id}` - Get file details
- `POST /api/v1/files/{id}/verify` - Verify file integrity
- `DELETE /api/v1/files/{id}` - Delete file

### Users
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update user profile

### System
- `GET /api/v1/health` - Health check

## How It Works

### File Upload Flow
```
1. User uploads file via API
2. Backend streams file to disk while calculating SHA-256
3. File metadata saved to MongoDB
4. Hash automatically anchored on blockchain via web3.py
5. Transaction hash stored in file metadata
6. User receives file record with blockchain confirmation
```

### Verification Flow
```
1. User requests verification for a file
2. Backend recalculates current file hash
3. Compares with database hash (DB integrity check)
4. Fetches original hash from blockchain
5. Compares current hash with on-chain hash
6. Returns verification result with blockchain details
```

## Documentation

Complete documentation available in `docs/`:

- [BLOCKCHAIN_SETUP.md](docs/BLOCKCHAIN_SETUP.md) - Detailed blockchain setup guide
- [PROJECT_STRUCTURE_PROPOSAL.md](docs/PROJECT_STRUCTURE_PROPOSAL.md) - Architecture and structure
- [Backend README](backend/README.md) - Backend documentation (if exists)
- [Contracts README](contracts/README.md) - Smart contract documentation

## Testing

```bash
# Run all tests
pytest backend/tests/

# Run unit tests only
pytest backend/tests/unit/

# Run integration tests
pytest backend/tests/integration/

# Run with coverage
pytest backend/tests/ --cov=app --cov-report=html

# Test smart contracts (when written)
forge test
```

## Security Notes

### Development (Current Setup)
- Uses Anvil's deterministic test accounts
- Private keys are publicly known - **NEVER use in production**
- Local blockchain resets on restart
- Perfect for development and testing

### Production Considerations
- Generate secure private keys: `cast wallet new`
- Use environment-specific key management (AWS Secrets Manager, Vault)
- Deploy to testnet (Sepolia) or mainnet
- Never commit `.env` files to version control
- Monitor blockchain node health
- Implement gas price strategies

## Environment Variables

Key configuration in `backend/.env`:

```bash
# API
API_V1_STR=/api/v1
AUTH_ENDPOINT=/auth
FILES_ENDPOINT=/files
USERS_ENDPOINT=/users

# Security
SECRET_KEY=your_secret_key_here

# Database
DATABASE_URL=mongodb://localhost:27017
DATABASE_NAME=file_guard

# Blockchain
WEB3_PROVIDER_URI=http://127.0.0.1:8545
ETH_PRIVATE_KEY=your_private_key_here
CONTRACT_ADDRESS=deployed_contract_address
```

See `backend/.env.example` for complete configuration.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Run tests and ensure they pass
6. Submit a pull request

## Development Roadmap

- [x] Smart contract implementation
- [x] Backend API with authentication
- [x] Blockchain integration (web3.py)
- [x] File upload and verification
- [x] Documentation
- [ ] Frontend implementation (React/Next.js)
- [ ] IPFS integration for decentralized storage
- [ ] Multi-chain support (Polygon, Arbitrum)
- [ ] Batch hash anchoring
- [ ] Admin dashboard

## License

[Add your license here]

## Support

For questions or issues:
- Check the [documentation](docs/)
- Review [BLOCKCHAIN_SETUP.md](docs/BLOCKCHAIN_SETUP.md)
- Open an issue on GitHub

---

**Built with:** Solidity 0.8.20 • Foundry 1.7.1 • web3.py 7.3.0 • FastAPI 0.111.0 • MongoDB
