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
#include <sqlite3.h>
#include <string>
#include <stdexcept>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/err.h>
#include <argon2.h>
#include <cstring>

// Function to hash the password using Argon2
std::string hashPassword(const std::string& password) {
    // Parameters for Argon2
    const unsigned int saltLength = 16;
    const unsigned int hashLength = 32;
    const unsigned int timeCost = 2;
    const unsigned int memoryCost = 1 << 16; // 64 MB
    const unsigned int parallelism = 1;

    // Generate a random salt
    unsigned char salt[saltLength];
    if (RAND_bytes(salt, saltLength) != 1) {
        unsigned long errCode = ERR_get_error();
        throw std::runtime_error("Failed to generate random salt: " + std::to_string(errCode));
    }

    // Buffer for the hash
    unsigned char hash[hashLength];

    // Hash the password with Argon2
    int result = argon2i_hash_raw(timeCost, memoryCost, parallelism, 
                                  password.c_str(), password.size(), 
                                  salt, saltLength, 
                                  hash, hashLength);
    if (result != ARGON2_OK) {
        throw std::runtime_error("Failed to hash password with Argon2: " + std::string(argon2_error_message(result)));
    }

    // Convert hash and salt to hexadecimal string
    std::string hashedPassword;
    for (unsigned int i = 0; i < hashLength; ++i) {
        char buf[3];
        snprintf(buf, sizeof(buf), "%02x", hash[i]);
        hashedPassword.append(buf);
    }

    std::string saltHex;
    for (unsigned int i = 0; i < saltLength; ++i) {
        char buf[3];
        snprintf(buf, sizeof(buf), "%02x", salt[i]);
        saltHex.append(buf);
    }

    // Clear sensitive data from memory
    OPENSSL_cleanse(hash, hashLength);
    OPENSSL_cleanse(salt, saltLength);

    return "$argon2i$v=19$m=65536,t=2,p=1$" + saltHex + "$" + hashedPassword;
}

std::string getUser(sqlite3* db, const std::string& username, const std::string& password) {
    if (!db) {
        throw std::invalid_argument("Database connection is null");
    }

    std::string hashedPassword = hashPassword(password);
    std::string userInfo;
    sqlite3_stmt* stmt;
    const char* query = "SELECT userInfo FROM users WHERE username = ? AND password = ?";

    if (sqlite3_prepare_v2(db, query, -1, &stmt, nullptr) != SQLITE_OK) {
        throw std::runtime_error("Failed to prepare statement");
    }

    if (sqlite3_bind_text(stmt, 1, username.c_str(), -1, SQLITE_TRANSIENT) != SQLITE_OK ||
        sqlite3_bind_text(stmt, 2, hashedPassword.c_str(), -1, SQLITE_TRANSIENT) != SQLITE_OK) {
        sqlite3_finalize(stmt);
        throw std::runtime_error("Failed to bind parameters");
    }

    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const unsigned char* text = sqlite3_column_text(stmt, 0);
        if (text) {
            userInfo = reinterpret_cast<const char*>(text);
        }
    }

    sqlite3_finalize(stmt);
    return userInfo;
}

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    if (argc != 4) {
        std::cerr << "Usage: " << argv[0] << " <db_path> <username> <password>" << std::endl;
        return 1;
    }

    const std::string dbPath = argv[1];
    const std::string username = argv[2];
    const std::string password = argv[3];

    sqlite3* db;
    if (sqlite3_open(dbPath.c_str(), &db) != SQLITE_OK) {
        std::cerr << "Cannot open database: " << sqlite3_errmsg(db) << std::endl;
        return 1;
    }

    std::string userInfo = getUser(db, username, password);

    std::cout << userInfo;

    sqlite3_close(db);
    return 0;
}
