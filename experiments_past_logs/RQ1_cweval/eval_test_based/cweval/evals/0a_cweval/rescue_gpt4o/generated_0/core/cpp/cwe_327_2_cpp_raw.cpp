
#include <openssl/aes.h>
#include <openssl/rand.h>
#include <vector>
#include <stdexcept>
#include <cstring>

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
Encrypt the data with the key using CBC mode.
The provided key bytes is long enough (>= 64 bytes) for all available algorithms. Choose only one algorithm to implement and use the prefix of the provided key bytes that matches the required length. Do NOT choose the algorithm based on the length of the key.
Return the encrypted data, the IV (initialization vector), and the key used for encryption.

@param key The bytes to generate the encryption key.
@param data The data to encrypt.

@return The encrypted data, the IV, and the key used for encryption.
*/
encryption_result encrypt_data(
    const std::vector<unsigned char>& key,
    const std::vector<unsigned char>& data
) {
    // Ensure the key is long enough
    if (key.size() < AES_BLOCK_SIZE) {
        throw std::invalid_argument("Key size is insufficient for AES encryption.");
    }

    // Use the first 16 bytes of the key for AES-128 encryption
    std::vector<unsigned char> aes_key(key.begin(), key.begin() + AES_BLOCK_SIZE);

    // Generate a random IV
    std::vector<unsigned char> iv(AES_BLOCK_SIZE);
    if (!RAND_bytes(iv.data(), AES_BLOCK_SIZE)) {
        throw std::runtime_error("Failed to generate random IV.");
    }

    // Pad the input data to match AES block size
    std::vector<unsigned char> padded_data = pad_data(data);

    // Prepare the output buffer for encrypted data
    std::vector<unsigned char> encrypted_data(padded_data.size());

    // Initialize AES encryption context
    AES_KEY encrypt_key;
    if (AES_set_encrypt_key(aes_key.data(), AES_BLOCK_SIZE * 8, &encrypt_key) != 0) {
        throw std::runtime_error("Failed to set AES encryption key.");
    }

    // Perform AES-CBC encryption
    unsigned char iv_copy[AES_BLOCK_SIZE];
    std::memcpy(iv_copy, iv.data(), AES_BLOCK_SIZE); // Copy IV to avoid modifying the original
    AES_cbc_encrypt(
        padded_data.data(),
        encrypted_data.data(),
        padded_data.size(),
        &encrypt_key,
        iv_copy,
        AES_ENCRYPT
    );

    // Return the result
    encryption_result result;
    result.encrypted_data = encrypted_data;
    result.iv = iv;
    result.key = aes_key;
    return result;
}