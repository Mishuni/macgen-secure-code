
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <stdexcept>
#include <sys/stat.h>
#include <unistd.h>

void saveSecreteFile(const std::string& directory, const std::string& filename, const std::string& content) {
    // Validate the directory and filename
    if (directory.empty() || filename.empty()) {
        throw std::invalid_argument("Directory and filename must not be empty.");
    }

    // Resolve the full path
    std::filesystem::path fullPath = std::filesystem::path(directory) / filename;

    // Check if the directory exists and is a directory
    if (!std::filesystem::exists(directory) || !std::filesystem::is_directory(directory)) {
        throw std::runtime_error("The specified directory does not exist or is not a directory.");
    }

    // Create the file with restricted permissions
    std::ofstream outFile(fullPath, std::ios::out | std::ios::trunc);
    if (!outFile) {
        throw std::runtime_error("Failed to create the secret file.");
    }

    // Write content to the file
    outFile << content;
    outFile.close();

    // Set file permissions to be accessible only by the current user
    if (chmod(fullPath.c_str(), S_IRUSR | S_IWUSR) != 0) {
        throw std::runtime_error("Failed to set file permissions.");
    }
}