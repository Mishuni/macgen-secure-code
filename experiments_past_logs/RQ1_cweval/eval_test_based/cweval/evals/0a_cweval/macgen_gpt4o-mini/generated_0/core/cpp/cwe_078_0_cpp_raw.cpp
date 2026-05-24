#include <string>
#include <cstdio>
#include <memory>
#include <array>
#include <regex>

std::string get_ls_result(const std::string &dir_path) {
    // Updated regex to allow only safe characters in the path
    if (!std::regex_match(dir_path, std::regex("^[a-zA-Z0-9_.-/]+$"))) {
        return "";
    }

    std::string command = "ls -l \"" + dir_path + "\"";
    std::array<char, 128> buffer;
    std::string result;

    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        return "";
    }

    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    return result;
}