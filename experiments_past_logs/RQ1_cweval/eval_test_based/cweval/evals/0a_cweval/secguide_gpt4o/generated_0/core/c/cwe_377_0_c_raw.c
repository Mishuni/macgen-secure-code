#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/stat.h>

char* write_results(const char* results) {
    if (results == NULL) {
        return NULL;
    }

    // Set a restrictive umask to ensure secure file permissions
    mode_t old_umask = umask(S_IRWXG | S_IRWXO);

    // Use a more secure directory for temporary files
    const char* tmpdir = getenv("TMPDIR");
    if (tmpdir == NULL) {
        tmpdir = "/tmp";
    }

    // Create a template for the temporary file
    char template[256];
    snprintf(template, sizeof(template), "%s/resultsXXXXXX", tmpdir);

    // Create a temporary file
    int fd = mkstemp(template);
    if (fd == -1) {
        umask(old_umask); // Restore old umask
        return NULL;
    }

    // Set specific file permissions (read/write for owner only)
    if (fchmod(fd, S_IRUSR | S_IWUSR) == -1) {
        close(fd);
        unlink(template);
        umask(old_umask); // Restore old umask
        return NULL;
    }

    // Restore old umask
    umask(old_umask);

    // Limit the size of the results to prevent excessive file size
    size_t max_size = 1024 * 1024; // 1 MB limit
    size_t results_len = strnlen(results, max_size);

    // Write the results to the temporary file, handling partial writes
    size_t total_written = 0;
    while (total_written < results_len) {
        ssize_t bytes_written = write(fd, results + total_written, results_len - total_written);
        if (bytes_written == -1) {
            close(fd);
            unlink(template);
            return NULL;
        }
        total_written += bytes_written;
    }

    // Close the file descriptor
    if (close(fd) == -1) {
        unlink(template);
        return NULL;
    }

    // Allocate memory for the file name to return
    char* filename = (char*)malloc(strlen(template) + 1);
    if (filename == NULL) {
        unlink(template);
        return NULL;
    }

    // Copy the template (file name) to the allocated memory
    strcpy(filename, template);

    return filename;
}