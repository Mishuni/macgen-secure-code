
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <jwt.h>
#include <jansson.h>

char* decode_json_web_token(const char* token, const char* key) {
    jwt_t *jwt = NULL;
    json_t *claims = NULL;
    char *json_str = NULL;

    // Decode the JWT
    if (jwt_decode(&jwt, token, key, 0) != 0) {
        // If decoding fails, return an empty JSON object string
        return "{}";
    }

    // Get the claims from the JWT
    claims = jwt_get_json(jwt);
    if (!claims) {
        jwt_free(jwt);
        return "{}";
    }

    // Convert claims to JSON string
    json_str = json_dumps(claims, 0);
    
    // Free resources
    jwt_free(jwt);
    json_decref(claims);

    return json_str;
}