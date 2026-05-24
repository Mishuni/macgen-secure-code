
#include <openssl/aes.h>
#include <openssl/rand.h>
#include <vector>
#include <stdexcept>

// Function to pad data to AES block size
std::vector<unsigned char> pad_data(const std::vector<unsigned char>& data) {
    size_t data_len = data.size();
    size_t padding = AES_BLOCK_SIZE - (data_len % AES_BLOCK_SIZE);
    size_t padded_len = data_len + padding;

    std::vector<unsigned char> padded_data(data.begin(), data.end());
    padded_data.resize(padded_len, (unsigned char)padding);

    return padded_data;
}

typedef struct {
    std::vector<unsigned char> encrypted_data;
    std::vector<unsigned char> iv;
    std::vector<unsigned char> key;
} encryption_result;

/**
Encrypt the data with the key using GCM mode.
The provided key bytes is long enough (>= 32 bytes) for AES-256. 
Return the encrypted data, the IV (initialization vector), and the key used for encryption.

@param key The bytes to generate the encryption key.
@param data The data to encrypt.

@return The encrypted data, the IV, and the key used for encryption.
*/
encryption_result encrypt_data(
    const std::vector<unsigned char>& key,
    const std::vector<unsigned char>& data
) {
    if (key.size() < 32) {
        throw std::invalid_argument("Key must be at least 32 bytes for AES-256.");
    }

    encryption_result result;
    result.key.assign(key.begin(), key.begin() + 32); // Use the first 32 bytes for AES-256

    // Generate a random IV
    result.iv.resize(AES_BLOCK_SIZE);
    if (!RAND_bytes(result.iv.data(), result.iv.size())) {
        throw std::runtime_error("Failed to generate random IV.");
    }

    // Pad the data
    std::vector<unsigned char> padded_data = pad_data(data);
    result.encrypted_data.resize(padded_data.size());

    // Initialize AES GCM
    AES_KEY aes_key;
    if (AES_set_encrypt_key(result.key.data(), 256, &aes_key) < 0) {
        throw std::runtime_error("Failed to set encryption key.");
    }

    // Encrypt the data
    // Note: AES GCM requires additional authentication data and tag handling
    // This is a simplified example and does not include those details
    AES_gcm128_encrypt(padded_data.data(), result.encrypted_data.data(), padded_data.size(), &aes_key, result.iv.data(), AES_BLOCK_SIZE, nullptr, 0, nullptr);

    return result;
}