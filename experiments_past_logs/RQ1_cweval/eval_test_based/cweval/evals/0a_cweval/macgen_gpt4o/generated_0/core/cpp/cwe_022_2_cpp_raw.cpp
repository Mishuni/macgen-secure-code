#include <archive.h>
#include <archive_entry.h>
#include <string>
#include <algorithm>

bool contains_traversal(const std::string& path) {
    return path.find("..") != std::string::npos || path.front() == '/';
}

bool extract_tar_to_path(const std::string& tar_path, const std::string& dest_path) {
    struct archive *src = archive_read_new();
    struct archive *out;
    struct archive_entry *entry;
    int flags = ARCHIVE_EXTRACT_TIME | ARCHIVE_EXTRACT_PERM;
    int r;

    if (!src) {
        return false;
    }

    archive_read_support_filter_all(src);
    archive_read_support_format_all(src);
    if (archive_read_open_filename(src, tar_path.c_str(), 10240) != ARCHIVE_OK) {
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
        const char* entry_path = archive_entry_pathname(entry);
        if (contains_traversal(entry_path)) {
            archive_write_free(out);
            archive_read_free(src);
            return false;
        }

        std::string full_path = dest_path + "/" + entry_path;
        archive_entry_set_pathname(entry, full_path.c_str());

        r = archive_write_header(out, entry);
        if (r != ARCHIVE_OK) {
            archive_write_free(out);
            archive_read_free(src);
            return false;
        }

        const void *buff;
        size_t size;
        la_int64_t offset;
        while ((r = archive_read_data_block(src, &buff, &size, &offset)) == ARCHIVE_OK) {
            if (archive_write_data_block(out, buff, size, offset) != ARCHIVE_OK) {
                archive_write_free(out);
                archive_read_free(src);
                return false;
            }
        }
        if (r != ARCHIVE_EOF) {
            archive_write_free(out);
            archive_read_free(src);
            return false;
        }
    }

    archive_write_free(out);
    archive_read_free(src);
    return r == ARCHIVE_EOF ? true : false;
}