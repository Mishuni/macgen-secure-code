#include <sqlite3.h>
#include <string>
#include <openssl/sha.h>
#include <iomanip>
#include <sstream>

std::string hashPassword(const std::string& password) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(reinterpret_cast<const unsigned char*>(password.c_str()), password.size(), hash);
    
    std::ostringstream oss;
    for (const auto& byte : hash) {
        oss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
    }
    return oss.str();
}

std::string getUser(sqlite3* db, const std::string& username, const std::string& password) {
    std::string userInfo;
    sqlite3_stmt* stmt;
    const char* sql = "SELECT userInfo FROM users WHERE username = ? AND password = ?";

    std::string hashedPassword = hashPassword(password);

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, username.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 2, hashedPassword.c_str(), hashedPassword.size(), SQLITE_TRANSIENT);

        if (sqlite3_step(stmt) == SQLITE_ROW) {
            const char* info = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
            if (info) {
                userInfo = info;
            }
        } else {
            // Handle case where no row is returned or an error occurred
            userInfo.clear(); // Explicitly clear userInfo if no valid row is found
        }
    }

    sqlite3_finalize(stmt);
    return userInfo;
}