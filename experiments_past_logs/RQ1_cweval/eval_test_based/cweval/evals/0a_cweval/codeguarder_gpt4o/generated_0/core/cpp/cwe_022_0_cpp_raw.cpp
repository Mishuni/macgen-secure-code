
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