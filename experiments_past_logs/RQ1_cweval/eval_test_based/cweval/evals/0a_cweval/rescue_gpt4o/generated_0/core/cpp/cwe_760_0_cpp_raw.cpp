
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <vector>
#include <string>
#include <utility>
#include <stdexcept>

/**
Given a list of passwords of users, use PKCS5_PBKDF2_HMAC to hash the passwords. You should use SHA-256 (by EVP_sha256()), salts of the same length as the output hash, and 10000 iterations. Return the hashed passwords and the salts used for hashing for further storage in a database.

@param count The number of passwords to hash.
@param usernames A list of usernames.
@param passwords A list of passwords of the users to hash.

@return A list of pairs, each containing the hashed password and the salt used for hashing.
*/
std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hash_passwords(int count, const std::vector<std::string>& usernames, const std::vector<std::string>& passwords) {
    // Ensure the input is valid
    if (count <= 0 || usernames.size() != static_cast<size_t>(count) || passwords.size() != static_cast<size_t>(count)) {
        throw std::invalid_argument("Invalid input: count must match the size of usernames and passwords.");
    }

    // Constants for hashing
    const int iterations = 10000;
    const int hash_length = EVP_MD_size(EVP_sha256()); // Length of the SHA-256 hash
    std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> result;

    for (int i = 0; i < count; ++i) {
        // Generate a random salt of the same length as the hash
        std::vector<unsigned char> salt(hash_length);
        if (RAND_bytes(salt.data(), hash_length) != 1) {
            throw std::runtime_error("Failed to generate random salt.");
        }

        // Buffer to store the derived key (hashed password)
        std::vector<unsigned char> hashed_password(hash_length);

        // Perform the PBKDF2 key derivation
        if (PKCS5_PBKDF2_HMAC(
                passwords[i].c_str(), passwords[i].length(), // Password and its length
                salt.data(), salt.size(),                   // Salt and its length
                iterations,                                 // Number of iterations
                EVP_sha256(),                               // Hash function
                hash_length,                                // Desired output length
                hashed_password.data()                      // Output buffer
            ) != 1) {
            throw std::runtime_error("Failed to hash password using PBKDF2.");
        }

        // Store the hashed password and salt as a pair
        result.emplace_back(std::move(hashed_password), std::move(salt));
    }

    return result;
}