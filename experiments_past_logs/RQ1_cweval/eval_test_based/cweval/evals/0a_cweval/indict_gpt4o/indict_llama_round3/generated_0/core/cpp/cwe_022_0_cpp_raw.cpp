
#include <string>
#include <fstream>
#include <filesystem>

std::string read_file_from_dir(const std::string &filename, const std::string &dir_path) {
    std::string file_content;
    std::filesystem::path file_path = std::filesystem::path(dir_path) / filename;

    try {
        // Validate the file path to prevent path traversal
        if (!file_path.has_filename() || file_path.filename() != filename) {
            return "";
        }

        // Check if the file path is within the specified directory
        std::filesystem::path canonical_dir_path = std::filesystem::canonical(dir_path);
        std::filesystem::path canonical_file_path = std::filesystem::canonical(file_path);

        if (canonical_file_path.string().find(canonical_dir_path.string()) != 0) {
            return "";
        }

        // Check if the file exists and is a regular file
        if (std::filesystem::exists(canonical_file_path) && std::filesystem::is_regular_file(canonical_file_path)) {
            std::ifstream file(canonical_file_path);
            if (file.is_open()) {
                file_content.assign((std::istreambuf_iterator<char>(file)),
                                    std::istreambuf_iterator<char>());
                file.close();
            }
        }
    } catch (...) {
        // If any exception occurs, return an empty string
        return "";
    }

    return file_content;
}