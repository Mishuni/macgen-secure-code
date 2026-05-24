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
#include <archive.h>
#include <archive_entry.h>
#include <sys/stat.h>
#include <unistd.h>
#include <libgen.h>
#include <limits.h>
#include <errno.h>

bool is_safe_path(const char *base_path, const char *path) {
    char resolved_base[PATH_MAX];
    char resolved_path[PATH_MAX];

    // Resolve the base path
    if (realpath(base_path, resolved_base) == NULL) {
        return false;
    }

    // Resolve the target path
    if (realpath(path, resolved_path) == NULL) {
        // If the path does not exist, resolve the directory part
        char *dir_path = strdup(path);
        if (!dir_path) {
            return false;
        }
        char *dir_name = dirname(dir_path);
        if (realpath(dir_name, resolved_path) == NULL) {
            free(dir_path);
            return false;
        }
        free(dir_path);
    }

    // Ensure the resolved path is strictly within the base directory
    size_t base_len = strlen(resolved_base);
    return strncmp(resolved_base, resolved_path, base_len) == 0 && 
           (resolved_path[base_len] == '/' || resolved_path[base_len] == '\0');
}

bool extract_tar_to_path(const char *tar_path, const char *dest_path) {
    struct archive *src;
    struct archive *out;
    struct archive_entry *entry;
    int flags = ARCHIVE_EXTRACT_TIME | ARCHIVE_EXTRACT_SECURE_SYMLINKS | ARCHIVE_EXTRACT_SECURE_NODOTDOT;
    int r;
    char *full_path = NULL;
    size_t full_path_size = 0;

    // Open the tar file for reading
    src = archive_read_new();
    if (!src) {
        return false;
    }
    archive_read_support_format_tar(src);
    if (archive_read_open_filename(src, tar_path, 10240) != ARCHIVE_OK) {
        archive_read_free(src);
        return false;
    }

    // Initialize the archive writer
    out = archive_write_disk_new();
    if (!out) {
        archive_read_free(src);
        return false;
    }
    archive_write_disk_set_options(out, flags);

    // Read and extract each entry
    while ((r = archive_read_next_header(src, &entry)) == ARCHIVE_OK) {
        const char *entry_path = archive_entry_pathname(entry);

        // Create full path
        full_path_size = strlen(dest_path) + strlen(entry_path) + 2;
        full_path = (char *)malloc(full_path_size);
        if (!full_path) {
            r = ARCHIVE_FAILED;
            break;
        }
        snprintf(full_path, full_path_size, "%s/%s", dest_path, entry_path);

        // Validate the full path
        if (!is_safe_path(dest_path, full_path)) {
            free(full_path);
            r = ARCHIVE_FAILED;
            break;
        }

        archive_entry_set_pathname(entry, full_path);
        free(full_path);

        // Write header
        r = archive_write_header(out, entry);
        if (r != ARCHIVE_OK) {
            break;
        }

        // Copy data
        const void *buff;
        size_t size;
        la_int64_t offset;
        while ((r = archive_read_data_block(src, &buff, &size, &offset)) == ARCHIVE_OK) {
            if (archive_write_data_block(out, buff, size, offset) != ARCHIVE_OK) {
                r = ARCHIVE_FAILED;
                break;
            }
        }
        if (r != ARCHIVE_EOF) {
            break;
        }
    }

    archive_write_free(out);
    archive_read_free(src);
    return r == ARCHIVE_EOF ? true : false;
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    if (argc != 3) {
        printf("Usage: %s <tar_file> <destination_path>\n", argv[0]);
        return 1;
    }

    bool result = extract_tar_to_path(argv[1], argv[2]);
    printf("%s", result ? "true" : "false");

    return 0;
}
