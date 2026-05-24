use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::Deserialize;
use std::fs::File;
use std::io::{self, Read};
use std::path::Path;

#[derive(Deserialize)]
struct SongRequest {
    filename: String,
}

#[post("/download")]
async fn download_song(song_request: web::Json<SongRequest>) -> impl Responder {
    let filename = &song_request.filename;

    // Validate filename
    if filename.is_empty() || !filename.chars().all(|c| c.is_alphanumeric() || c == '_' || c == '-') {
        return HttpResponse::BadRequest().body("Invalid input");
    }

    // Restrict file extensions
    if !filename.ends_with(".mp3") && !filename.ends_with(".wav") {
        return HttpResponse::BadRequest().body("Invalid file type");
    }

    // Safe path construction
    let file_path = Path::new("/var/songs").join(filename);

    // Check if file exists
    match File::open(&file_path) {
        Ok(mut file) => {
            let mut buffer = Vec::new();
            file.read_to_end(&mut buffer).expect("Failed to read file");
            HttpResponse::Ok()
                .content_type("audio/mpeg")
                .body(buffer)
        }
        Err(_) => HttpResponse::NotFound().body("File does not exist"),
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