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
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <limits.h>
#include <cerrno>
#include <cstring>

std::string get_ls_result(const std::string &dir_path) {
    // Check if the path is too long or empty
    if (dir_path.empty() || dir_path.length() > PATH_MAX) {
        throw std::invalid_argument("Path is empty or exceeds maximum length");
    }

    // Open the directory
    DIR *dir = opendir(dir_path.c_str());
    if (!dir) {
        throw std::runtime_error("Failed to open directory: " + std::string(std::strerror(errno)));
    }

    std::string result;
    struct dirent *entry;
    while ((entry = readdir(dir)) != nullptr) {
        // Skip the current and parent directory entries
        if (std::string(entry->d_name) == "." || std::string(entry->d_name) == "..") {
            continue;
        }
        result += entry->d_name;
        result += "\n";
    }

    // Close the directory
    if (closedir(dir) != 0) {
        throw std::runtime_error("Failed to close directory: " + std::string(std::strerror(errno)));
    }

    return result;
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
