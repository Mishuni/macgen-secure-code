use actix_web::{web, App, HttpResponse, HttpServer, Responder, post};
use serde::Deserialize;
use std::fs::File;
use std::io::Read;
use std::path::{Path, PathBuf};

#[derive(Deserialize)]
struct SongRequest {
    filename: String,
}

#[post("/download")]
async fn download_song(song_request: web::Json<SongRequest>) -> impl Responder {
    // Use an environment variable or configuration for the base path
    let base_path = std::env::var("SONG_BASE_PATH").unwrap_or_else(|_| "/var/songs".to_string());
    let base_path = Path::new(&base_path);

    // Validate and sanitize the filename
    if !is_valid_filename(&song_request.filename) {
        return HttpResponse::BadRequest().body("Invalid filename");
    }

    let file_path = base_path.join(&song_request.filename);

    // Canonicalize the path to prevent path traversal
    let canonicalized_path = match file_path.canonicalize() {
        Ok(path) => path,
        Err(_) => return HttpResponse::BadRequest().body("Invalid file path"),
    };

    // Ensure the file path is within the base directory
    if !canonicalized_path.starts_with(base_path) {
        return HttpResponse::BadRequest().body("Invalid file path");
    }

    // Open the file directly and handle errors
    let mut file = match File::open(&canonicalized_path) {
        Ok(file) => file,
        Err(_) => return HttpResponse::NotFound().body("File not found"),
    };

    let mut buffer = Vec::new();
    if let Err(_) = file.read_to_end(&mut buffer) {
        return HttpResponse::InternalServerError().body("Error reading file");
    }

    HttpResponse::Ok()
        .content_type("audio/mpeg")
        .body(buffer)
}

// Function to validate the filename
fn is_valid_filename(filename: &str) -> bool {
    // Allow only alphanumeric characters and a limited set of special characters
    let valid_chars = |c: char| c.is_alphanumeric() || c == '_' || c == '-';
    filename.chars().all(valid_chars) && !filename.contains("..")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(download_song)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}