#include <openssl/evp.h>
#include <openssl/rand.h>
#include <vector>
#include <string>
#include <utility>
#include <stdexcept>

const int MIN_PASSWORD_LENGTH = 8; // Example minimum length for passwords

std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hash_passwords(int count, const std::vector<std::string>& usernames, const std::vector<std::string>& passwords) {
    if (usernames.size() != passwords.size()) {
        throw std::invalid_argument("Usernames and passwords count mismatch.");
    }

    std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hashed_passwords;

    for (int i = 0; i < count; ++i) {
        const std::string& password = passwords[i];

        if (password.length() < MIN_PASSWORD_LENGTH) {
            throw std::invalid_argument("Password too short");
        }

        std::vector<unsigned char> salt(32);
        // Resize hash vector to the correct size for SHA-256
        std::vector<unsigned char> hash(EVP_MD_size(EVP_sha256()));
        
        // Generate random salt
        if (RAND_bytes(salt.data(), salt.size()) != 1) {
            throw std::runtime_error("Failed to generate secure random salt");
        }

        // Hash the password using PBKDF2
        if (PKCS5_PBKDF2_HMAC(password.c_str(), password.length(), salt.data(), salt.size(), 10000, EVP_sha256(), hash.size(), hash.data()) == 0) {
            throw std::runtime_error("Failed to hash password");
        }

        hashed_passwords.emplace_back(std::move(hash), std::move(salt));
    }

    return hashed_passwords;
}