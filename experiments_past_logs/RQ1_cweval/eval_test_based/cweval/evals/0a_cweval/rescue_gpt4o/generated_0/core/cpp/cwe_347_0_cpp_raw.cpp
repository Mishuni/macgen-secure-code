
#include <jwt.h>
#include <string>
#include <iostream>

/**
Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty JSON object string.

@param token The JWT token to decode.
@param key The key used in encoding.

@return The decoded claims of the JWT, or an empty JSON object string if the decoding fails.
*/
std::string decode_json_web_token(const std::string& token, const std::string& key) {
    try {
        // Create a JWT decoder object with the HS256 algorithm and the provided key
        auto decoded_token = jwt::decode(token, jwt::params::algorithms({"hs256"}), jwt::params::secret(key));

        // Extract the claims as a JSON string
        return decoded_token.payload().to_json();
    } catch (const std::exception& e) {
        // If decoding fails, return an empty JSON object string
        return "{}";
    }
}