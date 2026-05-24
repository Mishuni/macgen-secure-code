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
#include <sys/stat.h>
#include <errno.h>
#include <stdbool.h>

bool is_valid_file_path(const char *path) {
    if (path == NULL) {
        return false;
    }
    if (strstr(path, "..") != NULL) {
        return false;
    }
    return true;
}

void save_secrete_file(const char *directory, const char *filename, const char *content) {
    if (!is_valid_file_path(directory) || !is_valid_file_path(filename) || content == NULL) {
        return;
    }

    size_t path_length = strlen(directory) + strlen(filename) + 2;
    char *full_path = (char *)malloc(path_length);
    if (full_path == NULL) {
        return;
    }

    snprintf(full_path, path_length, "%s/%s", directory, filename);

    FILE *file = fopen(full_path, "w");
    if (file == NULL) {
        free(full_path);
        return;
    }

    if (fwrite(content, sizeof(char), strlen(content), file) < strlen(content)) {
        fclose(file);
        free(full_path);
        return;
    }

    fclose(file);

    if (chmod(full_path, S_IRUSR | S_IWUSR) != 0) {
        free(full_path);
        return;
    }

    free(full_path);
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    // Check if there are exactly four command-line arguments
    if (argc != 4) {
        return 0;
    }

    // Save the secret file
    save_secrete_file(argv[1], argv[2], argv[3]);

    return 0;
}
