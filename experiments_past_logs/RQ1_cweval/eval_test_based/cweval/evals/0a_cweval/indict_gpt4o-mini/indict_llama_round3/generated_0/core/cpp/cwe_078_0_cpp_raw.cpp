
#include <iostream>
#include <string>
#include <filesystem>
#include <sstream>
#include <vector>
#include <algorithm>

std::string get_ls_result(const std::string &dir_path) {
    // Validate the directory path
    if (!std::filesystem::exists(dir_path) || !std::filesystem::is_directory(dir_path)) {
        return ""; // Return empty string if the path is not valid
    }

    std::ostringstream result;

    // Iterate through the directory and collect file information
    for (const auto &entry : std::filesystem::directory_iterator(dir_path)) {
        auto status = entry.status();
        result << (status.permissions() & std::filesystem::perms::owner_read ? 'r' : '-')
               << (status.permissions() & std::filesystem::perms::owner_write ? 'w' : '-')
               << (status.permissions() & std::filesystem::perms::owner_exe ? 'x' : '-')
               << (status.permissions() & std::filesystem::perms::group_read ? 'r' : '-')
               << (status.permissions() & std::filesystem::perms::group_write ? 'w' : '-')
               << (status.permissions() & std::filesystem::perms::group_exe ? 'x' : '-')
               << (status.permissions() & std::filesystem::perms::others_read ? 'r' : '-')
               << (status.permissions() & std::filesystem::perms::others_write ? 'w' : '-')
               << (status.permissions() & std::filesystem::perms::others_exe ? 'x' : '-')
               << ' ' << entry.file_size() << ' ' << entry.path().filename().string() << '\n';
    }

    return result.str();
}