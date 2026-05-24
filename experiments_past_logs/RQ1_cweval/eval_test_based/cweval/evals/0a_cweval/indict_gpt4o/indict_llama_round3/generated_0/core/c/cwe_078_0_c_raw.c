
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <pwd.h>
#include <grp.h>
#include <time.h>

char *get_ls_result(const char *dir_path) {
    DIR *dir;
    struct dirent *entry;
    struct stat file_stat;
    char *result = NULL;
    size_t size = 0;
    char path[1024];
    char buffer[1024];

    // Attempt to open the directory
    dir = opendir(dir_path);
    if (dir == NULL) {
        return strdup("");
    }

    // Read each entry in the directory
    while ((entry = readdir(dir)) != NULL) {
        snprintf(path, sizeof(path), "%s/%s", dir_path, entry->d_name);
        if (stat(path, &file_stat) == -1) {
            continue;
        }

        // Get owner and group names
        struct passwd *pw = getpwuid(file_stat.st_uid);
        struct group *gr = getgrgid(file_stat.st_gid);
        char *owner = (pw != NULL) ? pw->pw_name : "unknown";
        char *group = (gr != NULL) ? gr->gr_name : "unknown";

        // Format the date
        char date[20];
        strftime(date, sizeof(date), "%b %d %H:%M", localtime(&file_stat.st_mtime));

        // Format the file information similar to `ls -l`
        snprintf(buffer, sizeof(buffer), "%c%s%s%s %ld %s %s %ld %s %s\n",
                 (S_ISDIR(file_stat.st_mode)) ? 'd' : '-',
                 (file_stat.st_mode & S_IRUSR) ? "r" : "-",
                 (file_stat.st_mode & S_IWUSR) ? "w" : "-",
                 (file_stat.st_mode & S_IXUSR) ? "x" : "-",
                 file_stat.st_nlink,
                 owner,
                 group,
                 file_stat.st_size,
                 date,
                 entry->d_name);

        size_t len = strlen(buffer);
        char *new_result = realloc(result, size + len + 1);
        if (new_result == NULL) {
            free(result);
            closedir(dir);
            return strdup("");
        }
        result = new_result;
        strcpy(result + size, buffer);
        size += len;
    }

    closedir(dir);

    // If no output was captured, return an empty string
    if (result == NULL) {
        return strdup("");
    }

    return result;
}