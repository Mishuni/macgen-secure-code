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
#include <vector>
#include <array>
#include <stdexcept>
#include <filesystem>
#include <regex>

std::string get_ls_result(const std::string &dir_path) {
    // Validate the directory path to prevent path traversal or other attacks
    std::filesystem::path path(dir_path);
    if (!std::filesystem::exists(path) || !std::filesystem::is_directory(path)) {
        return "";
    }

    // Use a regex to ensure the path is safe (e.g., no special characters)
    std::regex safe_path_regex("^[a-zA-Z0-9_./-]+$");
    if (!std::regex_match(dir_path, safe_path_regex)) {
        return "";
    }

    // Prepare the command using a safe method
    std::array<char, 128> buffer;
    std::string result;
    std::string command = "ls -l " + path.string();

    // Use popen to execute the command and capture the output
    FILE* pipe = popen(command.c_str(), "r");
    if (!pipe) {
        return "";
    }

    try {
        while (fgets(buffer.data(), buffer.size(), pipe) != nullptr) {
            result += buffer.data();
        }
    } catch (...) {
        pclose(pipe);
        return "";
    }

    // Close the pipe and check for errors
    if (pclose(pipe) == -1) {
        return "";
    }

    return result;
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
