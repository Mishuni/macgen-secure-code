
#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <stdexcept>
#include <filesystem>
#include <cstdio>
#include <memory>

std::string get_ls_result(const std::string &dir_path) {
    // Validate the directory path
    if (dir_path.empty() || !std::filesystem::exists(dir_path) || !std::filesystem::is_directory(dir_path)) {
        return "";
    }

    // Prepare the command
    std::string command = "ls -l " + dir_path;

    // Use a pipe to read the output of the command
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        return "";
    }

    // Read the output from the command
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    // Return the result or an empty string if an error occurred
    return result.empty() ? "" : result;
}