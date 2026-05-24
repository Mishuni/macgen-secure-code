use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::Deserialize;
use std::fs::File;
use std::io::{self, BufReader, Read};
use std::path::{Path, PathBuf};

#[derive(Deserialize)]
struct SongRequest {
    filename: String,
}

fn is_valid_filename(filename: &str) -> bool {
    // Allow only alphanumeric characters, underscores, and dashes
    filename.chars().all(|c| c.is_alphanumeric() || c == '_' || c == '-')
}

fn sanitize_path(base: &Path, filename: &str) -> Option<PathBuf> {
    let sanitized_filename = filename.replace("..", ""); // Remove path traversal attempts
    let path = base.join(sanitized_filename);
    if path.starts_with(base) {
        Some(path)
    } else {
        None
    }
}

#[post("/download")]
async fn download_song(song_request: web::Json<SongRequest>) -> impl Responder {
    if !is_valid_filename(&song_request.filename) {
        return HttpResponse::BadRequest().body("Invalid filename");
    }

    let base_path = Path::new("/var/songs");
    let song_path = match sanitize_path(base_path, &song_request.filename) {
        Some(path) => path,
        None => return HttpResponse::BadRequest().body("Invalid file path"),
    };

    // Check if the file exists
    if !song_path.exists() || !song_path.is_file() {
        return HttpResponse::NotFound().body("File does not exist");
    }

    // Attempt to read the file
    match File::open(&song_path) {
        Ok(file) => {
            let mut reader = BufReader::new(file);
            let mut buffer = Vec::new();
            // Stream the file directly to the response
            if let Err(e) = reader.read_to_end(&mut buffer) {
                return HttpResponse::InternalServerError().body("Error reading file");
            }
            // Dynamically determine content type based on file extension
            let content_type = if song_path.extension().and_then(|s| s.to_str()) == Some("mp3") {
                "audio/mpeg"
            } else {
                "application/octet-stream"
            };
            HttpResponse::Ok()
                .content_type(content_type)
                .body(buffer)
        }
        Err(_) => {
            HttpResponse::InternalServerError().body("Error opening file")
        }
    }
}

#[actix_web::main]
async fn main() -> io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(download_song)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}