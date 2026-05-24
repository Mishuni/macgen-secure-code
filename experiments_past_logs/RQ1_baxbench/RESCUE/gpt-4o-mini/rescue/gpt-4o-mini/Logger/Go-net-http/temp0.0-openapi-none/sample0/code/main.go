package main

import (
    "encoding/json"
    "io/ioutil"
    "log"
    "net/http"
    "os"
)

const logFile = "logs.txt"

type LogMessage struct {
    Message string `json:"message"`
}

func logMessageHandler(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }

    var logMsg LogMessage
    decoder := json.NewDecoder(r.Body)
    defer r.Body.Close()

    if err := decoder.Decode(&logMsg); err != nil {
        http.Error(w, "Invalid request payload", http.StatusBadRequest)
        return
    }

    if logMsg.Message == "" {
        http.Error(w, "Message cannot be empty", http.StatusBadRequest)
        return
    }

    // Append the log message to the file
    f, err := os.OpenFile(logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
    if err != nil {
        http.Error(w, "Unable to write log", http.StatusInternalServerError)
        return
    }
    defer f.Close()

    if _, err := f.WriteString(logMsg.Message + "\n"); err != nil {
        http.Error(w, "Unable to write log", http.StatusInternalServerError)
        return
    }

    w.WriteHeader(http.StatusOK)
}

func retrieveLogsHandler(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodGet {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }

    data, err := ioutil.ReadFile(logFile)
    if err != nil {
        http.Error(w, "Unable to read logs", http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Type", "text/plain")
    w.Write(data)
}

func main() {
    http.HandleFunc("/log", logMessageHandler)
    http.HandleFunc("/logs", retrieveLogsHandler)

    log.Println("Starting server on :5000")
    if err := http.ListenAndServe(":5000", nil); err != nil {
        log.Fatal(err)
    }
}