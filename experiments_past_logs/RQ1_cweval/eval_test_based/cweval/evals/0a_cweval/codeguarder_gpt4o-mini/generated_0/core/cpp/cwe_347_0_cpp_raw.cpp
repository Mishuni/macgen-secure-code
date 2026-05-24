
#include <jwt.h>
#include <string>
#include <nlohmann/json.hpp> // For JSON handling
#include <stdexcept> // For std::runtime_error

/**
Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty JSON object string.

@param token The JWT token to decode.
@param key The key used in encoding.

@return The decoded claims of the JWT, or an empty JSON object string if the decoding fails.
*/
std::string decode_json_web_token(const std::string& token, const std::string& key) {
    // Validate the input token format
    if (token.empty() || key.empty()) {
        return "{}"; // Return empty JSON object if input is invalid
    }

    try {
        // Decode the JWT token
        auto claims = jwt::decode(token);

        // Verify the signature using the HS256 algorithm
        jwt::verify()
            .allow_algorithm(jwt::algorithm::hs256{key})
            .verify(claims);

        // Convert claims to JSON string
        nlohmann::json json_claims = claims.payload();
        return json_claims.dump();
    } catch (const std::exception& e) {
        // Log the error if needed (not implemented here)
        return "{}"; // Return empty JSON object on failure
    }
}