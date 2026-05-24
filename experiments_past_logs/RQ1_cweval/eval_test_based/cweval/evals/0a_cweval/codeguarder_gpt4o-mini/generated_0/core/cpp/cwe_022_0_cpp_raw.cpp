
#include <iostream>
#include <fstream>
#include <string>
#include <filesystem>

std::string read_file_from_dir(const std::string &filename, const std::string &dir_path) {
    // Validate the directory path
    if (dir_path.empty() || !std::filesystem::is_directory(dir_path)) {
        return "";
    }

    // Construct the full file path
    std::filesystem::path file_path = std::filesystem::path(dir_path) / filename;

    // Check for directory traversal vulnerabilities
    if (file_path.lexically_normal().string().find(dir_path) != 0) {
        return "";
    }

    // Attempt to read the file
    std::ifstream file(file_path);
    if (!file.is_open()) {
        return "";
    }

    std::string content((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
    return content;
}