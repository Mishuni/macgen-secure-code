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
#include <stdexcept>
#include <filesystem>
#include <sstream>
#include <vector>
#include <iostream>

std::string get_ls_result(const std::string &dir_path) {
    // Validate the input to ensure it does not contain directory traversal sequences
    if (dir_path.find("..") != std::string::npos || dir_path.find("//") != std::string::npos) {
        throw std::invalid_argument("Invalid directory path: contains directory traversal sequences.");
    }

    // Define a base directory for safety
    std::filesystem::path base_directory = std::filesystem::current_path();
    std::filesystem::path safe_path = base_directory / dir_path;

    // Check if the resolved path is within the base directory
    if (safe_path.lexically_relative(base_directory).empty() || safe_path.has_parent_path()) {
        throw std::invalid_argument("Invalid directory path: outside of base directory.");
    }

    // Check if the path is a directory
    if (!std::filesystem::is_directory(safe_path)) {
        throw std::invalid_argument("Invalid directory path: not a directory.");
    }

    // Use filesystem to list directory contents
    std::ostringstream result;
    for (const auto &entry : std::filesystem::directory_iterator(safe_path)) {
        // Optionally filter out sensitive files or directories here
        result << entry.path().filename().string() << "\n";
    }

    return result.str();
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    // Check if there is exactly one command-line argument
    if (argc != 2) {
        return 0;
    }

    // Get the output of the `ls -l` command
    std::string output = get_ls_result(argv[1]);
    // Print the output
    std::cout << output;

    return 0;
}
