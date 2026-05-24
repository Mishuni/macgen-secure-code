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