#include <string>
#include <fstream>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdexcept>
#include <cerrno>
#include <cstring>
#include <limits.h>
#include <libgen.h>
#include <vector>

void saveSecreteFile(const std::string& directory, const std::string& filename, const std::string& content) {
    // Validate directory and filename inputs
    if (directory.empty() || filename.empty()) {
        throw std::invalid_argument("Invalid directory or filename");
    }

    // Resolve absolute paths to prevent directory traversal
    char resolvedPath[PATH_MAX];
    if (realpath(directory.c_str(), resolvedPath) == nullptr) {
        throw std::runtime_error("Failed to resolve directory path: " + std::string(strerror(errno)));
    }
    std::string resolvedDirectory(resolvedPath);

    // Set umask to ensure correct permissions
    mode_t oldUmask = umask(0077);

    // Create the directory if it doesn't exist
    if (mkdir(resolvedDirectory.c_str(), 0700) == -1 && errno != EEXIST) {
        umask(oldUmask); // Restore old umask
        throw std::runtime_error("Failed to create directory: " + std::string(strerror(errno)));
    }

    // Construct the full file path
    std::string filePath = resolvedDirectory + "/" + filename;

    // Write the content to a temporary file first
    std::string tempFilePath = filePath + ".tmp";
    int tempFd = open(tempFilePath.c_str(), O_WRONLY | O_CREAT | O_TRUNC | O_EXCL, S_IRUSR | S_IWUSR);
    if (tempFd == -1) {
        umask(oldUmask); // Restore old umask
        throw std::runtime_error("Failed to open temporary file: " + std::string(strerror(errno)));
    }

    if (write(tempFd, content.c_str(), content.size()) == -1) {
        close(tempFd);
        umask(oldUmask); // Restore old umask
        throw std::runtime_error("Failed to write to temporary file: " + std::string(strerror(errno)));
    }

    // Close the temporary file descriptor
    if (close(tempFd) == -1) {
        umask(oldUmask); // Restore old umask
        throw std::runtime_error("Failed to close temporary file: " + std::string(strerror(errno)));
    }

    // Atomically rename the temporary file to the target file
    if (rename(tempFilePath.c_str(), filePath.c_str()) == -1) {
        unlink(tempFilePath.c_str()); // Clean up the temporary file
        umask(oldUmask); // Restore old umask
        throw std::runtime_error("Failed to rename temporary file: " + std::string(strerror(errno)));
    }

    // Restore the old umask
    umask(oldUmask);
}