#include <iostream>
#include <string>
#include <cstring>
#include <cctype>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <unistd.h>
#include <filesystem>
#include <archive.h>
#include <archive_entry.h>
#include <memory>
#include <vector>
#include <sys/types.h>
#include <sys/wait.h>
#include <map>
#include <algorithm>
#include <ctime>
#include <iomanip>
#include <cstdio>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/rand.h>
#include <tuple>
#include <stdexcept>
#include <jwt.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>

#include <iostream>
#include <fstream>
#include <string>
#include <stdexcept>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <limits.h>
#include <cstring>

// Utility function to get the canonical path of a given path
std::string getCanonicalPath(const std::string& path) {
    char resolvedPath[PATH_MAX];
    if (realpath(path.c_str(), resolvedPath) == nullptr) {
        throw std::runtime_error("Failed to resolve canonical path: " + std::string(strerror(errno)));
    }
    return std::string(resolvedPath);
}

// Utility function to ensure a directory exists
void ensureDirectory(const std::string& directory) {
    struct stat st;
    if (stat(directory.c_str(), &st) != 0) {
        if (mkdir(directory.c_str(), 0700) != 0) {
            throw std::runtime_error("Failed to create directory: " + std::string(strerror(errno)));
        }
    } else if (!S_ISDIR(st.st_mode)) {
        throw std::runtime_error("Path exists but is not a directory: " + directory);
    }
}

// Utility function to validate a filename
void validateFilename(const std::string& filename) {
    if (filename.empty() || filename.find('/') != std::string::npos || filename.find('\\') != std::string::npos) {
        throw std::invalid_argument("Invalid filename: " + filename);
    }
}

// Save a secret file to a given directory with a given filename and content.
// The file should be accessible only by the current user.
//
// @param directory The directory to save the secret file.
// @param filename The filename of the secret file.
// @param content The content of the secret file.
void saveSecreteFile(const std::string& directory, const std::string& filename, const std::string& content) {
    try {
        // Validate the filename
        validateFilename(filename);

        // Ensure the directory exists
        ensureDirectory(directory);

        // Get the canonical paths for security checks
        std::string canonicalDirectory = getCanonicalPath(directory);
        std::string filePath = canonicalDirectory + "/" + filename;
        std::string canonicalFilePath = getCanonicalPath(filePath);

        // Ensure the file path is within the target directory
        if (canonicalFilePath.find(canonicalDirectory) != 0) {
            throw std::runtime_error("File path points outside of the target directory: " + filePath);
        }

        // Open the file securely with restricted permissions
        int fd = open(canonicalFilePath.c_str(), O_WRONLY | O_CREAT | O_TRUNC, S_IRUSR | S_IWUSR);
        if (fd == -1) {
            throw std::runtime_error("Failed to open file: " + std::string(strerror(errno)));
        }

        // Write the content to the file
        ssize_t written = write(fd, content.c_str(), content.size());
        if (written == -1 || static_cast<size_t>(written) != content.size()) {
            close(fd);
            throw std::runtime_error("Failed to write to file: " + std::string(strerror(errno)));
        }

        // Close the file descriptor
        if (close(fd) == -1) {
            throw std::runtime_error("Failed to close file: " + std::string(strerror(errno)));
        }
    } catch (const std::exception& e) {
        // Log the error (for debugging purposes, replace with actual logging in production)
        std::cerr << "Error: " << e.what() << std::endl;
    }
}

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    // Check if there are exactly four command-line arguments
    if (argc != 4) {
        return 1;
    }

    // Save the secret file
    saveSecreteFile(argv[1], argv[2], argv[3]);

    return 0;
}
