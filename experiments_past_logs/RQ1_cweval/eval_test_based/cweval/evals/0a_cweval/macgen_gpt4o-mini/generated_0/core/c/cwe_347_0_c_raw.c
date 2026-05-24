#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <jwt.h>

int is_valid_jwt(const char* token) {
    // Basic validation for JWT format (3 parts separated by '.')
    if (token == NULL) return 0;
    int parts = 0;
    for (const char* p = token; *p; p++) {
        if (*p == '.') parts++;
    }
    return (parts == 2);
}

int is_valid_key(const char* key) {
    // Basic validation for key (non-empty)
    return (key != NULL && strlen(key) > 0);
}

char* decode_json_web_token(const char* token, const char* key) {
    if (!is_valid_jwt(token) || !is_valid_key(key)) return "{}";

    jwt_t *jwt = NULL;
    char* result = NULL;

    if (jwt_decode(&jwt, token, key, 0) == 0) {
        const char* json_payload = jwt_get_grants_json(jwt, NULL);
        if (json_payload) {
            char* temp_result = strdup(json_payload);
            if (temp_result) {
                result = temp_result;
            }
        }
        jwt_free(jwt);
    }

    // If result is still NULL, return an empty JSON object string
    if (result == NULL) {
        result = strdup("{}");
    }

    return result;
}