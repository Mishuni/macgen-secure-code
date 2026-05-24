use actix_web::{post, get, web, App, HttpServer, HttpResponse, Responder};
use serde::Deserialize;
use std::fs::{OpenOptions, File};
use std::io::{Write, Read};
use std::sync::Mutex;
use regex::Regex;

#[derive(Deserialize)]
struct LogMessage {
    message: String,
}

struct AppState {
    log_file: Mutex<File>,
}

fn sanitize_log_message(message: &str) -> String {
    // More robust sanitization: escape newlines and other potentially harmful characters
    let re = Regex::new(r"[^\x20-\x7E]").unwrap(); // Allow only printable ASCII characters
    re.replace_all(message, "").to_string()
}

#[post("/log")]
async fn log_message(data: web::Json<LogMessage>, state: web::Data<AppState>) -> impl Responder {
    let sanitized_message = sanitize_log_message(&data.message);
    let log_entry = format!("{}\n", sanitized_message);
    let mut file = state.log_file.lock().unwrap();
    if let Err(e) = file.write_all(log_entry.as_bytes()) {
        eprintln!("Failed to write to log file: {}", e);
        return HttpResponse::InternalServerError().finish();
    }
    HttpResponse::Ok().finish()
}

#[get("/logs")]
async fn get_logs(state: web::Data<AppState>) -> impl Responder {
    let mut file = match File::open("logs.txt") {
        Ok(file) => file,
        Err(_) => {
            eprintln!("Failed to open log file. Creating a new one.");
            File::create("logs.txt").expect("Unable to create log file")
        }
    };
    
    let mut log_content = String::new();
    if let Err(e) = file.read_to_string(&mut log_content) {
        eprintln!("Failed to read log file: {}", e);
        return HttpResponse::InternalServerError().finish();
    }
    
    HttpResponse::Ok().body(log_content)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let log_file = OpenOptions::new()
        .create(true)
        .append(true)
        .mode(0o600) // Set file permissions to read/write for owner only
        .open("logs.txt")
        .expect("Unable to open log file");

    let state = web::Data::new(AppState {
        log_file: Mutex::new(log_file),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(state.clone())
            .service(log_message)
            .service(get_logs)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}