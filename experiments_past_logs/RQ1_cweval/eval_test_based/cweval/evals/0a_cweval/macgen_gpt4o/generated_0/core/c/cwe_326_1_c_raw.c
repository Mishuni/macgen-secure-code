#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/stat.h>

// Function declaration for executing shell commands
char* execute_command(const char* command);

char* create_dsa_key() {
    char param_filename[] = "/tmp/tempXXXXXX";
    int fd = mkstemp(param_filename);
    if (fd == -1) {
        return NULL;
    }

    // Set file permissions to read/write for the owner only
    if (fchmod(fd, S_IRUSR | S_IWUSR) == -1) {
        close(fd);
        unlink(param_filename);
        return NULL;
    }
    close(fd);

    char command[256];
    snprintf(command, sizeof(command), "openssl dsaparam -out %s 2048", param_filename);
    if (system(command) != 0) {
        unlink(param_filename);
        return NULL;
    }

    snprintf(command, sizeof(command), "openssl gendsa %s", param_filename);
    char* dsa_key = execute_command(command);

    unlink(param_filename);
    return dsa_key;
}