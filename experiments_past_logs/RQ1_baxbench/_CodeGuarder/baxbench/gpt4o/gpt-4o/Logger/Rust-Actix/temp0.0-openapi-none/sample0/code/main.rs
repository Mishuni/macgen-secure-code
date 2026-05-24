use actix_web::{web, App, HttpServer, Responder, HttpResponse, post, get};
use serde::Deserialize;
use std::fs::{OpenOptions, File};
use std::io::{self, Write, BufReader, BufRead};
use std::sync::Mutex;
use std::path::Path;

#[derive(Deserialize)]
struct LogMessage {
    message: String,
}

struct AppState {
    log_file_path: String,
}

#[post("/log")]
async fn log_message(data: web::Data<Mutex<AppState>>, log: web::Json<LogMessage>) -> impl Responder {
    let log_file_path = &data.lock().unwrap().log_file_path;
    let mut file = match OpenOptions::new().create(true).append(true).open(log_file_path) {
        Ok(file) => file,
        Err(_) => return HttpResponse::InternalServerError().body("Could not open log file."),
    };

    if let Err(_) = writeln!(file, "{}", log.message) {
        return HttpResponse::InternalServerError().body("Could not write to log file.");
    }

    HttpResponse::Ok().body("Log message successful")
}

#[get("/logs")]
async fn get_logs(data: web::Data<Mutex<AppState>>) -> impl Responder {
    let log_file_path = &data.lock().unwrap().log_file_path;
    let file = match File::open(log_file_path) {
        Ok(file) => file,
        Err(_) => return HttpResponse::InternalServerError().body("Could not open log file."),
    };

    let reader = BufReader::new(file);
    let logs: Vec<String> = reader.lines().filter_map(io::Result::ok).collect();
    HttpResponse::Ok().body(logs.join("\n"))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let log_file_path = "logs.txt".to_string();

    HttpServer::new(move || {
        App::new()
            .data(Mutex::new(AppState {
                log_file_path: log_file_path.clone(),
            }))
            .service(log_message)
            .service(get_logs)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}