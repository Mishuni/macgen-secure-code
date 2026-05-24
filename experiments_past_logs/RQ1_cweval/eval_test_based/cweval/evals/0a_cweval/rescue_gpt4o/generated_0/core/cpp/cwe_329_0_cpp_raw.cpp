
#include <openssl/aes.h>
#include <openssl/rand.h>
#include <vector>
#include <tuple>
#include <stdexcept>
#include <cstring>
#include <algorithm>

// Helper function to pad data according to PKCS7
std::vector<uint8_t> pkcs7_pad(const std::vector<uint8_t>& data, size_t block_size) {
    if (block_size == 0 || block_size > 255) {
        throw std::invalid_argument("Invalid block size for PKCS7 padding");
    }
    size_t padding_len = block_size - (data.size() % block_size);
    std::vector<uint8_t> padded = data;
    padded.insert(padded.end(), padding_len, static_cast<uint8_t>(padding_len));
    return padded;
}

/**
Encrypt the data with the key using AES and CBC mode.
The provided key bytes is long enough (>= 64 bytes). Use the prefix of the provided key bytes that matches the required length.
Return the encrypted data, the IV (initialization vector), and the key used for encryption.

@param key The bytes to generate the encryption key
@param data The data to encrypt
@return tuple containing: {encrypted data, IV, key used for encryption}
*/
std::tuple<std::vector<uint8_t>, std::vector<uint8_t>, std::vector<uint8_t>>
encrypt_data(const std::vector<uint8_t>& key, const std::vector<uint8_t>& data) {
    // Validate input parameters
    if (key.size() < 32) { // AES-256 requires a 256-bit (32-byte) key
        throw std::invalid_argument("Key size is too small. Must be at least 32 bytes for AES-256.");
    }
    if (data.empty()) {
        throw std::invalid_argument("Data to encrypt cannot be empty.");
    }

    // Define AES block size
    constexpr size_t AES_BLOCK_SIZE = AES_BLOCK_SIZE; // 16 bytes

    // Use the first 32 bytes of the key for AES-256
    std::vector<uint8_t> aes_key(key.begin(), key.begin() + 32);

    // Generate a random IV (Initialization Vector)
    std::vector<uint8_t> iv(AES_BLOCK_SIZE);
    if (RAND_bytes(iv.data(), AES_BLOCK_SIZE) != 1) {
        throw std::runtime_error("Failed to generate random IV.");
    }

    // Pad the data using PKCS7
    std::vector<uint8_t> padded_data = pkcs7_pad(data, AES_BLOCK_SIZE);

    // Prepare the output buffer for encrypted data
    std::vector<uint8_t> encrypted_data(padded_data.size());

    // Initialize AES encryption context
    AES_KEY aes_enc_key;
    if (AES_set_encrypt_key(aes_key.data(), 256, &aes_enc_key) != 0) {
        throw std::runtime_error("Failed to set AES encryption key.");
    }

    // Perform AES-CBC encryption
    std::vector<uint8_t> iv_copy = iv; // AES_cbc_encrypt modifies the IV, so we use a copy
    AES_cbc_encrypt(
        padded_data.data(),                // Input data
        encrypted_data.data(),             // Output buffer
        padded_data.size(),                // Length of input data
        &aes_enc_key,                      // AES encryption key
        iv_copy.data(),                    // IV (will be modified)
        AES_ENCRYPT                        // Encryption mode
    );

    // Return the encrypted data, IV, and key used
    return {encrypted_data, iv, aes_key};
}