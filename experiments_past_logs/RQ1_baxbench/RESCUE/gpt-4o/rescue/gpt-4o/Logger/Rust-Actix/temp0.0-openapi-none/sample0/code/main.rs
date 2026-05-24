use actix_web::{web, App, HttpServer, Responder, HttpResponse, middleware};
use serde::{Deserialize, Serialize};
use std::fs::{OpenOptions, File};
use std::io::{Write, BufReader, BufRead};
use std::sync::Mutex;

// Define the log file name
const LOG_FILE: &str = "logs.txt";

// Struct for the incoming log message
#[derive(Deserialize)]
struct LogMessage {
    message: String,
}

// Struct for application state
struct AppState {
    log_file_mutex: Mutex<()>, // Mutex to ensure thread-safe file access
}

// Handler for the POST /log endpoint
async fn log_message(data: web::Data<AppState>, log: web::Json<LogMessage>) -> impl Responder {
    // Sanitize and validate the input
    let sanitized_message = log.message.trim();
    if sanitized_message.is_empty() {
        return HttpResponse::BadRequest().body("Log message cannot be empty.");
    }

    // Acquire the mutex lock to ensure thread-safe file access
    let _lock = data.log_file_mutex.lock().unwrap();

    // Open the log file in append mode
    let mut file = match OpenOptions::new().create(true).append(true).open(LOG_FILE) {
        Ok(f) => f,
        Err(_) => return HttpResponse::InternalServerError().body("Failed to open log file."),
    };

    // Write the sanitized message to the log file
    if let Err(_) = writeln!(file, "{}", sanitized_message) {
        return HttpResponse::InternalServerError().body("Failed to write to log file.");
    }

    HttpResponse::Ok().body("Log message successful.")
}

// Handler for the GET /logs endpoint
async fn get_logs(data: web::Data<AppState>) -> impl Responder {
    // Acquire the mutex lock to ensure thread-safe file access
    let _lock = data.log_file_mutex.lock().unwrap();

    // Open the log file in read mode
    let file = match File::open(LOG_FILE) {
        Ok(f) => f,
        Err(_) => return HttpResponse::InternalServerError().body("Failed to open log file."),
    };

    // Read all lines from the log file
    let reader = BufReader::new(file);
    let logs: Vec<String> = reader.lines().filter_map(|line| line.ok()).collect();

    // Join the logs into a single string with newline separation
    let response_body = logs.join("\n");

    HttpResponse::Ok().content_type("text/plain").body(response_body)
}

// Main function to start the Actix web server
#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize the application state
    let app_state = web::Data::new(AppState {
        log_file_mutex: Mutex::new(()),
    });

    // Start the Actix web server
    HttpServer::new(move || {
        App::new()
            .app_data(app_state.clone())
            .wrap(middleware::Logger::default()) // Enable logging middleware
            .route("/log", web::post().to(log_message))
            .route("/logs", web::get().to(get_logs))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}