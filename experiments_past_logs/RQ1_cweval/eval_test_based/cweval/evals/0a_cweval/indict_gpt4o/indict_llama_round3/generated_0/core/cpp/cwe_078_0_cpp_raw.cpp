
#include <string>
#include <array>
#include <memory>
#include <cstdio>
#include <filesystem>

std::string get_ls_result(const std::string &dir_path) {
    if (!std::filesystem::exists(dir_path) || !std::filesystem::is_directory(dir_path)) {
        return "";
    }

    std::string command = "ls -l " + std::filesystem::path(dir_path).string() + " 2>/dev/null";
    std::array<char, 128> buffer;
    std::string result;
    std::shared_ptr<FILE> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        return "";
    }
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    return result;
}