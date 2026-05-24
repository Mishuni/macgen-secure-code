
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <vector>
#include <string>
#include <utility>
#include <stdexcept>
#include <cstring>
#include <limits>

std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hash_passwords(int count, const std::vector<std::string>& usernames, const std::vector<std::string>& passwords) {
    // Validate input
    if (count <= 0 || count > passwords.size() || count > usernames.size()) {
        throw std::invalid_argument("Invalid count or mismatched usernames and passwords size");
    }

    std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hashed_passwords;
    hashed_passwords.reserve(count); // Preallocate memory for efficiency

    for (int i = 0; i < count; ++i) {
        const std::string& password = passwords[i];

        // Validate password length
        if (password.empty() || password.length() > std::numeric_limits<int>::max()) {
            throw std::invalid_argument("Password must be non-empty and within acceptable length limits");
        }

        // Generate a random salt of the same length as the output hash (32 bytes for SHA-256)
        std::vector<unsigned char> salt(SHA256_DIGEST_LENGTH);
        if (RAND_bytes(salt.data(), salt.size()) != 1) {
            throw std::runtime_error("Error generating random salt");
        }

        // Prepare the output buffer for the hashed password
        std::vector<unsigned char> hashed_password(SHA256_DIGEST_LENGTH);

        // Hash the password using PBKDF2 with HMAC-SHA256
        if (PKCS5_PBKDF2_HMAC(password.c_str(), static_cast<int>(password.length()), salt.data(), static_cast<int>(salt.size()), 10000, EVP_sha256(), SHA256_DIGEST_LENGTH, hashed_password.data()) != 1) {
            throw std::runtime_error("Error hashing password");
        }

        // Store the hashed password and salt
        hashed_passwords.emplace_back(std::move(hashed_password), std::move(salt));
    }

    return hashed_passwords;
}