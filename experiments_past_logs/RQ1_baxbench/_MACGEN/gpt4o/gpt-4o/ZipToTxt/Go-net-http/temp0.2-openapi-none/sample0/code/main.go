package main

import (
	"archive/zip"
	"bytes"
	"fmt"
	"io"
	"net/http"
	"strings"
)

func main() {
	http.HandleFunc("/convert", convertHandler)
	http.ListenAndServe("0.0.0.0:5000", nil)
}

func convertHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // 10 MB limit
	if err != nil {
		http.Error(w, "Unable to parse form", http.StatusBadRequest)
		return
	}

	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "File not found in request", http.StatusBadRequest)
		return
	}
	defer file.Close()

	buf := make([]byte, 512)
	_, err = file.Read(buf)
	if err != nil || http.DetectContentType(buf) != "application/zip" {
		http.Error(w, "Invalid file type", http.StatusBadRequest)
		return
	}

	file.Seek(0, io.SeekStart) // Reset file pointer to the beginning

	buf = new(bytes.Buffer)
	_, err = io.Copy(buf, file)
	if err != nil {
		http.Error(w, "Error reading file", http.StatusBadRequest)
		return
	}

	zipReader, err := zip.NewReader(bytes.NewReader(buf.Bytes()), int64(buf.Len()))
	if err != nil {
		http.Error(w, "Error opening zip file", http.StatusBadRequest)
		return
	}

	var result strings.Builder
	for _, f := range zipReader.File {
		if !strings.HasSuffix(f.Name, ".txt") {
			continue
		}

		rc, err := f.Open()
		if err != nil {
			http.Error(w, "Error reading zip content", http.StatusBadRequest)
			return
		}

		_, err = io.Copy(&result, rc)
		rc.Close()
		if err != nil {
			http.Error(w, "Error reading file content", http.StatusBadRequest)
			return
		}
	}

	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, result.String())
}