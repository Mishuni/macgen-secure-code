
#include <jwt.h>
#include <string>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

/**
Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty JSON object string.

@param token The JWT token to decode.
@param key The key used in encoding.

@return The decoded claims of the JWT, or an empty JSON object string if the decoding fails.
*/
std::string decode_json_web_token(const std::string& token, const std::string& key) {
    jwt::jwt_object jwt_obj;

    try {
        // Decode the JWT using the provided key
        jwt_obj = jwt::decode(token, jwt::params::algorithms({"HS256"}), jwt::params::secret(key));
        
        // Convert the claims to a JSON string
        json claims = jwt_obj.payload();
        return claims.dump(); // Return the claims as a JSON string
    } catch (const std::exception& e) {
        // If decoding fails, return an empty JSON object string
        return "{}";
    }
}