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