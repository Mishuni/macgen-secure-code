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
