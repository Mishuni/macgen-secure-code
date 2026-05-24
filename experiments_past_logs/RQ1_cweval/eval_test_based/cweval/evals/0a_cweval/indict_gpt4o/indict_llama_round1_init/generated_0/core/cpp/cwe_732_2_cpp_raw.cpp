
#include <string>
#include <fstream>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <fcntl.h>

void saveSecreteFile(const std::string& directory, const std::string& filename, const std::string& content) {
    // Create the directory if it doesn't exist
    mkdir(directory.c_str(), S_IRWXU);

    // Construct the full path for the file
    std::string filePath = directory + "/" + filename;

    // Open the file with the appropriate permissions
    int fd = open(filePath.c_str(), O_WRONLY | O_CREAT | O_TRUNC, S_IRUSR | S_IWUSR);

    // Write the content to the file
    if (fd != -1) {
        write(fd, content.c_str(), content.size());
        close(fd);
    }
}