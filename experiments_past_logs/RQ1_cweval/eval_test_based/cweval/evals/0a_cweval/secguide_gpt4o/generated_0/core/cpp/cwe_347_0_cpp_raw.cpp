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