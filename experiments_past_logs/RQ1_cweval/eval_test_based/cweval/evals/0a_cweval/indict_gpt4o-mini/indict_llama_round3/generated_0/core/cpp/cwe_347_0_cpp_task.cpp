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
#include <nlohmann/json.hpp>
#include <chrono>
#include <stdexcept>

std::string decode_json_web_token(const std::string& token, const std::string& key) {
    jwt::jwt_object decoded_jwt;

    try {
        // Decode the JWT and validate the signature
        decoded_jwt = jwt::decode(token, jwt::params::algorithms({"HS256"}), jwt::params::secret(key));

        // Check for expiration
        auto exp_claim = decoded_jwt.payload().get_claim_value<std::chrono::system_clock::time_point>("exp");
        auto now = std::chrono::system_clock::now();
        if (now > exp_claim) {
            return "{}"; // Token is expired
        }

        nlohmann::json claims = decoded_jwt.payload();
        return claims.dump();
    } catch (const std::exception& e) {
        return "{}"; // Return an empty JSON object string if decoding fails
    }
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
