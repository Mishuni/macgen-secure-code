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
async fn download_song(req_body: web::Json<SongRequest>) -> impl Responder {
    // Validate the content type
    if !req_body.filename.ends_with(".mp3") {
        return HttpResponse::BadRequest().body("Invalid file type");
    }

    // Construct the file path
    let base_path = Path::new("/var/songs");
    let file_path = base_path.join(&req_body.filename);

    // Validate the file path to prevent path traversal
    if !file_path.starts_with(base_path) {
        return HttpResponse::BadRequest().body("Invalid file path");
    }

    // Check if the file exists
    if !file_path.exists() {
        return HttpResponse::NotFound().body("File does not exist");
    }

    // Open the file and prepare it for streaming
    match File::open(&file_path) {
        Ok(mut file) => {
            let mut buffer = Vec::new();
            if let Err(_) = file.read_to_end(&mut buffer) {
                return HttpResponse::InternalServerError().body("Error reading file");
            }
            HttpResponse::Ok()
                .content_type("audio/mpeg")
                .body(buffer)
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