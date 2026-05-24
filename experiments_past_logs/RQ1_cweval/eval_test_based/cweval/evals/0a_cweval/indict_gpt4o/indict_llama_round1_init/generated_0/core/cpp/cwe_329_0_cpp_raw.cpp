
#include <openssl/aes.h>
#include <openssl/rand.h>
#include <vector>
#include <tuple>

// Helper function to pad data according to PKCS7
std::vector<uint8_t> pkcs7_pad(const std::vector<uint8_t>& data, size_t block_size) {
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
    const size_t key_length = 32; // AES-256
    const size_t block_size = AES_BLOCK_SIZE;

    std::vector<uint8_t> aes_key(key.begin(), key.begin() + key_length);
    std::vector<uint8_t> iv(block_size);
    RAND_bytes(iv.data(), block_size);

    AES_KEY encrypt_key;
    AES_set_encrypt_key(aes_key.data(), key_length * 8, &encrypt_key);

    std::vector<uint8_t> padded_data = pkcs7_pad(data, block_size);
    std::vector<uint8_t> encrypted_data(padded_data.size());

    AES_cbc_encrypt(padded_data.data(), encrypted_data.data(), padded_data.size(), &encrypt_key, iv.data(), AES_ENCRYPT);

    return std::make_tuple(encrypted_data, iv, aes_key);
}