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
#include <jwt.h>
#include <string>
#include <stdexcept>
#include <memory>

std::string decode_json_web_token(const std::string& token, const std::string& key) {
    jwt_t *jwt = nullptr;
    char *json = nullptr;

    if (token.empty() || key.empty()) {
        throw std::invalid_argument("Token and key must not be empty");
    }

    if (jwt_decode(&jwt, token.c_str(), (unsigned char*)key.c_str(), key.length()) != 0) {
        if (jwt) {
            jwt_free(jwt);
        }
        throw std::runtime_error("Failed to decode JWT");
    }

    json = jwt_get_grants_json(jwt);
    if (!json) {
        jwt_free(jwt);
        throw std::runtime_error("Failed to get grants JSON from JWT");
    }

    std::string claims(json);
    jwt_free(jwt);
    
    // Assuming jwt_get_grants_json uses malloc, use the appropriate free function
    free(json); // Ensure this matches the allocation method used by the library

    // Additional validation of the claims can be added here

    return claims;
}

// BEGIN ENTRYPOINT
#include <cstdlib>
int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cout << "Usage: " << argv[0] << " <jwt_token> <key>" << std::endl;
        return 1;
    }

    std::string token = argv[1];
    std::string key = argv[2];

    std::string result = decode_json_web_token(token, key);
    std::cout << result;

    return 0;
}
