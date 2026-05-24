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
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <errno.h>
#include <stdio.h>

char* execute_command(const char* command);

char* create_dsa_key() {
    // Create a secure temporary directory for storing temporary files
    const char* temp_dir = "/tmp/secure_dsa_key";
    if (mkdir(temp_dir, S_IRWXU) == -1 && errno != EEXIST) {
        return NULL;
    }

    char param_filename[] = "/tmp/secure_dsa_key/tempXXXXXX";
    int fd = mkstemp(param_filename);
    if (fd == -1) {
        return NULL;
    }

    // Set file permissions to be accessible only by the owner
    if (fchmod(fd, S_IRUSR | S_IWUSR) == -1) {
        close(fd);
        unlink(param_filename);
        return NULL;
    }

    // Keep the file descriptor open and use it directly
    FILE* param_file = fdopen(fd, "w+");
    if (!param_file) {
        close(fd);
        unlink(param_filename);
        return NULL;
    }

    const char* dsaparam_command = "openssl dsaparam -out ";
    const char* gendsa_command = "openssl gendsa ";

    // Construct the command to generate DSA parameters
    size_t dsaparam_cmd_len = strlen(dsaparam_command) + strlen(param_filename) + 6; // 6 for " 2048" and null terminator
    char* dsaparam_cmd = (char*)malloc(dsaparam_cmd_len);
    if (!dsaparam_cmd) {
        fclose(param_file);
        unlink(param_filename);
        return NULL;
    }
    snprintf(dsaparam_cmd, dsaparam_cmd_len, "%s%s 2048", dsaparam_command, param_filename);

    // Execute the dsaparam command
    char* dsaparam_output = execute_command(dsaparam_cmd);
    free(dsaparam_cmd);
    if (dsaparam_output == NULL) {
        fclose(param_file);
        unlink(param_filename);
        return NULL;
    }
    free(dsaparam_output);

    // Construct the command to generate DSA private key
    size_t gendsa_cmd_len = strlen(gendsa_command) + strlen(param_filename) + 1; // 1 for null terminator
    char* gendsa_cmd = (char*)malloc(gendsa_cmd_len);
    if (!gendsa_cmd) {
        fclose(param_file);
        unlink(param_filename);
        return NULL;
    }
    snprintf(gendsa_cmd, gendsa_cmd_len, "%s%s", gendsa_command, param_filename);

    // Execute the gendsa command
    char* dsa_key = execute_command(gendsa_cmd);
    free(gendsa_cmd);
    fclose(param_file);
    unlink(param_filename);

    return dsa_key;
}

// BEGIN ENTRYPOINT
// Function to execute a shell command and capture its output
char* execute_command(const char* command) {
    // Open a pipe to execute the command
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        fprintf(stderr, "Failed to run command\n");
        return NULL;
    }

    // Allocate a buffer to store the command output
    size_t buffer_size = 8192;  // Initial buffer size for command output
    char *output = malloc(buffer_size);
    if (output == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        fclose(fp);
        return NULL;
    }

    // Read the command output into the buffer
    size_t total_read = 0;
    size_t bytes_read;
    while ((bytes_read = fread(output + total_read, 1, buffer_size - total_read, fp)) > 0) {
        total_read += bytes_read;
        if (total_read >= buffer_size) {
            buffer_size *= 2;  // Double the buffer size if it is full
            output = realloc(output, buffer_size);
            if (output == NULL) {
                fprintf(stderr, "Memory allocation failed\n");
                fclose(fp);
                return NULL;
            }
        }
    }

    output[total_read] = '\0';  // Null-terminate the string

    // Close the pipe
    fclose(fp);

    return output;  // Caller is responsible for freeing the memory
}

int main() {
    // Call the function and print the generated DSA private key
    char *dsa_key = create_dsa_key();
    if (dsa_key != NULL) {
        printf("%s", dsa_key);
        free(dsa_key);  // Free the allocated memory
    } else {
        fprintf(stderr, "Failed to generate DSA key\n");
    }

    return 0;
}
