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
#include <limits.h>
#include <errno.h>
#include <sys/stat.h>
#include <ctype.h>

char *read_file_from_dir(const char *filename, const char *dir_path) {
    // Validate filename: allow only alphanumeric characters, underscores, and a single dot
    int dot_count = 0;
    size_t filename_len = strlen(filename);
    if (filename_len == 0 || filename_len >= NAME_MAX) {
        errno = EINVAL;
        return NULL; // Invalid filename length
    }
    for (size_t i = 0; i < filename_len; ++i) {
        if (!isalnum(filename[i]) && filename[i] != '.' && filename[i] != '_') {
            errno = EINVAL;
            return NULL; // Invalid character found
        }
        if (filename[i] == '.') {
            dot_count++;
            if (i == 0 || i == filename_len - 1) {
                errno = EINVAL;
                return NULL; // Dot is at the start or end
            }
        }
    }
    if (dot_count > 1 || filename[0] == '.' || strcmp(filename, "..") == 0) {
        errno = EINVAL;
        return NULL; // More than one dot found or invalid filename
    }

    // Construct the full path
    char full_path[PATH_MAX];
    if (snprintf(full_path, sizeof(full_path), "%s/%s", dir_path, filename) < 0) {
        errno = EIO;
        return NULL; // Error in path construction
    }

    // Canonicalize the path to ensure it's safe
    char real_path[PATH_MAX];
    if (realpath(full_path, real_path) == NULL) {
        return NULL; // Error in resolving path
    }

    // Ensure the file is within the intended directory
    char real_dir_path[PATH_MAX];
    if (realpath(dir_path, real_dir_path) == NULL) {
        return NULL; // Error in resolving directory path
    }
    size_t dir_path_len = strlen(real_dir_path);
    if (real_dir_path[dir_path_len - 1] != '/') {
        if (dir_path_len + 1 >= PATH_MAX) {
            errno = ENAMETOOLONG;
            return NULL; // Directory path too long
        }
        real_dir_path[dir_path_len] = '/';
        real_dir_path[dir_path_len + 1] = '\0';
        dir_path_len++;
    }
    if (strncmp(real_path, real_dir_path, dir_path_len) != 0) {
        errno = EACCES;
        return NULL; // File is outside the intended directory
    }

    // Open the file
    FILE *file = fopen(real_path, "r");
    if (!file) {
        return NULL; // Error opening file
    }

    // Determine file size
    struct stat st;
    if (fstat(fileno(file), &st) != 0) {
        fclose(file);
        return NULL; // Error getting file size
    }

    // Check for potential integer overflow
    if (st.st_size < 0 || (size_t)st.st_size >= SIZE_MAX - 1) {
        fclose(file);
        errno = EFBIG;
        return NULL; // File size is too large
    }

    // Allocate memory for file content
    char *content = (char *)malloc(st.st_size + 1);
    if (!content) {
        fclose(file);
        errno = ENOMEM;
        return NULL; // Memory allocation failed
    }

    // Read file content
    size_t read_size = fread(content, 1, st.st_size, file);
    if (read_size != (size_t)st.st_size) {
        free(content);
        fclose(file);
        errno = EIO;
        return NULL; // Error reading file
    }

    // Null-terminate the content
    content[read_size] = '\0';

    // Close the file
    fclose(file);

    return content;
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    // Check if there are exactly two command-line arguments
    if (argc != 3) {
        return 0;
    }

    // Read the file from the directory
    char *content = read_file_from_dir(argv[1], argv[2]);
    // print the content
    printf("%s", content);

    if (content != "" && content != NULL) {
        // Free the allocated memory
        free(content);
    }

    return 0;
}
