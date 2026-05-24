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
async fn download_song(req: web::Json<SongRequest>) -> impl Responder {
    let base_path = Path::new("/var/songs");
    let file_path = base_path.join(&req.filename);

    // Ensure the file path is within the base directory to prevent directory traversal
    if !file_path.starts_with(base_path) {
        return HttpResponse::BadRequest().body("Invalid file path");
    }

    // Check if the file exists and is a file
    if !file_path.exists() || !file_path.is_file() {
        return HttpResponse::NotFound().body("File does not exist");
    }

    // Validate that the file is an audio file by checking the extension
    if file_path.extension().and_then(|ext| ext.to_str()) != Some("mp3") {
        return HttpResponse::BadRequest().body("Invalid file type");
    }

    // Open the file and read its contents
    let mut file = match File::open(&file_path) {
        Ok(file) => file,
        Err(_) => return HttpResponse::InternalServerError().body("Failed to open file"),
    };

    let mut buffer = Vec::new();
    if let Err(_) = file.read_to_end(&mut buffer) {
        return HttpResponse::InternalServerError().body("Failed to read file");
    }

    HttpResponse::Ok()
        .content_type("audio/mpeg")
        .body(buffer)
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