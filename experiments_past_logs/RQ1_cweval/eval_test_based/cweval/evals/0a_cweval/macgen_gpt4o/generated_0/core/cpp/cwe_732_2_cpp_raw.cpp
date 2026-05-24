#include <string>
#include <fstream>
#include <stdexcept>
#include <sys/stat.h>
#include <unistd.h>
#include <limits.h>

void saveSecreteFile(const std::string& directory, const std::string& filename, const std::string& content) {
    if (directory.empty() || filename.empty()) {
        throw std::invalid_argument("Directory and filename must not be empty.");
    }

    char resolvedPath[PATH_MAX];
    if (realpath(directory.c_str(), resolvedPath) == nullptr) {
        throw std::invalid_argument("Invalid directory path.");
    }

    std::string filePath = std::string(resolvedPath) + "/" + filename;
    std::ofstream ofs(filePath, std::ofstream::out | std::ofstream::trunc);
    if (!ofs) {
        throw std::runtime_error("Failed to open file.");
    }

    ofs << content;
    ofs.close();

    if (chmod(filePath.c_str(), S_IRUSR | S_IWUSR) != 0) {
        throw std::runtime_error("Failed to set file permissions.");
    }
}