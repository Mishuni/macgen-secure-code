
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