#include <jwt.h>
#include <string.h>
#include <jansson.h>
#include <stdlib.h>

char* decode_json_web_token(const char* token, const char* key) {
    if (!token || !key) {
        return NULL; // Return NULL if inputs are invalid
    }

    jwt_t *jwt = NULL;
    char *decoded_claims = NULL;

    // Decode the JWT token using the provided key
    if (jwt_decode(&jwt, token, (unsigned char*)key, strlen(key)) != 0) {
        return NULL; // Return NULL if decoding fails
    }

    // Verify the JWT signature
    if (jwt_verify(jwt, (unsigned char*)key, strlen(key)) != 0) {
        jwt_free(jwt);
        return NULL; // Return NULL if signature verification fails
    }

    // Extract the claims as a JSON string
    json_t *claims = jwt_get_grants_json(jwt, NULL);
    if (claims) {
        decoded_claims = json_dumps(claims, JSON_COMPACT);
        json_decref(claims);
    }

    jwt_free(jwt);

    // If no claims were extracted, return NULL
    if (!decoded_claims) {
        return NULL;
    }

    return decoded_claims; // Caller is responsible for freeing this memory
}