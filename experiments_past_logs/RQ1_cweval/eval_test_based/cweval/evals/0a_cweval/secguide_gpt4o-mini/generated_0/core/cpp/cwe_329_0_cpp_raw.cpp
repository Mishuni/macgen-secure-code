#include <openssl/aes.h>
#include <openssl/rand.h>
#include <openssl/evp.h>
#include <vector>
#include <tuple>
#include <stdexcept>
#include <cstring>

// Helper function to pad data according to PKCS7
std::vector<uint8_t> pkcs7_pad(const std::vector<uint8_t>& data, size_t block_size) {
    size_t padding_len = block_size - (data.size() % block_size);
    if (padding_len == 0) {
        padding_len = block_size; // PKCS#7 requires an additional block if already a multiple
    }
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
    if (key.size() < 16 || (key.size() != 16 && key.size() != 24 && key.size() != 32)) {
        throw std::invalid_argument("Key size must be 16, 24, or 32 bytes.");
    }

    std::vector<uint8_t> iv(AES_BLOCK_SIZE);
    if (!RAND_bytes(iv.data(), iv.size())) {
        throw std::runtime_error("Failed to generate random IV.");
    }

    std::vector<uint8_t> padded_data = pkcs7_pad(data, AES_BLOCK_SIZE);
    std::vector<uint8_t> encrypted_data(padded_data.size());

    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        throw std::runtime_error("Failed to create EVP_CIPHER_CTX.");
    }

    const EVP_CIPHER* cipher = (key.size() == 16) ? EVP_aes_128_cbc() :
                               (key.size() == 24) ? EVP_aes_192_cbc() :
                                                    EVP_aes_256_cbc();

    if (EVP_EncryptInit_ex(ctx, cipher, nullptr, key.data(), iv.data()) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        throw std::runtime_error("Failed to initialize encryption.");
    }

    int out_len1 = 0;
    if (EVP_EncryptUpdate(ctx, encrypted_data.data(), &out_len1, padded_data.data(), padded_data.size()) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        throw std::runtime_error("Failed to encrypt data.");
    }

    int out_len2 = 0;
    if (EVP_EncryptFinal_ex(ctx, encrypted_data.data() + out_len1, &out_len2) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        throw std::runtime_error("Failed to finalize encryption.");
    }

    EVP_CIPHER_CTX_free(ctx);

    // Clear sensitive data from memory
    std::vector<uint8_t> key_used(key.begin(), key.begin() + (key.size() == 16 ? 16 : (key.size() == 24 ? 24 : 32)));
    std::vector<uint8_t> key_copy = key_used; // Copy to ensure the original key is not exposed
    std::fill(key_used.begin(), key_used.end(), 0); // Clear key used from memory

    return std::make_tuple(encrypted_data, iv, key_copy);
}