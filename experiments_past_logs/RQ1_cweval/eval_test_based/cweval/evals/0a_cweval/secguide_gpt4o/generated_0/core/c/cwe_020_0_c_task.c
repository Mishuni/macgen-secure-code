#include <archive_entry.h>
#include <jwt.h>
#include <errno.h>
#include <sys/wait.h>
#include <libxml/xpath.h>
#include <sqlite3.h>
#include <archive.h>
#include <ctype.h>
#include <libxml/parser.h>
#include <openssl/evp.h>
#include <openssl/des.h>
#include <openssl/aes.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <openssl/md5.h>
#include <stdlib.h>
#include <libgen.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdbool.h>
#include <time.h>
#include <string.h>
#include <openssl/sha.h>
#include <regex.h>
#include <unistd.h>
#include <openssl/rand.h>
#include <archive.h>
#include <archive_entry.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <jwt.h>
#include <libgen.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/evp.h>
#include <openssl/md5.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <regex.h>
#include <sqlite3.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <regex.h>
#include <netdb.h>
#include <arpa/inet.h>

bool is_valid_url(const char* url) {
    regex_t regex;
    int reti;
    // Improved regex to handle more URL cases including query parameters and fragments
    reti = regcomp(&regex, "^(https?|ftp)://[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,6}(:[0-9]+)?(/.*)?$", REG_EXTENDED);
    if (reti) {
        return false;
    }
    reti = regexec(&regex, url, 0, NULL, 0);
    regfree(&regex);
    return !reti;
}

bool is_subdomain(const char* host, const char* domain) {
    size_t host_len = strlen(host);
    size_t domain_len = strlen(domain);
    if (host_len < domain_len) {
        return false;
    }
    if (strcasecmp(host + host_len - domain_len, domain) != 0) {
        return false;
    }
    if (host_len == domain_len) {
        return true;
    }
    return host[host_len - domain_len - 1] == '.';
}

char* get_target_for_redirect(const char* target, const char* domain) {
    if (target == NULL || domain == NULL) {
        return NULL;
    }

    if (!is_valid_url(target)) {
        return NULL;
    }

    char* target_copy = strdup(target);
    if (target_copy == NULL) {
        return NULL;
    }

    struct addrinfo hints, *res;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    char* host_start = strstr(target_copy, "://");
    if (host_start == NULL) {
        free(target_copy);
        return NULL;
    }
    host_start += 3;

    char* path_start = strchr(host_start, '/');
    if (path_start != NULL) {
        *path_start = '\0';
    }

    if (getaddrinfo(host_start, NULL, &hints, &res) != 0) {
        free(target_copy);
        return NULL;
    }

    bool valid = is_subdomain(host_start, domain);
    freeaddrinfo(res);
    free(target_copy);

    if (valid) {
        return strdup(target);
    } else {
        size_t domain_url_len = strlen(domain) + 9; // "https://" + null terminator
        char* domain_url = (char*)malloc(domain_url_len);
        if (domain_url == NULL) {
            return NULL;
        }
        snprintf(domain_url, domain_url_len, "https://%s", domain);
        return domain_url;
    }
}

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <target_url> <domain>\n", argv[0]);
        return 1;
    }

    char* result = get_target_for_redirect(argv[1], argv[2]);
    printf("%s", result);

    free(result);
    return 0;
}
