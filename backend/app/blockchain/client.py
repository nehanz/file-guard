"""
Blockchain client for interacting with FileIntegrity smart contract via web3.py.
"""
import json
import logging
from pathlib import Path
from typing import Tuple, Optional

from web3 import AsyncWeb3
from web3.exceptions import ContractLogicError
from eth_account import Account

from app.core.config import settings

logger = logging.getLogger(__name__)


class BlockchainClient:
    """
    Async blockchain client for FileIntegrity contract operations.
    Connects to local Anvil node for file hash anchoring and verification.
    """

    def __init__(self):
        """Initialize web3 connection and load contract ABI."""
        self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(settings.WEB3_PROVIDER_URI))

        # Load account from private key
        if not settings.ETH_PRIVATE_KEY:
            raise ValueError("ETH_PRIVATE_KEY not configured in settings")

        self.account = Account.from_key(settings.ETH_PRIVATE_KEY)

        # Load contract ABI
        abi_path = Path(__file__).parent / "contract_abi.json"
        with open(abi_path, "r") as f:
            contract_abi = json.load(f)

        # Initialize contract instance
        if not settings.CONTRACT_ADDRESS:
            raise ValueError("CONTRACT_ADDRESS not configured in settings")

        self.contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(settings.CONTRACT_ADDRESS),
            abi=contract_abi
        )

        logger.info(f"BlockchainClient initialized with contract at {settings.CONTRACT_ADDRESS}")

    async def is_connected(self) -> bool:
        """Check if connected to blockchain node."""
        try:
            await self.w3.eth.block_number
            return True
        except Exception as e:
            logger.error(f"Blockchain connection failed: {e}")
            return False

    async def store_hash_on_chain(self, file_id: str, sha256_hash: str) -> str:
        """
        Anchor file SHA-256 hash to blockchain.

        Args:
            file_id: Unique file identifier (MongoDB ObjectId as string)
            sha256_hash: Hexadecimal SHA-256 hash of file content (64 chars)

        Returns:
            Transaction hash as hex string

        Raises:
            ContractLogicError: If file hash already exists or validation fails
        """
        try:
            # Get current nonce for account
            nonce = await self.w3.eth.get_transaction_count(self.account.address)

            # Build transaction
            tx = await self.contract.functions.storeHash(
                file_id,
                sha256_hash
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': await self.w3.eth.gas_price
            })

            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, settings.ETH_PRIVATE_KEY)

            # Send transaction
            tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            # Wait for transaction receipt
            receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)

            tx_hash_hex = receipt.transactionHash.hex()
            logger.info(f"Hash anchored for file {file_id}: tx={tx_hash_hex}")

            return tx_hash_hex

        except ContractLogicError as e:
            logger.error(f"Contract error storing hash for {file_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error storing hash for {file_id}: {e}")
            raise

    async def get_hash_from_chain(self, file_id: str) -> Tuple[str, int, str]:
        """
        Retrieve file hash record from blockchain.

        Args:
            file_id: Unique file identifier

        Returns:
            Tuple of (sha256_hash, timestamp, owner_address)

        Raises:
            ContractLogicError: If file record not found
        """
        try:
            result = await self.contract.functions.getHash(file_id).call()
            sha256_hash, timestamp, owner = result

            logger.info(f"Retrieved hash for file {file_id} from blockchain")
            return sha256_hash, timestamp, owner

        except ContractLogicError as e:
            logger.error(f"File record not found on blockchain: {file_id}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving hash for {file_id}: {e}")
            raise

    async def verify_hash_on_chain(self, file_id: str, sha256_hash: str) -> bool:
        """
        Verify if provided hash matches blockchain record.

        Args:
            file_id: Unique file identifier
            sha256_hash: Hash to verify

        Returns:
            True if hashes match, False otherwise

        Raises:
            ContractLogicError: If file record not found
        """
        try:
            # Get current nonce
            nonce = await self.w3.eth.get_transaction_count(self.account.address)

            # Build transaction (verifyHash emits event)
            tx = await self.contract.functions.verifyHash(
                file_id,
                sha256_hash
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 100000,
                'gasPrice': await self.w3.eth.gas_price
            })

            # Sign and send
            signed_tx = self.w3.eth.account.sign_transaction(tx, settings.ETH_PRIVATE_KEY)
            tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)

            # Parse return value from receipt
            result = await self.contract.functions.verifyHash(file_id, sha256_hash).call()

            logger.info(f"Verified hash for {file_id}: {result}")
            return result

        except ContractLogicError as e:
            logger.error(f"Verification failed for {file_id}: {e}")
            raise

    async def hash_exists(self, file_id: str) -> bool:
        """
        Check if file hash has been anchored on blockchain.

        Args:
            file_id: Unique file identifier

        Returns:
            True if hash exists, False otherwise
        """
        try:
            exists = await self.contract.functions.exists(file_id).call()
            return exists
        except Exception as e:
            logger.error(f"Error checking existence for {file_id}: {e}")
            return False


# Singleton instance
_blockchain_client: Optional[BlockchainClient] = None


async def get_blockchain_client() -> BlockchainClient:
    """
    Dependency injection function for FastAPI.
    Returns singleton blockchain client instance.
    """
    global _blockchain_client

    if _blockchain_client is None:
        _blockchain_client = BlockchainClient()

        # Verify connection
        if not await _blockchain_client.is_connected():
            raise ConnectionError("Cannot connect to blockchain node at " + settings.WEB3_PROVIDER_URI)

    return _blockchain_client
