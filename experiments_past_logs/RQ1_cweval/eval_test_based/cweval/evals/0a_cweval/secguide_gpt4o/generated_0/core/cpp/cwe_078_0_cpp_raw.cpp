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