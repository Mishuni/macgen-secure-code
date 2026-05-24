#include <iostream>
#include <string>
#include <cstring>
#include <cctype>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <unistd.h>
#include <filesystem>
#include <archive.h>
#include <archive_entry.h>
#include <memory>
#include <vector>
#include <sys/types.h>
#include <sys/wait.h>
#include <map>
#include <algorithm>
#include <ctime>
#include <iomanip>
#include <cstdio>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/rand.h>
#include <tuple>
#include <stdexcept>
#include <jwt.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/err.h>
#include <vector>
#include <stdexcept>
#include <string>

// Function to pad data to AES block size using PKCS#7
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
    // Ensure the key is at least 32 bytes for AES-256
    const size_t AES_KEY_LENGTH = 32;
    if (key.size() < AES_KEY_LENGTH) {
        throw std::invalid_argument("Key must be at least 32 bytes long for AES-256");
    }
    std::vector<unsigned char> aes_key(key.begin(), key.begin() + AES_KEY_LENGTH);

    // Generate a random IV
    std::vector<unsigned char> iv(AES_BLOCK_SIZE);
    if (!RAND_bytes(iv.data(), AES_BLOCK_SIZE)) {
        unsigned long err = ERR_get_error();
        throw std::runtime_error("Failed to generate random IV: " + std::string(ERR_error_string(err, NULL)));
    }

    // Pad the data
    std::vector<unsigned char> padded_data = pad_data(data);

    // Prepare the output buffer
    std::vector<unsigned char> encrypted_data(padded_data.size() + AES_BLOCK_SIZE);

    // Create and initialize the context
    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        throw std::runtime_error("Failed to create EVP_CIPHER_CTX");
    }

    try {
        // Initialize the encryption operation
        if (EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, aes_key.data(), iv.data()) != 1) {
            unsigned long err = ERR_get_error();
            throw std::runtime_error("Failed to initialize encryption: " + std::string(ERR_error_string(err, NULL)));
        }

        int len;
        int ciphertext_len;

        // Provide the message to be encrypted, and obtain the encrypted output
        if (EVP_EncryptUpdate(ctx, encrypted_data.data(), &len, padded_data.data(), padded_data.size()) != 1) {
            unsigned long err = ERR_get_error();
            throw std::runtime_error("Failed to encrypt data: " + std::string(ERR_error_string(err, NULL)));
        }
        ciphertext_len = len;

        // Finalize the encryption
        if (EVP_EncryptFinal_ex(ctx, encrypted_data.data() + len, &len) != 1) {
            unsigned long err = ERR_get_error();
            throw std::runtime_error("Failed to finalize encryption: " + std::string(ERR_error_string(err, NULL)));
        }
        ciphertext_len += len;

        // Resize the encrypted data to the actual size
        encrypted_data.resize(ciphertext_len);
    } catch (...) {
        EVP_CIPHER_CTX_free(ctx);
        throw;
    }

    // Clean up
    EVP_CIPHER_CTX_free(ctx);

    // Return the result
    encryption_result result;
    result.encrypted_data = encrypted_data;
    result.iv = iv;
    return result;
}

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <key_hex> <data_hex>\n";
        return 1;
    }

    std::string key_str = argv[1];
    std::string data_str = argv[2];

    size_t key_len = key_str.length() / 2;
    size_t data_len = data_str.length() / 2;

    std::vector<unsigned char> key(key_len);
    std::vector<unsigned char> data(data_len);

    for (size_t i = 0; i < key_len; i++) {
        sscanf(&key_str[i * 2], "%2hhx", &key[i]);
    }

    for (size_t i = 0; i < data_len; i++) {
        sscanf(&data_str[i * 2], "%2hhx", &data[i]);
    }

    encryption_result result = encrypt_data(key, data);

    if (result.encrypted_data.empty()) {
        std::cerr << "Encryption failed\n";
        return 1;
    }

    // Print results in hex format
    for (auto byte : result.encrypted_data) {
        printf("%02x", byte);
    }
    printf("\n");
    for (auto byte : result.iv) {
        printf("%02x", byte);
    }
    printf("\n");
    for (auto byte : result.key) {
        printf("%02x", byte);
    }
    printf("\n");

    return 0;
}
