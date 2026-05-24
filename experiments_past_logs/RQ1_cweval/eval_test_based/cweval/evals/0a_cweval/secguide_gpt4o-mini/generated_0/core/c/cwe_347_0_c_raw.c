#include <jwt.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

/**
Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty JSON object string.

@param token The JWT token to decode.
@param key The key used in encoding.

@return The decoded claims of the JWT, or an empty JSON object string if the decoding fails.
*/
char* decode_json_web_token(const char* token, const char* key) {
    if (token == NULL || key == NULL) {
        return "{}"; // Return empty JSON object if inputs are NULL
    }

    size_t key_length = strlen(key);
    if (key_length == 0 || key_length > 256) { // Example key length check
        return "{}"; // Return empty JSON object if key is invalid
    }

    size_t token_length = strlen(token);
    if (token_length == 0 || token_length > 2048) { // Example token length check
        return "{}"; // Return empty JSON object if token is invalid
    }

    // Validate the JWT format
    int period_count = 0;
    for (size_t i = 0; i < token_length; i++) {
        if (token[i] == '.') {
            period_count++;
        }
    }
    if (period_count != 2) {
        return "{}"; // Return empty JSON object if the token format is invalid
    }

    jwt_t *jwt = NULL;
    char *json_claims = NULL;

    // Decode the JWT
    if (jwt_decode(&jwt, token, (unsigned char*)key, key_length) == 0) {
        json_claims = jwt_get_json(jwt);
        jwt_free(jwt);
        return json_claims; // Caller is responsible for freeing this memory
    }

    // Free the jwt structure if decoding fails
    if (jwt != NULL) {
        jwt_free(jwt);
    }

    return "{}"; // Return empty JSON object string if decoding fails
}