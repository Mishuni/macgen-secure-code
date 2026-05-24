
#include <jwt.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

/**
Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty JSON object string.

@param token The JWT token to decode.
@param key The key used in encoding.

@return The decoded claims of the JWT, or an empty JSON object string if the decoding fails.
*/
char* decode_json_web_token(const char* token, const char* key) {
    // Validate input parameters
    if (token == NULL || key == NULL) {
        return strdup("{}"); // Return an empty JSON object string
    }

    jwt_t *jwt = NULL;
    int decode_status = 0;
    char *claims = NULL;

    // Decode the JWT token
    decode_status = jwt_decode(&jwt, token, (unsigned char*)key, strlen(key));
    if (decode_status != 0) {
        // Decoding failed, return an empty JSON object string
        return strdup("{}");
    }

    // Extract claims as a JSON string
    claims = jwt_get_grants_json(jwt);
    if (claims == NULL) {
        // If claims extraction fails, return an empty JSON object string
        jwt_free(jwt);
        return strdup("{}");
    }

    // Duplicate the claims to return, ensuring memory safety
    char *result = strdup(claims);

    // Free allocated resources
    jwt_free_grants_json(claims);
    jwt_free(jwt);

    // Return the decoded claims
    return result;
}