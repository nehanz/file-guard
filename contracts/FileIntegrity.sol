// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title FileIntegrity
 * @dev Smart contract for anchoring file SHA-256 hashes on-chain for immutable integrity verification
 */
contract FileIntegrity {
    struct FileRecord {
        string sha256Hash;
        uint256 timestamp;
        address owner;
    }

    // Mapping: fileId => FileRecord
    mapping(string => FileRecord) private records;

    event FileHashAnchored(
        string indexed fileId,
        string sha256Hash,
        address indexed owner,
        uint256 timestamp
    );

    event FileHashVerified(
        string indexed fileId,
        address indexed verifier,
        bool isValid
    );

    /**
     * @dev Store a file hash on the blockchain
     * @param fileId Unique identifier for the file (from database)
     * @param sha256Hash SHA-256 hash of the file content
     */
    function storeHash(string memory fileId, string memory sha256Hash) public {
        require(bytes(fileId).length > 0, "File ID cannot be empty");
        require(bytes(sha256Hash).length == 64, "Invalid SHA-256 hash length");
        require(bytes(records[fileId].sha256Hash).length == 0, "File hash already anchored");

        records[fileId] = FileRecord({
            sha256Hash: sha256Hash,
            timestamp: block.timestamp,
            owner: msg.sender
        });

        emit FileHashAnchored(fileId, sha256Hash, msg.sender, block.timestamp);
    }

    /**
     * @dev Retrieve file hash record from blockchain
     * @param fileId Unique identifier for the file
     * @return sha256Hash The stored hash
     * @return timestamp When the hash was anchored
     * @return owner Address that anchored the hash
     */
    function getHash(string memory fileId)
        public
        view
        returns (
            string memory sha256Hash,
            uint256 timestamp,
            address owner
        )
    {
        FileRecord memory rec = records[fileId];
        require(bytes(rec.sha256Hash).length > 0, "File record not found on blockchain");
        return (rec.sha256Hash, rec.timestamp, rec.owner);
    }

    /**
     * @dev Verify if a file hash matches what's stored on-chain
     * @param fileId Unique identifier for the file
     * @param sha256Hash Hash to verify against stored hash
     * @return isValid True if hashes match
     */
    function verifyHash(string memory fileId, string memory sha256Hash)
        public
        returns (bool isValid)
    {
        FileRecord memory rec = records[fileId];
        require(bytes(rec.sha256Hash).length > 0, "File record not found on blockchain");

        isValid = keccak256(bytes(rec.sha256Hash)) == keccak256(bytes(sha256Hash));

        emit FileHashVerified(fileId, msg.sender, isValid);
        return isValid;
    }

    /**
     * @dev Check if a file hash exists on-chain
     * @param fileId Unique identifier for the file
     * @return exists True if the file has been anchored
     */
    function exists(string memory fileId) public view returns (bool) {
        return bytes(records[fileId].sha256Hash).length > 0;
    }
}
