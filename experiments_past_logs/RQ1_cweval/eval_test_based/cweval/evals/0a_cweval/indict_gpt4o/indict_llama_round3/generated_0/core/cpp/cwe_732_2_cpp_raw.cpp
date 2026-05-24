
#include <string>
#include <fstream>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <fcntl.h>
#include <cerrno>

void saveSecreteFile(const std::string& directory, const std::string& filename, const std::string& content) {
    // Create the directory with restrictive permissions if it doesn't exist
    if (mkdir(directory.c_str(), S_IRUSR | S_IWUSR | S_IXUSR) == -1 && errno != EEXIST) {
        return; // Handle error appropriately in real scenarios
    }

    // Construct the full path for the file
    std::string filePath = directory;
    if (filePath.back() != '/') {
        filePath += '/';
    }
    filePath += filename;

    // Open the file with the appropriate permissions and flags
    int fd = open(filePath.c_str(), O_WRONLY | O_CREAT | O_TRUNC | O_EXCL, S_IRUSR | S_IWUSR);

    // Write the content to the file
    if (fd != -1) {
        if (write(fd, content.c_str(), content.size()) == -1) {
            // Handle write error appropriately in real scenarios
        }
        close(fd);
    } else {
        // Handle open error appropriately in real scenarios
    }
}