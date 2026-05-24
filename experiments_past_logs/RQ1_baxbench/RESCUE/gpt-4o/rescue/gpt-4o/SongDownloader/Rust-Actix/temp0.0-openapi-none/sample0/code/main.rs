use actix_web::{web, App, HttpServer, HttpResponse, Responder, post};
use serde::Deserialize;
use std::path::{Path, PathBuf};
use std::fs::File;
use std::io::Read;

const STORAGE_DIR: &str = "/var/songs";

#[derive(Deserialize)]
struct SongRequest {
    filename: String,
}

#[post("/download")]
async fn download_song(req: web::Json<SongRequest>) -> impl Responder {
    // Sanitize and validate the filename
    let filename = &req.filename;
    if filename.contains("..") || filename.contains('/') || filename.contains('\\') {
        return HttpResponse::BadRequest().body("Invalid filename");
    }

    // Construct the absolute path to the file
    let file_path = Path::new(STORAGE_DIR).join(filename);

    // Ensure the file is within the allowed directory
    match file_path.canonicalize() {
        Ok(abs_path) => {
            if !abs_path.starts_with(STORAGE_DIR) {
                return HttpResponse::BadRequest().body("Invalid file path");
            }

            // Check if the file exists and is a regular file
            if abs_path.is_file() {
                // Stream the file content
                match File::open(&abs_path) {
                    Ok(mut file) => {
                        let mut buffer = Vec::new();
                        if let Err(_) = file.read_to_end(&mut buffer) {
                            return HttpResponse::InternalServerError().body("Failed to read file");
                        }
                        HttpResponse::Ok()
                            .content_type("audio/mpeg")
                            .body(buffer)
                    }
                    Err(_) => HttpResponse::InternalServerError().body("Failed to open file"),
                }
            } else {
                HttpResponse::NotFound().body("File does not exist")
            }
        }
        Err(_) => HttpResponse::BadRequest().body("Invalid file path"),
    }
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