package main

import (
    "encoding/json"
    "net/http"
    "os"
    "path/filepath"
)

const songsDir = "/var/songs"

// Predefined list of allowed filenames
var allowedFilenames = map[string]struct{}{
    "peters_mixtape.mp3": {},
}

type RequestBody struct {
    Filename string `json:"filename"`
}

func isValidFilename(filename string) bool {
    _, exists := allowedFilenames[filename]
    return exists
}

func downloadSong(w http.ResponseWriter, r *http.Request) {
    var reqBody RequestBody
    if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil || reqBody.Filename == "" {
        http.Error(w, "Invalid input", http.StatusBadRequest)
        return
    }

    if !isValidFilename(reqBody.Filename) {
        http.Error(w, "Invalid input", http.StatusBadRequest)
        return
    }

    filePath := filepath.Clean(filepath.Join(songsDir, reqBody.Filename))
    if _, err := os.Stat(filePath); os.IsNotExist(err) {
        http.Error(w, "File does not exist", http.StatusNotFound)
        return
    }

    w.Header().Set("X-Content-Type-Options", "nosniff")
    w.Header().Set("Content-Type", "audio/mpeg")
    http.ServeFile(w, r, filePath)
}

func main() {
    http.HandleFunc("/download", downloadSong)
    http.ListenAndServe("0.0.0.0:5000", nil)
}