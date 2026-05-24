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

#include <string>
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <cctype>

std::string escape_html(const std::string &input) {
    std::ostringstream escaped;
    for (char c : input) {
        switch (c) {
            case '&':  escaped << "&amp;"; break;
            case '\"': escaped << "&quot;"; break;
            case '\'': escaped << "&#39;"; break;
            case '<':  escaped << "&lt;"; break;
            case '>':  escaped << "&gt;"; break;
            default:   escaped << c; break;
        }
    }
    return escaped.str();
}

std::string get_welcome_message(const std::string &username) {
    std::string safe_username = escape_html(username);
    return "Welcome, " + safe_username + "!";
}

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cout << "Usage: " << argv[0] << " <username>\n";
        return 1;
    }

    std::string message = get_welcome_message(argv[1]);
    std::cout << message;

    return 0;
}
