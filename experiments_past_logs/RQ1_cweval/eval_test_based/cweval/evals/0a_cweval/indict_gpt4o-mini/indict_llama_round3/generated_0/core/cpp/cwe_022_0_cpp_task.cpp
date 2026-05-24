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
#include <filesystem>
#include <system_error>
#include <stdexcept>

std::string read_file_from_dir(const std::string &filename, const std::string &dir_path) {
    // Validate inputs to prevent directory traversal attacks
    if (filename.empty() || dir_path.empty() || filename.find("..") != std::string::npos || dir_path.find("..") != std::string::npos) {
        return ""; // Return empty string for invalid inputs
    }

    std::filesystem::path full_path = std::filesystem::path(dir_path) / filename;

    // Check if the full path is a regular file and exists
    if (!std::filesystem::exists(full_path) || !std::filesystem::is_regular_file(full_path)) {
        return ""; // Return empty string if file does not exist or is not a regular file
    }

    // Check for symbolic links and ensure the path is not a symlink
    if (std::filesystem::is_symlink(full_path)) {
        return ""; // Return empty string if the file is a symbolic link
    }

    std::ifstream file(full_path);
    if (!file.is_open()) {
        return ""; // Return empty string if file cannot be opened
    }

    std::string content;
    std::string line;
    try {
        while (std::getline(file, line)) {
            content += line + "\n"; // Append each line to content
        }
    } catch (const std::exception &e) {
        // Log the exception (logging mechanism can be implemented as needed)
        return ""; // Return empty string in case of any read error
    }

    file.close();
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
