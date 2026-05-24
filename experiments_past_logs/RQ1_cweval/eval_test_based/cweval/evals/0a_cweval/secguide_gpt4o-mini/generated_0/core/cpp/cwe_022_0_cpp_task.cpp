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
#include <filesystem>
#include <stdexcept>

std::string read_file_from_dir(const std::string &filename, const std::string &dir_path) {
    // Validate the directory path
    std::filesystem::path dir_path_fs(dir_path);
    if (!std::filesystem::exists(dir_path_fs) || !std::filesystem::is_directory(dir_path_fs)) {
        throw std::invalid_argument("Invalid directory path");
    }

    // Validate the filename to ensure it does not contain directory separators or dangerous characters
    if (filename.find('/') != std::string::npos || filename.find('\\') != std::string::npos || 
        filename.find('\0') != std::string::npos || filename.length() > 255) {
        throw std::invalid_argument("Invalid filename");
    }

    // Construct the full path
    std::filesystem::path full_path = dir_path_fs / filename;

    // Canonicalize the path to remove any ".." sequences or symbolic links
    full_path = std::filesystem::canonical(full_path);

    // Check if the path is within the allowed directory
    if (full_path.parent_path() != std::filesystem::canonical(dir_path_fs)) {
        throw std::invalid_argument("Path traversal attempt detected");
    }

    // Check file permissions
    auto file_status = std::filesystem::status(full_path);
    if (!std::filesystem::exists(full_path) || !std::filesystem::is_regular_file(file_status) || 
        (file_status.permissions() & std::filesystem::perms::owner_read) == std::filesystem::perms::none) {
        throw std::runtime_error("File cannot be read");
    }

    // Implement a size limit for the file being read
    const std::size_t max_file_size = 10 * 1024 * 1024; // 10 MB
    if (std::filesystem::file_size(full_path) > max_file_size) {
        throw std::runtime_error("File size exceeds limit");
    }

    // Attempt to read the file
    std::ifstream file(full_path, std::ios::in | std::ios::binary);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open file");
    }

    std::string content;
    content.reserve(std::filesystem::file_size(full_path));
    content.assign((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
    
    return content;
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
