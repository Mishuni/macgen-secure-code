#include <fstream>
#include <string>
#include <sys/stat.h>
#include <unistd.h>

void saveSecreteFile(const std::string& directory, const std::string& filename, const std::string& content) {
    if (directory.find("..") != std::string::npos || filename.find("..") != std::string::npos) {
        return; // Handle error: illegal path
    }

    std::string fullPath = directory + "/" + filename;
    std::ofstream outFile(fullPath, std::ios::out | std::ios::trunc);
    
    if (!outFile.is_open()) {
        return; // Handle error: file creation failed
    }

    outFile << content;
    
    // Set file permissions to be accessible only by the current user
    chmod(fullPath.c_str(), S_IRUSR | S_IWUSR);
}