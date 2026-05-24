
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <vector>
#include <string>
#include <utility>

std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hash_passwords(int count, const std::vector<std::string>& usernames, const std::vector<std::string>& passwords) {
    std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hashed_passwords;

    for (int i = 0; i < count; ++i) {
        const std::string& password = passwords[i];

        // Generate a random salt of the same length as the output hash (32 bytes for SHA-256)
        std::vector<unsigned char> salt(SHA256_DIGEST_LENGTH);
        if (RAND_bytes(salt.data(), salt.size()) != 1) {
            throw std::runtime_error("Error generating random salt");
        }

        // Prepare the output buffer for the hashed password
        std::vector<unsigned char> hashed_password(SHA256_DIGEST_LENGTH);

        // Hash the password using PBKDF2 with HMAC-SHA256
        if (PKCS5_PBKDF2_HMAC(password.c_str(), password.length(), salt.data(), salt.size(), 10000, EVP_sha256(), SHA256_DIGEST_LENGTH, hashed_password.data()) != 1) {
            throw std::runtime_error("Error hashing password");
        }

        // Store the hashed password and salt
        hashed_passwords.emplace_back(hashed_password, salt);
    }

    return hashed_passwords;
}