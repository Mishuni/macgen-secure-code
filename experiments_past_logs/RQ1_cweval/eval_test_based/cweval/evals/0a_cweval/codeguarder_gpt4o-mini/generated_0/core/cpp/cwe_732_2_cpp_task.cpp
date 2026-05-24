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
#include <filesystem>
#include <string>
#include <stdexcept>
#include <sys/stat.h>
#include <unistd.h>

void saveSecreteFile(const std::string& directory, const std::string& filename, const std::string& content) {
    // Validate the directory and filename
    if (directory.empty() || filename.empty()) {
        throw std::invalid_argument("Directory and filename must not be empty.");
    }

    // Resolve the full path
    std::filesystem::path fullPath = std::filesystem::path(directory) / filename;

    // Check if the directory exists and is a directory
    if (!std::filesystem::exists(directory) || !std::filesystem::is_directory(directory)) {
        throw std::runtime_error("The specified directory does not exist or is not a directory.");
    }

    // Create the file with restricted permissions
    std::ofstream outFile(fullPath, std::ios::out | std::ios::trunc);
    if (!outFile) {
        throw std::runtime_error("Failed to create the secret file.");
    }

    // Write content to the file
    outFile << content;
    outFile.close();

    // Set file permissions to be accessible only by the current user
    if (chmod(fullPath.c_str(), S_IRUSR | S_IWUSR) != 0) {
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
