#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/err.h>
#include <vector>
#include <string>
#include <utility>
#include <stdexcept>
#include <cstring>

struct HashedPassword {
    std::vector<unsigned char> hashed_password;
    std::vector<unsigned char> salt;
};

std::vector<HashedPassword> hash_passwords(int count, const std::vector<std::string>& usernames, const std::vector<std::string>& passwords) {
    if (count > passwords.size()) {
        throw std::out_of_range("Count exceeds the number of provided passwords");
    }

    std::vector<HashedPassword> hashed_passwords;

    for (int i = 0; i < count; ++i) {
        const std::string& password = passwords[i];

        if (password.length() < 8) {
            throw std::invalid_argument("Password must be at least 8 characters long");
        }

        std::vector<unsigned char> salt(16);
        if (RAND_bytes(salt.data(), salt.size()) != 1) {
            throw std::runtime_error("Failed to generate random salt");
        }

        std::vector<unsigned char> hashed_password(EVP_MD_size(EVP_sha256()));
        const int iterations = 100000;

        if (!PKCS5_PBKDF2_HMAC(password.c_str(), password.length(), salt.data(), salt.size(), iterations, EVP_MD_size(EVP_sha256()), hashed_password.data())) {
            throw std::runtime_error("PBKDF2 hashing failed");
        }

        hashed_passwords.push_back({std::move(hashed_password), std::move(salt)});

        // Clear sensitive data from memory
        std::memset(hashed_password.data(), 0, hashed_password.size());
        std::memset(salt.data(), 0, salt.size());
    }

    return hashed_passwords;
}