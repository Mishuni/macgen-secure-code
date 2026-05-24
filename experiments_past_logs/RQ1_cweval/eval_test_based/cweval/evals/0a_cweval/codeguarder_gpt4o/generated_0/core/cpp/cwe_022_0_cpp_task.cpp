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
#include <stdexcept>

std::string read_file_from_dir(const std::string &filename, const std::string &dir_path) {
    try {
        // Construct the full path using std::filesystem to prevent path traversal
        std::filesystem::path base_path(dir_path);
        std::filesystem::path file_path = base_path / filename;

        // Resolve the absolute path and ensure it is within the specified directory
        std::filesystem::path real_path = std::filesystem::canonical(file_path);
        if (real_path.string().find(base_path.string()) != 0) {
            throw std::runtime_error("Invalid file path: Path is outside the specified directory.");
        }

        // Open the file and read its contents
        std::ifstream file(real_path, std::ios::in);
        if (!file.is_open()) {
            return ""; // Return empty string if file cannot be opened
        }

        std::string content((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
        return content;
    } catch (const std::exception &e) {
        // Handle any exceptions and return an empty string
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
