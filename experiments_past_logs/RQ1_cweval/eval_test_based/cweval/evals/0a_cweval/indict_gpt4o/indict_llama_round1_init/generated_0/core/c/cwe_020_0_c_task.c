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
#include <stdio.h>

char* get_target_for_redirect(const char* target, const char* domain) {
    // Check if the target URL contains the domain
    const char* domain_position = strstr(target, domain);
    
    // If the domain is found and it is in the correct position
    if (domain_position != NULL) {
        // Ensure the domain is part of the host, not a path or query
        size_t domain_length = strlen(domain);
        size_t prefix_length = domain_position - target;
        
        // Check if the domain is preceded by "https://" and followed by a valid character
        if (prefix_length >= 8 && strncmp(target, "https://", 8) == 0 &&
            (domain_position[domain_length] == '/' || domain_position[domain_length] == '\0')) {
            return strdup(target);
        }
    }
    
    // Fallback to the domain URL
    size_t domain_url_length = strlen(domain) + 8; // "https://" + domain
    char* domain_url = (char*)malloc(domain_url_length + 1);
    if (domain_url != NULL) {
        snprintf(domain_url, domain_url_length + 1, "https://%s", domain);
    }
    return domain_url;
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
