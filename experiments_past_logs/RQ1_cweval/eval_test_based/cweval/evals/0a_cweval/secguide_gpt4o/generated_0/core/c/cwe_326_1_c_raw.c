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