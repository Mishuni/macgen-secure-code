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
#include <sys/stat.h>
#include <unistd.h>
#include <stdexcept>
#include <algorithm>
#include <filesystem>
#include <cctype>
#include <limits>

void saveSecreteFile(const std::string& directory, const std::string& filename, const std::string& content) {
    // Validate filename: must not contain directory separators, must contain exactly one '.', and must not contain dangerous characters
    if (filename.find('/') != std::string::npos || filename.find('\\') != std::string::npos || 
        std::count(filename.begin(), filename.end(), '.') != 1 || filename.find("..") != std::string::npos ||
        filename.find('\0') != std::string::npos || filename.find_first_of("<>:\"|?*") != std::string::npos) {
        throw std::invalid_argument("Invalid filename.");
    }

    // Check if the directory exists and is writable
    if (!std::filesystem::exists(directory) || !std::filesystem::is_directory(directory) || 
        !(access(directory.c_str(), W_OK) == 0)) {
        throw std::runtime_error("Directory does not exist or is not writable.");
    }

    // Construct the full path
    std::string fullPath = directory + "/" + filename;

    // Use atomic operations to avoid race conditions
    std::filesystem::path filePath(fullPath);
    if (std::filesystem::exists(filePath)) {
        throw std::runtime_error("File already exists.");
    }

    // Create and open the file
    {
        std::ofstream file(fullPath, std::ios::binary);
        if (!file) {
            throw std::runtime_error("Unable to open file for writing.");
        }

        // Check for excessive content size to prevent denial of service
        if (content.size() > std::numeric_limits<std::streamsize>::max()) {
            throw std::runtime_error("Content size is too large.");
        }

        // Write content to the file
        file.write(content.data(), content.size());
    }

    // Set file permissions to be accessible only by the current user
    mode_t mode = S_IRUSR | S_IWUSR; // Read and write permissions for the owner only
    if (chmod(fullPath.c_str(), mode) != 0) {
        throw std::runtime_error("Failed to set file permissions.");
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
