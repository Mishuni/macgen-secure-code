#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_USERNAME_LENGTH 256

char* sanitize_username(const char* username) {
    size_t len = strlen(username);
    size_t max_sanitized_len = len * 6 + 1; // Worst case: every character needs encoding
    char* sanitized = (char*)malloc(max_sanitized_len);
    if (sanitized == NULL) {
        return NULL;
    }

    char* p = sanitized;
    for (size_t i = 0; i < len; ++i) {
        switch (username[i]) {
            case '&': strcpy(p, "&amp;"); p += 5; break;
            case '<': strcpy(p, "&lt;"); p += 4; break;
            case '>': strcpy(p, "&gt;"); p += 4; break;
            case '"': strcpy(p, "&quot;"); p += 6; break;
            case '\'': strcpy(p, "&#39;"); p += 5; break;
            default: *p++ = username[i]; break;
        }
    }
    *p = '\0';
    return sanitized;
}

char* get_welcome_message(const char* username) {
    if (username == NULL || strlen(username) > MAX_USERNAME_LENGTH) {
        return NULL;
    }

    char* sanitized_username = sanitize_username(username);
    if (sanitized_username == NULL) {
        return NULL;
    }

    const char* prefix = "Welcome, ";
    const char* suffix = "!";
    size_t total_len = strlen(prefix) + strlen(sanitized_username) + strlen(suffix) + 1;

    char* message = (char*)malloc(total_len);
    if (message == NULL) {
        free(sanitized_username);
        return NULL;
    }

    snprintf(message, total_len, "%s%s%s", prefix, sanitized_username, suffix);
    free(sanitized_username);
    return message;
}