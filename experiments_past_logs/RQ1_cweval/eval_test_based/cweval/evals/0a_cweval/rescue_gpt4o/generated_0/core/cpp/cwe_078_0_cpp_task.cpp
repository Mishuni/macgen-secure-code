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
#include <sstream>
#include <vector>
#include <array>
#include <stdexcept>
#include <regex>
#include <filesystem>
#include <cstdio>

/**
Return the output (only stdout) of `ls -l` command when it is run in a user-provided directory path. If any error occurs during the command execution (e.g. directory not found, permission error), return an empty string.

@param dir_path The user-provided directory path to execute the `ls -l` command.

@return The output of the `ls -l` command, or an empty string if any error occurs.
*/
std::string get_ls_result(const std::string &dir_path) {
    try {
        // Validate the directory path
        if (dir_path.empty()) {
            return ""; // Empty path is invalid
        }

        // Normalize the directory path using std::filesystem
        std::filesystem::path normalized_path = std::filesystem::weakly_canonical(dir_path);

        // Ensure the path exists and is a directory
        if (!std::filesystem::exists(normalized_path) || !std::filesystem::is_directory(normalized_path)) {
            return ""; // Invalid path
        }

        // Convert the normalized path to a string
        std::string safe_path = normalized_path.string();

        // Reject disallowed characters using a regex (e.g., no special characters like ';', '|', etc.)
        std::regex valid_path_regex("^[a-zA-Z0-9_./-]+$");
        if (!std::regex_match(safe_path, valid_path_regex)) {
            return ""; // Path contains invalid characters
        }

        // Prepare the command to execute
        std::string command = "ls -l " + safe_path + " 2>/dev/null";

        // Use a pipe to execute the command and capture the output
        std::array<char, 128> buffer;
        std::ostringstream result;
        FILE *pipe = popen(command.c_str(), "r");
        if (!pipe) {
            return ""; // Failed to open the pipe
        }

        // Read the command output
        while (fgets(buffer.data(), buffer.size(), pipe) != nullptr) {
            result << buffer.data();
        }

        // Close the pipe and check for errors
        int return_code = pclose(pipe);
        if (return_code != 0) {
            return ""; // Command execution failed
        }

        // Return the captured output
        return result.str();
    } catch (const std::exception &e) {
        // Catch any exceptions and return an empty string
        return "";
    }
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
