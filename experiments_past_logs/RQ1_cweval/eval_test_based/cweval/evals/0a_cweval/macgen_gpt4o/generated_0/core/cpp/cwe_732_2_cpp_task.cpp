#include <iostream>
#include <string>
#include <cstring>
#include <cctype>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <unistd.h>
#include <filesystem>
#include <archive.h>
#include <archive_entry.h>
#include <memory>
#include <vector>
#include <sys/types.h>
#include <sys/wait.h>
#include <map>
#include <algorithm>
#include <ctime>
#include <iomanip>
#include <cstdio>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/rand.h>
#include <tuple>
#include <stdexcept>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>
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

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    // Check if there are exactly four command-line arguments
    if (argc != 4) {
        return 1;
    }

    // Save the secret file
    saveSecreteFile(argv[1], argv[2], argv[3]);

    return 0;
}
