#include <sqlite3.h>
#include <string>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <iomanip>
#include <sstream>
#include <stdexcept>
#include <vector>
#include <cstring>
#include <algorithm>

std::string generateSalt(size_t length) {
    std::vector<unsigned char> salt(length);
    if (RAND_bytes(salt.data(), length) != 1) {
        throw std::runtime_error("Failed to generate salt");
    }
    std::ostringstream oss;
    for (const auto& byte : salt) {
        oss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
    }
    return oss.str();
}

std::string hashPassword(const std::string& password, const std::string& salt) {
    std::string saltedPassword = password + salt;
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hashLength;

    EVP_MD_CTX* ctx = EVP_MD_CTX_new();
    if (!ctx) {
        throw std::runtime_error("Failed to create context");
    }
    if (EVP_DigestInit_ex(ctx, EVP_sha256(), nullptr) != 1 ||
        EVP_DigestUpdate(ctx, saltedPassword.c_str(), saltedPassword.size()) != 1 ||
        EVP_DigestFinal_ex(ctx, hash, &hashLength) != 1) {
        EVP_MD_CTX_free(ctx);
        throw std::runtime_error("Failed to hash password");
    }
    EVP_MD_CTX_free(ctx);

    std::ostringstream oss;
    for (unsigned int i = 0; i < hashLength; ++i) {
        oss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(hash[i]);
    }
    return oss.str();
}

bool constantTimeCompare(const std::string& a, const std::string& b) {
    if (a.size() != b.size()) return false;
    return std::equal(a.begin(), a.end(), b.begin());
}

std::string getUser(sqlite3* db, const std::string& username, const std::string& password) {
    std::string userInfo;
    sqlite3_stmt* stmt;

    const char* sql = "SELECT salt, hashed_password, userInfo FROM users WHERE username = ?";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        throw std::runtime_error("Failed to prepare statement");
    }

    sqlite3_bind_text(stmt, 1, username.c_str(), -1, SQLITE_STATIC);

    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const char* salt = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
        const char* storedHash = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
        
        if (salt && storedHash) {
            std::string hashedPassword = hashPassword(password, salt);
            if (constantTimeCompare(hashedPassword, storedHash)) {
                const char* info = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
                if (info) {
                    userInfo = info;
                }
            }
        }
    }

    sqlite3_finalize(stmt);
    return userInfo;
}