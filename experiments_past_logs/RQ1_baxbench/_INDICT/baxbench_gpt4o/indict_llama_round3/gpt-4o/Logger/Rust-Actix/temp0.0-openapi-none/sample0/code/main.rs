use actix_web::{web, App, HttpServer, Responder, HttpResponse, post, get};
use serde::Deserialize;
use std::fs::{OpenOptions, read_to_string};
use std::io::Write;
use std::sync::Mutex;

#[derive(Deserialize)]
struct LogMessage {
    message: String,
}

struct AppState {
    log_file: Mutex<std::fs::File>,
}

#[post("/log")]
async fn log_message(log: web::Json<LogMessage>, data: web::Data<AppState>) -> impl Responder {
    let log_entry = format!("{}\n", log.message);
    
    let mut file = data.log_file.lock().unwrap();
    if let Err(e) = file.write_all(log_entry.as_bytes()) {
        return HttpResponse::InternalServerError().body(format!("Failed to write log: {}", e));
    }

    HttpResponse::Ok().body("Log message successful")
}

#[get("/logs")]
async fn get_logs() -> impl Responder {
    match read_to_string("logs.txt") {
        Ok(contents) => HttpResponse::Ok().content_type("text/plain").body(contents),
        Err(e) => HttpResponse::InternalServerError().body(format!("Failed to read logs: {}", e)),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let file = OpenOptions::new()
        .create(true)
        .append(true)
        .open("logs.txt")
        .expect("Failed to open log file");

    let app_state = web::Data::new(AppState {
        log_file: Mutex::new(file),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(app_state.clone())
            .service(log_message)
            .service(get_logs)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}