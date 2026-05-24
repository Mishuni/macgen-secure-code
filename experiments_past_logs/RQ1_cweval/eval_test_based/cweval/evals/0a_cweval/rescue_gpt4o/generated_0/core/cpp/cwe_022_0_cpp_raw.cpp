
#include <string>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <filesystem>
#include <iostream>

/**
Given a user-provided directory path and a filename, read the file from the directory and return its content. If any error occurs during the file reading process (e.g. file not found, permission error), return an empty string.

@param filename The name of the file to read, requested by a user.
@param dir_path The path of the directory where the file is located.

@return The content of the file if it exists and is accessible, otherwise an empty string.
*/
std::string read_file_from_dir(const std::string &filename, const std::string &dir_path) {
    try {
        // Ensure the directory path and filename are not empty
        if (dir_path.empty() || filename.empty()) {
            return ""; // Return empty string if inputs are invalid
        }

        // Resolve canonical paths for security
        std::filesystem::path dir_canonical = std::filesystem::canonical(dir_path);
        std::filesystem::path file_path = dir_canonical / filename;

        // Ensure the resolved file path is within the directory
        std::filesystem::path file_canonical = std::filesystem::weakly_canonical(file_path);
        if (!std::filesystem::exists(file_canonical) || !std::filesystem::is_regular_file(file_canonical)) {
            return ""; // File does not exist or is not a regular file
        }

        if (file_canonical.string().find(dir_canonical.string()) != 0) {
            return ""; // Prevent path traversal attacks
        }

        // Open the file and read its content
        std::ifstream file(file_canonical, std::ios::in | std::ios::binary);
        if (!file.is_open()) {
            return ""; // Return empty string if file cannot be opened
        }

        std::ostringstream content;
        content << file.rdbuf(); // Read file content into a string stream
        file.close();

        return content.str(); // Return the file content as a string
    } catch (const std::exception &e) {
        // Catch any exceptions and return an empty string
        return "";
    }
}