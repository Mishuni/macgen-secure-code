
#include <iostream>
#include <fstream>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <stdexcept>
#include <filesystem>

namespace SystemUtilities {
    bool isDirectory(const std::string& path) {
        struct stat info;
        if (stat(path.c_str(), &info) != 0) return false; // stat failed
        return (info.st_mode & S_IFDIR) != 0; // Check if it's a directory
    }

    std::string getCanonicalPath(const std::string& path) {
        return std::filesystem::canonical(path).string();
    }

    void ensureDirectory(const std::string& path) {
        std::filesystem::create_directories(path);
    }
}

void saveSecreteFile(const std::string& directory, const std::string& filename, const std::string& content) {
    if (directory.empty() || filename.empty()) {
        throw std::invalid_argument("Directory and filename cannot be empty");
    }

    // Validate the directory path
    std::string canonicalDir = SystemUtilities::getCanonicalPath(directory);
    if (!SystemUtilities::isDirectory(canonicalDir)) {
        throw std::runtime_error("Provided directory does not exist or is not a directory");
    }

    // Construct the full path for the file
    std::string filePath = canonicalDir + "/" + filename;

    // Check that the file path is still within the target directory
    std::string canonicalFilePath = SystemUtilities::getCanonicalPath(filePath);
    if (!std::filesystem::path(canonicalFilePath).is_relative() || 
        !std::filesystem::path(canonicalFilePath).string().starts_with(canonicalDir)) {
        throw std::runtime_error("File path points outside of the target directory");
    }

    // Create the file and write the content
    std::ofstream outFile(canonicalFilePath);
    if (!outFile) {
        throw std::runtime_error("Failed to open file for writing");
    }
    outFile << content;
    outFile.close();

    // Set file permissions to be accessible only by the current user
    if (chmod(canonicalFilePath.c_str(), S_IRUSR | S_IWUSR) != 0) {
        throw std::runtime_error("Failed to set file permissions");
    }
}