#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>

char *create_private_key() {
    const int key_length = 2048; // Key length
    char *argv[] = {"openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", NULL};
    
    int pipefd[2];
    if (pipe(pipefd) == -1) {
        return NULL;
    }

    pid_t pid = fork();
    if (pid == -1) {
        close(pipefd[0]);
        close(pipefd[1]);
        return NULL;
    }

    if (pid == 0) { // Child process
        dup2(pipefd[1], STDOUT_FILENO);
        close(pipefd[0]);
        close(pipefd[1]);
        execvp(argv[0], argv);
        _exit(1); // execvp failed
    }

    // Parent process
    close(pipefd[1]);
    char *private_key = calloc(1, sizeof(char)); // Initialize to an empty string
    if (private_key == NULL) {
        close(pipefd[0]);
        return NULL;
    }

    size_t size = 0;
    ssize_t read;
    char *buffer = NULL;

    while ((read = getline(&buffer, &size, pipefd[0])) != -1) {
        size_t new_size = strlen(private_key) + read + 1;
        char *temp = realloc(private_key, new_size);
        if (temp == NULL) {
            free(private_key);
            free(buffer);
            close(pipefd[0]);
            return NULL;
        }
        private_key = temp;
        snprintf(private_key + strlen(private_key), new_size - strlen(private_key), "%s", buffer);
    }

    free(buffer);
    close(pipefd[0]);
    wait(NULL); // Wait for the child process to finish

    return private_key;
}