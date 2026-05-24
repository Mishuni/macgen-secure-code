#include <string>
#include <fstream>
#include <filesystem>
#include <regex>
#include <algorithm>
#include <cctype>
#include <vector>

std::string read_file_from_dir(const std::string &filename, const std::string &dir_path) {
    // Allowlist of acceptable file extensions
    const std::vector<std::string> allowed_extensions = {".txt", ".md", ".csv"};

    // Validate filename using a stricter regex pattern
    std::regex valid_filename_regex("^[a-zA-Z0-9_-]+\\.[a-zA-Z0-9]+$");
    if (!std::regex_match(filename, valid_filename_regex)) {
        return "";
    }

    // Check if the file extension is allowed (case-insensitive)
    std::string extension = std::filesystem::path(filename).extension().string();
    std::transform(extension.begin(), extension.end(), extension.begin(), ::tolower);
    std::vector<std::string> lower_allowed_extensions = allowed_extensions;
    for (auto &ext : lower_allowed_extensions) {
        std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);
    }
    if (std::find(lower_allowed_extensions.begin(), lower_allowed_extensions.end(), extension) == lower_allowed_extensions.end()) {
        return "";
    }

    // Canonicalize the directory path to prevent directory traversal
    std::filesystem::path canonical_dir;
    try {
        canonical_dir = std::filesystem::canonical(dir_path);
    } catch (const std::filesystem::filesystem_error&) {
        return "";
    }

    // Construct the full file path
    std::filesystem::path file_path = canonical_dir / filename;

    // Ensure the file path is within the canonical directory
    std::filesystem::path canonical_file_path;
    try {
        canonical_file_path = std::filesystem::canonical(file_path);
        if (canonical_file_path.string().find(canonical_dir.string()) != 0) {
            return "";
        }
    } catch (const std::filesystem::filesystem_error&) {
        return "";
    }

    // Check file size before opening
    std::uintmax_t file_size;
    try {
        file_size = std::filesystem::file_size(canonical_file_path);
        if (file_size > 10 * 1024 * 1024) { // Example size limit: 10 MB
            return "";
        }
    } catch (const std::filesystem::filesystem_error&) {
        return "";
    }

    // Read the file content
    std::ifstream file(canonical_file_path, std::ios::binary);
    if (!file.is_open()) {
        return "";
    }

    std::string content;
    content.reserve(file_size);
    char buffer[4096];
    while (file.read(buffer, sizeof(buffer))) {
        content.append(buffer, file.gcount());
    }
    content.append(buffer, file.gcount()); // Append any remaining characters

    return content;
}