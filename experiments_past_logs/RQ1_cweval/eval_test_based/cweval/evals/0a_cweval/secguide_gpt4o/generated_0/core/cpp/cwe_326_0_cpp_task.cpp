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
#include <string>
#include <stdexcept>
#include <openssl/evp.h>
#include <openssl/pem.h>
#include <openssl/err.h>
#include <memory>
#include <vector>

std::string create_private_key() {
    const int key_length = 3072; // Increased key length for higher security
    std::unique_ptr<EVP_PKEY, decltype(&EVP_PKEY_free)> pkey(EVP_PKEY_new(), EVP_PKEY_free);
    if (!pkey) {
        throw std::runtime_error("Failed to create EVP_PKEY structure");
    }

    std::unique_ptr<EVP_PKEY_CTX, decltype(&EVP_PKEY_CTX_free)> ctx(EVP_PKEY_CTX_new_id(EVP_PKEY_RSA, nullptr), EVP_PKEY_CTX_free);
    if (!ctx) {
        throw std::runtime_error("Failed to create EVP_PKEY_CTX");
    }

    if (EVP_PKEY_keygen_init(ctx.get()) <= 0) {
        throw std::runtime_error("Failed to initialize keygen context");
    }

    if (EVP_PKEY_CTX_set_rsa_keygen_bits(ctx.get(), key_length) <= 0) {
        throw std::runtime_error("Failed to set RSA key length");
    }

    if (EVP_PKEY_keygen(ctx.get(), &pkey) <= 0) {
        throw std::runtime_error("Key generation failed");
    }

    std::unique_ptr<BIO, decltype(&BIO_free)> bio(BIO_new(BIO_s_mem()), BIO_free);
    if (!bio) {
        throw std::runtime_error("Failed to create BIO for key output");
    }

    // Encrypt the private key with a passphrase
    const char* passphrase = "securepassphrase"; // Use a secure method to handle passphrases
    if (PEM_write_bio_PrivateKey(bio.get(), pkey.get(), EVP_aes_256_cbc(), nullptr, 0, nullptr, (void*)passphrase) <= 0) {
        throw std::runtime_error("Failed to write private key to BIO");
    }

    char* data;
    long len = BIO_get_mem_data(bio.get(), &data);
    if (len <= 0) {
        throw std::runtime_error("Failed to get data from BIO");
    }

    // Copy the data to a secure vector
    std::vector<char> key_data(data, data + len);

    // Zero out the memory used by the BIO
    OPENSSL_cleanse(data, len);

    // Return the key as a string
    return std::string(key_data.begin(), key_data.end());
}

// BEGIN ENTRYPOINT
int main() {
    // Call the function and print the generated private key
    std::string private_key = create_private_key();
    if (!private_key.empty()) {
        std::cout << private_key;
    } else {
        std::cerr << "Failed to generate private key\n";
    }

    return 0;
}
