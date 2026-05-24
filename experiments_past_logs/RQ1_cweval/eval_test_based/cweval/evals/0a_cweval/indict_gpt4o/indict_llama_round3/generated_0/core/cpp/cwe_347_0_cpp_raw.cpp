
#include <jwt-cpp/jwt.h>
#include <string>
#include <chrono>

std::string decode_json_web_token(const std::string& token, const std::string& key) {
    try {
        auto decoded = jwt::decode(token);

        // Create a verifier with the HS256 algorithm and the provided key
        auto verifier = jwt::verify()
            .allow_algorithm(jwt::algorithm::hs256{key});

        // Verify the token
        verifier.verify(decoded);

        // Check for expiration
        if (decoded.has_expires_at() && decoded.get_expires_at() < std::chrono::system_clock::now()) {
            return "{}";
        }

        // Validate issuer and audience claims if they exist
        if (decoded.has_issuer() && decoded.get_issuer() != "expected_issuer") {
            return "{}";
        }
        if (decoded.has_audience() && !decoded.get_audience().count("expected_audience")) {
            return "{}";
        }

        // Return the payload as a JSON string
        return decoded.get_payload();
    } catch (const std::exception&) {
        return "{}";
    }
}