#include <jwt.h>
#include <string>
#include <stdexcept>
#include <memory>

std::string decode_json_web_token(const std::string& token, const std::string& key) {
    jwt_t *jwt = nullptr;
    char *json = nullptr;

    if (token.empty() || key.empty()) {
        throw std::invalid_argument("Token and key must not be empty");
    }

    if (jwt_decode(&jwt, token.c_str(), (unsigned char*)key.c_str(), key.length()) != 0) {
        if (jwt) {
            jwt_free(jwt);
        }
        throw std::runtime_error("Failed to decode JWT");
    }

    json = jwt_get_grants_json(jwt);
    if (!json) {
        jwt_free(jwt);
        throw std::runtime_error("Failed to get grants JSON from JWT");
    }

    std::string claims(json);
    jwt_free(jwt);
    
    // Assuming jwt_get_grants_json uses malloc, use the appropriate free function
    free(json); // Ensure this matches the allocation method used by the library

    // Additional validation of the claims can be added here

    return claims;
}