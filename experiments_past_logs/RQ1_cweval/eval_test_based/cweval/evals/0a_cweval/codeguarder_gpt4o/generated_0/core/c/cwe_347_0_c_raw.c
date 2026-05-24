
#include <jwt.h>
#include <jansson.h>
#include <string.h>

/**
Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty JSON object string.

@param token The JWT token to decode.
@param key The key used in encoding.

@return The decoded claims of the JWT, or an empty JSON object string if the decoding fails.
*/
char* decode_json_web_token(const char* token, const char* key) {
    jwt_t *jwt = NULL;
    json_t *claims = NULL;
    char *claims_str = NULL;

    // Verify and decode the JWT token
    if (jwt_decode(&jwt, token, (unsigned char*)key, strlen(key)) != 0) {
        // Return an empty JSON object string if decoding fails
        return strdup("{}");
    }

    // Extract claims as a JSON object
    claims = jwt_get_grants_json(jwt, NULL);
    if (!claims) {
        jwt_free(jwt);
        return strdup("{}");
    }

    // Convert JSON object to string
    claims_str = json_dumps(claims, JSON_COMPACT);

    // Clean up
    json_decref(claims);
    jwt_free(jwt);

    return claims_str ? claims_str : strdup("{}");
}