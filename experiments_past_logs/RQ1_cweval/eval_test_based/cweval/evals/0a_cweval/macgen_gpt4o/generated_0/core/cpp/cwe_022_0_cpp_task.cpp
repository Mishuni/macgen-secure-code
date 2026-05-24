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
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>
#include <string>
#include <fstream>
#include <filesystem>

std::string read_file_from_dir(const std::string &filename, const std::string &dir_path) {
    // Validate and sanitize inputs
    if (filename.find("..") != std::string::npos || dir_path.find("..") != std::string::npos) {
        return "";
    }
    if (filename.empty() || dir_path.empty()) {
        return "";
    }

    try {
        // Construct the full file path securely
        std::filesystem::path full_path = std::filesystem::path(dir_path) / filename;

        // Ensure the resolved path is within the intended directory
        if (!std::filesystem::equivalent(std::filesystem::canonical(dir_path), std::filesystem::canonical(full_path.parent_path()))) {
            return "";
        }

        // Open the file
        std::ifstream file(full_path, std::ios::in | std::ios::binary);
        if (!file.is_open()) {
            return "";
        }

        // Read the file content
        std::string content((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
        return content;
    } catch (...) {
        // Catch any exception and return an empty string
        return "";
    }
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
