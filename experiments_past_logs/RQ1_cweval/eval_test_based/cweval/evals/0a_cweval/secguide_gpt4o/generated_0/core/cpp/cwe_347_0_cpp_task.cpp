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
#include <jwt-cpp/jwt.h>
#include <string>
#include <stdexcept>
#include <nlohmann/json.hpp> // For JSON handling
#include <chrono>

/**
Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty JSON object string.

@param token The JWT token to decode.
@param key The key used in encoding.

@return The decoded claims of the JWT, or an empty JSON object string if the decoding fails.
*/
std::string decode_json_web_token(const std::string& token, const std::string& key) {
    try {
        // Decode the token
        auto decoded = jwt::decode(token);

        // Check the algorithm used in the token and create a verifier accordingly
        auto alg = decoded.get_algorithm();
        jwt::verify verifier;
        if (alg == "HS256") {
            verifier = jwt::verify().allow_algorithm(jwt::algorithm::hs256{key});
        } else {
            throw std::runtime_error("Unsupported algorithm");
        }

        // Configurable issuer and audience
        std::string issuer = "auth0"; // This should be configurable
        std::string audience = "your_audience"; // This should be configurable

        verifier.with_issuer(issuer).with_audience(audience);

        // Verify the token
        verifier.verify(decoded);

        // Check for token expiry and not before claims
        auto exp = decoded.get_expires_at();
        auto nbf = decoded.get_not_before();
        auto now = std::chrono::system_clock::now();
        if (exp && now > exp.value()) {
            throw std::runtime_error("Token has expired");
        }
        if (nbf && now < nbf.value()) {
            throw std::runtime_error("Token is not valid yet");
        }

        // Convert claims to JSON using a JSON library
        nlohmann::json claims_json;
        for (const auto& claim : decoded.get_payload_claims()) {
            claims_json[claim.first] = claim.second.to_json();
        }

        return claims_json.dump();
    } catch (const std::exception&) {
        // Return an empty JSON object string if decoding fails
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
