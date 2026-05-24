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

#include <string>
#include <fstream>
#include <iostream>
#include <filesystem>
#include <stdexcept>

namespace SystemUtilities {
    std::string getCanonicalPath(const std::string &path) {
        return std::filesystem::canonical(path).string();
    }

    bool isDirectory(const std::string &path) {
        return std::filesystem::is_directory(path);
    }
}

std::string read_file_from_dir(const std::string &filename, const std::string &dir_path) {
    // Check if the directory path is empty
    if (dir_path.empty()) {
        return "";
    }

    // Validate the filename
    if (filename.empty() || filename.find("..") != std::string::npos || filename.find("/") != std::string::npos) {
        return ""; // Reject disallowed characters and path traversal
    }

    // Construct the full path
    std::string full_path = dir_path + "/" + filename;

    // Get canonical paths for validation
    std::string canonical_dir_path = SystemUtilities::getCanonicalPath(dir_path);
    std::string canonical_full_path = SystemUtilities::getCanonicalPath(full_path);

    // Ensure the file is within the specified directory
    if (!std::filesystem::exists(canonical_full_path) || !std::filesystem::is_regular_file(canonical_full_path) ||
        canonical_full_path.find(canonical_dir_path) != 0) {
        return ""; // File does not exist or is outside the allowed directory
    }

    // Read the file content
    std::ifstream file(canonical_full_path);
    if (!file.is_open()) {
        return ""; // Return empty string if file cannot be opened
    }

    std::string content((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
    return content; // Return the content of the file
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    // Check if there are exactly two command-line arguments
    if (argc != 3) {
        return 0;
    }

    // Read the file from the directory
    std::string content = read_file_from_dir(argv[1], argv[2]);
    // print the content
    std::cout << content;

    return 0;
}
