#include <iostream>
#include <string>
#include <filesystem>
#include <sstream>
#include <array>
#include <cstdio>

std::string get_ls_result(const std::string &dir_path) {
    // Prevent path traversal and command injection
    if (dir_path.find("..") != std::string::npos || dir_path.find_first_of("&;|") != std::string::npos) {
        return "";
    }

    std::filesystem::path path(dir_path);
    if (!std::filesystem::exists(path) || !std::filesystem::is_directory(path)) {
        return "";
    }

    // Escape the directory path to prevent command injection
    std::string safe_dir_path;
    for (char c : dir_path) {
        if (c == ' ' || c == '\\' || c == '\'' || c == '\"') {
            safe_dir_path += '\\';
        }
        safe_dir_path += c;
    }

    std::string command = "ls -l " + safe_dir_path + " 2>/dev/null";
    std::array<char, 128> buffer;
    std::string result;
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
    pclose(pipe);
    return result;
}