
#include <jwt-cpp/jwt.h>
#include <string>

std::string decode_json_web_token(const std::string& token, const std::string& key) {
    try {
        auto decoded = jwt::decode(token);
        auto verifier = jwt::verify()
            .allow_algorithm(jwt::algorithm::hs256{key})
            .with_issuer(decoded.get_issuer());

        verifier.verify(decoded);

        return decoded.get_payload();
    } catch (const std::exception&) {
        return "{}";
    }
}