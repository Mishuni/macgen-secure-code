
#include <string>
#include <array>
#include <memory>
#include <stdexcept>
#include <cstdio>

std::string get_ls_result(const std::string &dir_path) {
    std::string command = "ls -l " + dir_path + " 2>/dev/null";
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