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
#include <sstream>
#include <filesystem>
#include <cctype>
#include <algorithm>

std::string read_file_from_dir(const std::string &filename, const std::string &dir_path) {
    // Validate input for safe characters
    if (!std::all_of(filename.begin(), filename.end(), [](char c) { return std::isalnum(c) || c == '_' || c == '.'; }) ||
        !std::all_of(dir_path.begin(), dir_path.end(), [](char c) { return std::isalnum(c) || c == '_' || c == '/' || c == '.'; })) {
        return "";
    }

    // Check for path traversal
    if (filename.find("..") != std::string::npos || dir_path.find("..") != std::string::npos) {
        return "";
    }

    std::filesystem::path full_path = std::filesystem::path(dir_path) / filename;
    std::ifstream file(full_path);

    if (!file.is_open()) {
        return "";
    }

    std::stringstream buffer;
    buffer << file.rdbuf();
    return buffer.str();
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
