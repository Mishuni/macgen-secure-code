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