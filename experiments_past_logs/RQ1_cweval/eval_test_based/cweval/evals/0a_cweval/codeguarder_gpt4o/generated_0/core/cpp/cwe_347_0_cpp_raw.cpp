
#include <jwt-cpp/jwt.h>
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
        // Verify and decode the JWT token
        auto decoded = jwt::decode(token);

        // Verify the token's signature and algorithm
        auto verifier = jwt::verify()
            .allow_algorithm(jwt::algorithm::hs256{key})
            .with_issuer("auth0");

        verifier.verify(decoded);

        // Extract claims as JSON
        return decoded.get_payload();
    } catch (const std::exception& e) {
        // Return an empty JSON object string if decoding fails
        return "{}";
    }
}