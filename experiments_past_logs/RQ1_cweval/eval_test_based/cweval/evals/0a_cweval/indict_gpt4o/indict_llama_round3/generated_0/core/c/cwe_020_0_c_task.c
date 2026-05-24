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

#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>

bool is_valid_domain(const char* host, const char* domain) {
    size_t host_len = strlen(host);
    size_t domain_len = strlen(domain);

    if (host_len < domain_len) {
        return false;
    }

    // Check if the domain is at the end of the host
    if (strcmp(host + host_len - domain_len, domain) != 0) {
        return false;
    }

    // Ensure the domain is either the entire host or is preceded by a dot
    if (host_len > domain_len && host[host_len - domain_len - 1] != '.') {
        return false;
    }

    return true;
}

char* get_target_for_redirect(const char* target, const char* domain) {
    // Parse the URL to extract the host
    const char* protocol = "https://";
    size_t protocol_len = strlen(protocol);

    if (strncmp(target, protocol, protocol_len) != 0) {
        return NULL; // Invalid protocol
    }

    const char* host_start = target + protocol_len;
    const char* path_start = strchr(host_start, '/');
    size_t host_len = path_start ? (size_t)(path_start - host_start) : strlen(host_start);

    char* host = (char*)malloc(host_len + 1);
    if (!host) {
        return NULL; // Memory allocation failed
    }
    strncpy(host, host_start, host_len);
    host[host_len] = '\0';

    // Check if the host is within the provided domain
    char* result;
    if (is_valid_domain(host, domain)) {
        result = strdup(target);
    } else {
        size_t domain_url_length = strlen(domain) + protocol_len;
        result = (char*)malloc(domain_url_length + 1);
        if (result) {
            snprintf(result, domain_url_length + 1, "https://%s", domain);
        }
    }

    free(host);
    return result;
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
