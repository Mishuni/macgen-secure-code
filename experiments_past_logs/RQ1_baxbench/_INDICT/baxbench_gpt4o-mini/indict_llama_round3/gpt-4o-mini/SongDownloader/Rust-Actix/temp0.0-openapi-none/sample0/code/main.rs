use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::Deserialize;
use std::fs::File;
use std::io::{self, BufReader, Read};
use std::path::{Path, PathBuf};
use actix_web::http::header::ContentType;
use actix_web::web::Bytes;

#[derive(Deserialize)]
struct SongRequest {
    filename: String,
}

fn sanitize_filename(filename: &str) -> Option<String> {
    // Basic sanitization to prevent directory traversal attacks
    if filename.contains("..") || filename.contains("/") || filename.contains("\\") {
        None
    } else {
        Some(filename.to_string())
    }
}

#[post("/download")]
async fn download_song(song_request: web::Json<SongRequest>) -> impl Responder {
    let sanitized_filename = match sanitize_filename(&song_request.filename) {
        Some(name) => name,
        None => return HttpResponse::BadRequest().body("Invalid input"),
    };

    let song_path = PathBuf::from(format!("/var/songs/{}", sanitized_filename));

    // Check if the file exists
    if !song_path.exists() {
        return HttpResponse::NotFound().body("File does not exist");
    }

    // Attempt to read the file
    let file = File::open(&song_path);
    match file {
        Ok(file) => {
            let mut reader = BufReader::new(file);
            let mut buffer = Vec::new();
            // Stream the file content instead of reading it all at once
            let mut chunk = vec![0; 8192]; // 8 KB buffer
            let mut response_body = Vec::new();
            while let Ok(bytes_read) = reader.read(&mut chunk) {
                if bytes_read == 0 {
                    break; // End of file
                }
                response_body.extend_from_slice(&chunk[..bytes_read]);
            }
            HttpResponse::Ok()
                .content_type(ContentType::audio_mpeg())
                .body(Bytes::from(response_body))
        }
        Err(_) => HttpResponse::InternalServerError().body("Error opening file"),
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