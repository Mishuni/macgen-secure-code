
#include <openssl/sha.h>
#include <openssl/evp.h>
#include <openssl/err.h>
#include <string>
#include <sstream>
#include <iomanip>

std::string hashCertificate(const std::string& cert) {
    // Initialize the SHA-256 context
    EVP_MD_CTX* ctx = EVP_MD_CTX_new();
    if (!ctx) {
        throw std::runtime_error("Failed to create EVP_MD_CTX");
    }

    // Initialize SHA-256
    if (EVP_DigestInit_ex(ctx, EVP_sha256(), nullptr) != 1) {
        EVP_MD_CTX_free(ctx);
        throw std::runtime_error("Failed to initialize SHA-256");
    }

    // Update the context with the certificate data
    if (EVP_DigestUpdate(ctx, cert.data(), cert.size()) != 1) {
        EVP_MD_CTX_free(ctx);
        throw std::runtime_error("Failed to update SHA-256 with certificate data");
    }

    // Finalize the digest
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    if (EVP_DigestFinal_ex(ctx, hash, &hash_len) != 1) {
        EVP_MD_CTX_free(ctx);
        throw std::runtime_error("Failed to finalize SHA-256");
    }

    // Clean up
    EVP_MD_CTX_free(ctx);

    // Convert hash to hexadecimal string
    std::ostringstream hex_stream;
    for (unsigned int i = 0; i < hash_len; ++i) {
        hex_stream << std::setw(2) << std::setfill('0') << std::hex << static_cast<int>(hash[i]);
    }

    return hex_stream.str();
}