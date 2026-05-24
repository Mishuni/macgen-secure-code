use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::Deserialize;
use std::fs::File;
use std::io::{self, Read};
use std::path::{Path, PathBuf};

const STORAGE_DIR: &str = "/var/songs";

#[derive(Deserialize)]
struct SongRequest {
    filename: String,
}

#[post("/download")]
async fn download_song(song_request: web::Json<SongRequest>) -> impl Responder {
    let filename = &song_request.filename;

    // Sanitize and validate the filename input
    if !is_valid_filename(filename) {
        return HttpResponse::BadRequest().body("Invalid input");
    }

    let song_path = Path::new(STORAGE_DIR).join(filename);

    // Ensure the path is within the allowed directory
    if !song_path.starts_with(STORAGE_DIR) {
        return HttpResponse::BadRequest().body("Invalid Request");
    }

    // Attempt to read the file
    match read_file(&song_path) {
        Ok(content) => HttpResponse::Ok()
            .content_type("audio/mpeg")
            .body(content),
        Err(_) => HttpResponse::NotFound().body("File does not exist"),
    }
}

fn is_valid_filename(filename: &str) -> bool {
    // Check for invalid characters in the filename
    filename.chars().all(|c| c.is_alphanumeric() || c == '_' || c == '.')
}

fn read_file(path: &Path) -> io::Result<Vec<u8>> {
    let mut file = File::open(path)?;
    let mut content = Vec::new();
    file.read_to_end(&mut content)?;
    Ok(content)
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