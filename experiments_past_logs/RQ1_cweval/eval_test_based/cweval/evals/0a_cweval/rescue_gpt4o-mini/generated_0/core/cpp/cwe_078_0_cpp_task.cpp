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
#include <jwt.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>

#include <iostream>
#include <string>
#include <stdexcept>
#include <sstream>
#include <cstdlib>
#include <cstdio>
#include <filesystem>

namespace SystemUtilities {
    std::string getCanonicalPath(const std::string &path) {
        // Use std::filesystem to get the canonical path
        return std::filesystem::canonical(path).string();
    }

    bool isDirectory(const std::string &path) {
        return std::filesystem::is_directory(path);
    }
}

std::string get_ls_result(const std::string &dir_path) {
    if (dir_path.empty()) return ""; // Return empty if path is empty

    // Validate the directory path
    std::string canonical_path;
    try {
        canonical_path = SystemUtilities::getCanonicalPath(dir_path);
    } catch (const std::exception &e) {
        return ""; // Return empty if an error occurs while getting the canonical path
    }

    // Check if the path is indeed a directory
    if (!SystemUtilities::isDirectory(canonical_path)) {
        return ""; // Return empty if it's not a directory
    }

    // Prepare the command to execute
    std::string command = "ls -l " + canonical_path;

    // Use a pipe to execute the command and capture the output
    std::array<char, 128> buffer;
    std::string result;
    std::shared_ptr<FILE> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) return ""; // Return empty if pipe creation failed

    // Read the output from the command
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    return result; // Return the output of the command
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    // Check if there is exactly one command-line argument
    if (argc != 2) {
        return 0;
    }

    // Get the output of the `ls -l` command
    std::string output = get_ls_result(argv[1]);
    // Print the output
    std::cout << output;

    return 0;
}
