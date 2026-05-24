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
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>
#include <string>
#include <nlohmann/json.hpp>
#include <jwt/jwt.hpp> // Corrected include path

std::string decode_json_web_token(const std::string& token, const std::string& key) {
    try {
        // Validate inputs
        if (token.empty() || key.empty()) {
            return "{}";
        }

        // Decode the JWT token
        auto decoded = jwt::decode(token);

        // Verify the token using HS256 algorithm and the provided key
        auto verifier = jwt::verify()
            .allow_algorithm(jwt::algorithm::hs256{key})
            .with_issuer(decoded.get_issuer());

        verifier.verify(decoded);

        // Extract claims and convert to JSON
        nlohmann::json claims_json;
        for (const auto& e : decoded.get_payload_claims()) {
            claims_json[e.first] = e.second.to_json();
        }

        return claims_json.dump();
    } catch (...) {
        // Return empty JSON object string on failure
        return "{}";
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
