#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <archive.h>
#include <archive_entry.h>
#include <sys/stat.h>
#include <unistd.h>
#include <libgen.h>

bool is_valid_path(const char *path) {
    if (strstr(path, "..") != NULL) {
        return false;
    }
    return true;
}

bool is_reserved_device_name(const char *path) {
    // Implement checks for reserved device names if necessary
    return false;
}

bool extract_tar_to_path(const char *tar_path, const char *dest_path) {
    struct archive *src;
    struct archive *out;
    struct archive_entry *entry;
    int flags = ARCHIVE_EXTRACT_TIME | ARCHIVE_EXTRACT_PERM | ARCHIVE_EXTRACT_SECURE_NODOTDOT;
    int r;

    src = archive_read_new();
    if (!src) {
        return false;
    }
    archive_read_support_format_tar(src);

    if (archive_read_open_filename(src, tar_path, 10240) != ARCHIVE_OK) {
        archive_read_free(src);
        return false;
    }

    out = archive_write_disk_new();
    if (!out) {
        archive_read_free(src);
        return false;
    }
    archive_write_disk_set_options(out, flags);

    while ((r = archive_read_next_header(src, &entry)) == ARCHIVE_OK) {
        const char *entry_path = archive_entry_pathname(entry);
        if (!is_valid_path(entry_path)) {
            archive_write_free(out);
            archive_read_free(src);
            return false;
        }

        size_t required_size = snprintf(NULL, 0, "%s/%s", dest_path, entry_path) + 1;
        char *full_path = malloc(required_size);
        if (!full_path) {
            archive_write_free(out);
            archive_read_free(src);
            return false;
        }
        snprintf(full_path, required_size, "%s/%s", dest_path, entry_path);

        if (is_reserved_device_name(full_path)) {
            free(full_path);
            archive_write_free(out);
            archive_read_free(src);
            return false;
        }

        archive_entry_set_pathname(entry, full_path);

        r = archive_write_header(out, entry);
        if (r != ARCHIVE_OK) {
            free(full_path);
            archive_write_free(out);
            archive_read_free(src);
            return false;
        }

        const void *buff;
        size_t size;
        la_int64_t offset;
        while ((r = archive_read_data_block(src, &buff, &size, &offset)) == ARCHIVE_OK) {
            if (archive_write_data_block(out, buff, size, offset) != ARCHIVE_OK) {
                free(full_path);
                archive_write_free(out);
                archive_read_free(src);
                return false;
            }
        }
        if (r != ARCHIVE_EOF) {
            free(full_path);
            archive_write_free(out);
            archive_read_free(src);
            return false;
        }

        free(full_path);
    }

    archive_write_free(out);
    archive_read_free(src);
    return r == ARCHIVE_EOF ? true : false;
}