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

char *read_file_from_dir(const char *filename, const char *dir_path) {
    if (filename == NULL || dir_path == NULL) {
        return strdup("");
    }

    // Construct the full path
    size_t dir_len = strlen(dir_path);
    size_t file_len = strlen(filename);
    size_t path_length = dir_len + file_len + 2; // 1 for '/' and 1 for '\0'

    char *full_path = (char *)malloc(path_length);
    if (full_path == NULL) {
        return strdup("");
    }

    // Ensure correct path construction
    if (dir_path[dir_len - 1] == '/') {
        snprintf(full_path, path_length, "%s%s", dir_path, filename);
    } else {
        snprintf(full_path, path_length, "%s/%s", dir_path, filename);
    }

    // Resolve the full path to prevent path traversal
    char resolved_path[PATH_MAX];
    if (realpath(full_path, resolved_path) == NULL) {
        free(full_path);
        return strdup("");
    }
    free(full_path);

    // Check if the resolved path starts with the directory path
    if (strncmp(resolved_path, dir_path, dir_len) != 0 || (resolved_path[dir_len] != '/' && resolved_path[dir_len] != '\0')) {
        return strdup("");
    }

    // Open the file
    FILE *file = fopen(resolved_path, "r");
    if (file == NULL) {
        return strdup("");
    }

    // Determine file size
    if (fseek(file, 0, SEEK_END) != 0) {
        fclose(file);
        return strdup("");
    }
    long file_size = ftell(file);
    if (file_size < 0) {
        fclose(file);
        return strdup("");
    }
    rewind(file);

    // Allocate memory for file content
    char *content = (char *)malloc(file_size + 1);
    if (content == NULL) {
        fclose(file);
        return strdup("");
    }

    // Read file content
    size_t read_size = fread(content, 1, file_size, file);
    fclose(file);

    if (read_size != file_size) {
        free(content);
        return strdup("");
    }

    content[file_size] = '\0';
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
