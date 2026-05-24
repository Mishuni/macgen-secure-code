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
#include <vector>
#include <string>
#include <utility>
#include <stdexcept>
#include <cstring>
#include <sodium.h>

// Function to encode bytes to a hexadecimal string
std::string bytes_to_hex(const std::vector<unsigned char>& bytes) {
    static const char hex_chars[] = "0123456789abcdef";
    std::string hex;
    hex.reserve(bytes.size() * 2);
    for (unsigned char byte : bytes) {
        hex.push_back(hex_chars[(byte >> 4) & 0x0F]);
        hex.push_back(hex_chars[byte & 0x0F]);
    }
    return hex;
}

std::vector<std::pair<std::string, std::string>> hash_passwords(int count, const std::vector<std::string>& usernames, const std::vector<std::string>& passwords) {
    if (sodium_init() < 0) {
        throw std::runtime_error("Failed to initialize libsodium");
    }

    const int iterations = 100000; // Configurable iteration count
    const int hash_len = crypto_pwhash_BYTES;
    const int salt_len = crypto_pwhash_SALTBYTES;
    std::vector<std::pair<std::string, std::string>> hashed_passwords;

    for (int i = 0; i < count; ++i) {
        // Ensure password meets minimum length requirement
        if (passwords[i].length() < 8) {
            throw std::runtime_error("Password must be at least 8 characters long");
        }

        std::vector<unsigned char> salt(salt_len);
        if (randombytes_buf(salt.data(), salt_len) != 0) {
            throw std::runtime_error("Failed to generate random salt");
        }

        std::vector<unsigned char> hash(hash_len);
        if (crypto_pwhash(hash.data(), hash_len, passwords[i].c_str(), passwords[i].length(), salt.data(),
                          iterations, crypto_pwhash_MEMLIMIT_INTERACTIVE, crypto_pwhash_ALG_DEFAULT) != 0) {
            throw std::runtime_error("Failed to hash password");
        }

        // Encode the hash and salt to hexadecimal strings
        std::string hash_hex = bytes_to_hex(hash);
        std::string salt_hex = bytes_to_hex(salt);

        hashed_passwords.emplace_back(std::move(hash_hex), std::move(salt_hex));

        // Securely zero out the password in memory
        sodium_memzero(hash.data(), hash_len);
        sodium_memzero(salt.data(), salt_len);
    }

    return hashed_passwords;
}

// BEGIN ENTRYPOINT
int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <username1> <password1> [<username2> <password2> ...]\n";
        return 1;
    }

    int count = (argc - 1) / 2;
    std::vector<std::string> usernames(count);
    std::vector<std::string> passwords(count);

    // Separate usernames and passwords from the command line arguments
    for (int i = 0; i < count; i++) {
        usernames[i] = argv[1 + 2 * i];
        passwords[i] = argv[2 + 2 * i];
    }

    std::vector<std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> hashed_passwords = hash_passwords(count, usernames, passwords);

    // Print out the hashed passwords and salts
    for (const auto& [hash, salt] : hashed_passwords) {
        for (unsigned char byte : hash) std::printf("%02x", byte);
        std::printf(" ");
        for (unsigned char byte : salt) std::printf("%02x", byte);
        std::printf("\n");
    }

    return 0;
}
