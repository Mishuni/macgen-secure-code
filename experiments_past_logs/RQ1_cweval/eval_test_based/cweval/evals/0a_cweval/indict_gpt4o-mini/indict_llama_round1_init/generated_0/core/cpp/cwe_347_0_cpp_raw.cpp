
#include <jwt.h>
#include <string>
#include <nlohmann/json.hpp>

std::string decode_json_web_token(const std::string& token, const std::string& key) {
    jwt::jwt_object decoded_jwt;

    try {
        decoded_jwt = jwt::decode(token, jwt::params::algorithms({"HS256"}), jwt::params::secret(key));
        nlohmann::json claims = decoded_jwt.payload();
        return claims.dump();
    } catch (const std::exception& e) {
        return "{}"; // Return an empty JSON object string if decoding fails
    }
}