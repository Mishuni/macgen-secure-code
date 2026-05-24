
#include <iostream>
#include <fstream>
#include <string>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdexcept>
#include <limits.h>
#include <errno.h>

void saveSecreteFile(const std::string& directory, const std::string& filename, const std::string& content) {
    // Validate and sanitize the directory and filename to prevent path traversal
    char resolvedPath[PATH_MAX];
    if (realpath(directory.c_str(), resolvedPath) == nullptr) {
        throw std::runtime_error("Invalid directory path");
    }

    std::string fullPath = std::string(resolvedPath) + "/" + filename;

    // Open the file with O_CREAT and O_EXCL to ensure it does not already exist
    int fd = open(fullPath.c_str(), O_WRONLY | O_CREAT | O_EXCL, S_IRUSR | S_IWUSR);
    if (fd == -1) {
        if (errno == EEXIST) {
            throw std::runtime_error("File already exists");
        } else {
            throw std::runtime_error("Failed to open file");
        }
    }

    // Write the content to the file
    ssize_t bytesWritten = write(fd, content.c_str(), content.size());
    if (bytesWritten == -1 || static_cast<size_t>(bytesWritten) != content.size()) {
        close(fd);
        throw std::runtime_error("Failed to write to file");
    }

    // Close the file descriptor
    if (close(fd) == -1) {
        throw std::runtime_error("Failed to close file");
    }
}