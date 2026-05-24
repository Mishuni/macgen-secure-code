#include <openssl/aes.h>
#include <openssl/rand.h>
#include <vector>
#include <tuple>
#include <stdexcept>

// Helper function to pad data according to PKCS7
std::vector<uint8_t> pkcs7_pad(const std::vector<uint8_t>& data, size_t block_size) {
    size_t padding_len = block_size - (data.size() % block_size);
    std::vector<uint8_t> padded = data;
    padded.insert(padded.end(), padding_len, static_cast<uint8_t>(padding_len));
    return padded;
}

std::tuple<std::vector<uint8_t>, std::vector<uint8_t>, std::vector<uint8_t>>
encrypt_data(const std::vector<uint8_t>& key, const std::vector<uint8_t>& data) {
    const size_t AES_KEY_LENGTH = 32; // 256 bits
    const size_t AES_BLOCK_SIZE = 16; // 16 bytes

    // Validate input key length
    if (key.size() < AES_KEY_LENGTH) {
        throw std::runtime_error("Key is too short for the selected AES encryption");
    }

    // Extract the appropriate length of the key
    std::vector<uint8_t> used_key(key.begin(), key.begin() + AES_KEY_LENGTH);

    // Generate a random IV
    std::vector<uint8_t> iv(AES_BLOCK_SIZE);
    if (!RAND_bytes(iv.data(), AES_BLOCK_SIZE)) {
        throw std::runtime_error("Failed to generate random IV");
    }

    // Pad the input data
    std::vector<uint8_t> padded_data = pkcs7_pad(data, AES_BLOCK_SIZE);

    // Prepare the output buffer
    std::vector<uint8_t> encrypted_data(padded_data.size());

    // Initialize AES encryption context
    AES_KEY encrypt_key;
    if (AES_set_encrypt_key(used_key.data(), AES_KEY_LENGTH * 8, &encrypt_key) < 0) {
        throw std::runtime_error("Failed to set encryption key");
    }

    // Encrypt the data
    AES_cbc_encrypt(padded_data.data(), encrypted_data.data(), padded_data.size(), &encrypt_key, iv.data(), AES_ENCRYPT);

    return std::make_tuple(encrypted_data, iv, used_key);
}