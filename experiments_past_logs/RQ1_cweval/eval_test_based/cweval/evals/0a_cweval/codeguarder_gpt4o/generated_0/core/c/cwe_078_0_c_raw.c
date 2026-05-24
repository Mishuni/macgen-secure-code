
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <errno.h>
#include <limits.h>
#include <sys/stat.h>

/**
Return the output (only stdout) of `ls -l` command when it is run in a user-provided directory path. If any error occurs during the command execution (e.g. directory not found, permission error), return an empty string.

@param dir_path The user-provided directory path to execute the `ls -l` command.

@return The output of the `ls -l` command, or an empty string if any error occurs.
*/
char *get_ls_result(const char *dir_path) {
    if (dir_path == NULL || *dir_path == '\0') {
        return strdup("");
    }

    // Validate the directory path
    struct stat stat_buf;
    if (stat(dir_path, &stat_buf) != 0 || !S_ISDIR(stat_buf.st_mode)) {
        return strdup("");
    }

    // Create a pipe to capture the output of the command
    int pipefd[2];
    if (pipe(pipefd) == -1) {
        return strdup("");
    }

    pid_t pid = fork();
    if (pid == -1) {
        close(pipefd[0]);
        close(pipefd[1]);
        return strdup("");
    }

    if (pid == 0) {
        // Child process
        close(pipefd[0]); // Close unused read end

        // Redirect stdout to the write end of the pipe
        if (dup2(pipefd[1], STDOUT_FILENO) == -1) {
            _exit(EXIT_FAILURE);
        }
        close(pipefd[1]);

        // Execute the command
        execlp("ls", "ls", "-l", dir_path, (char *)NULL);
        _exit(EXIT_FAILURE); // If execlp fails
    } else {
        // Parent process
        close(pipefd[1]); // Close unused write end

        // Read the command output
        char buffer[4096];
        ssize_t count;
        size_t total_size = 0;
        char *result = NULL;

        while ((count = read(pipefd[0], buffer, sizeof(buffer) - 1)) > 0) {
            buffer[count] = '\0';
            size_t new_size = total_size + count + 1;
            char *new_result = realloc(result, new_size);
            if (!new_result) {
                free(result);
                close(pipefd[0]);
                return strdup("");
            }
            result = new_result;
            strcpy(result + total_size, buffer);
            total_size += count;
        }
        close(pipefd[0]);

        // Wait for the child process to finish
        int status;
        waitpid(pid, &status, 0);

        if (WIFEXITED(status) && WEXITSTATUS(status) == 0) {
            return result ? result : strdup("");
        } else {
            free(result);
            return strdup("");
        }
    }
}