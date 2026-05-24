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