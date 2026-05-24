
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <vector>
#include <string>
#include <utility>
#include <stdexcept>

std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hash_passwords(int count, const std::vector<std::string>& usernames, const std::vector<std::string>& passwords) {
    if (count != usernames.size() || count != passwords.size()) {
        throw std::invalid_argument("Count does not match the size of usernames or passwords vectors");
    }

    if (count == 0) {
        throw std::invalid_argument("Input vectors must not be empty");
    }

    std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> result;
    const int hash_len = EVP_MD_size(EVP_sha256());
    const int iterations = 10000;

    for (int i = 0; i < count; ++i) {
        std::vector<unsigned char> salt(hash_len);
        std::vector<unsigned char> hash(hash_len);

        // Generate a random salt
        if (RAND_bytes(salt.data(), hash_len) != 1) {
            throw std::runtime_error("Error generating random salt");
        }

        // Hash the password with the salt
        if (PKCS5_PBKDF2_HMAC(passwords[i].c_str(), passwords[i].length(), salt.data(), hash_len, iterations, EVP_sha256(), hash_len, hash.data()) != 1) {
            throw std::runtime_error("Error hashing password");
        }

        result.emplace_back(hash, salt);
    }

    return result;
}