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
#include <unistd.h>
#include <sys/stat.h>
#include <limits.h>

void save_secrete_file(const char *directory, const char *filename, const char *content) {
    long int path_max;
    char *real_output_directory;
    char *real_filename;
    FILE *file;
    size_t content_length = strlen(content);
    int success = 1;

    // Validate input parameters
    if (directory == NULL || filename == NULL || content == NULL) {
        fprintf(stderr, "Invalid input parameters.\n");
        return;
    }

    // Get maximum path length
    path_max = pathconf(directory, _PC_PATH_MAX);
    if (path_max <= 0) {
        path_max = PATH_MAX; // Fallback to a default value
    }

    // Allocate memory for the real paths
    real_output_directory = malloc(path_max);
    real_filename = malloc(path_max);
    if (real_output_directory == NULL || real_filename == NULL) {
        fprintf(stderr, "Unable to allocate memory.\n");
        success = 0;
        goto exit;
    }

    // Resolve the real paths
    if (realpath(directory, real_output_directory) == NULL || 
        realpath(filename, real_filename) == NULL) {
        fprintf(stderr, "Failed to resolve paths.\n");
        success = 0;
        goto exit;
    }

    // Check for directory traversal attack
    if (strncmp(real_filename, real_output_directory, strlen(real_output_directory)) != 0) {
        fprintf(stderr, "Possible directory traversal attack for: %s\n", filename);
        success = 0;
        goto exit;
    }

    // Create the file in the specified directory
    char full_path[PATH_MAX];
    snprintf(full_path, sizeof(full_path), "%s/%s", real_output_directory, real_filename);

    // Open the file for writing
    file = fopen(full_path, "w");
    if (file == NULL) {
        fprintf(stderr, "Failed to open file for writing: %s\n", full_path);
        success = 0;
        goto exit;
    }

    // Write content to the file
    if (fwrite(content, sizeof(char), content_length, file) != content_length) {
        fprintf(stderr, "Failed to write content to file: %s\n", full_path);
        success = 0;
    }

    // Close the file
    fclose(file);

    // Set file permissions to be accessible only by the current user
    if (chmod(full_path, S_IRUSR | S_IWUSR) != 0) {
        fprintf(stderr, "Failed to set file permissions for: %s\n", full_path);
        success = 0;
    }

exit:
    if (!success) {
        fprintf(stderr, "Failed to save secret file '%s'.\n", full_path);
    }
    free(real_filename);
    free(real_output_directory);
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
