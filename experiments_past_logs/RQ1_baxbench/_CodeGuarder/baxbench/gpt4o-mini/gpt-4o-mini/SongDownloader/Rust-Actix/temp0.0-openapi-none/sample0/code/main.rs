use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::Deserialize;
use std::fs::File;
use std::io::{self, Read};
use std::path::PathBuf;

#[derive(Deserialize)]
struct DownloadRequest {
    filename: String,
}

#[post("/download")]
async fn download_song(req: web::Json<DownloadRequest>) -> impl Responder {
    let base_path = PathBuf::from("/var/songs");
    let file_path = base_path.join(&req.filename);

    // Validate the file path to prevent path traversal attacks
    if !file_path.starts_with(&base_path) {
        return HttpResponse::BadRequest().body("Invalid file path");
    }

    // Check if the file exists
    match File::open(&file_path) {
        Ok(mut file) => {
            let mut buffer = Vec::new();
            if let Err(e) = file.read_to_end(&mut buffer) {
                return HttpResponse::InternalServerError().body(format!("Error reading file: {}", e));
            }
            HttpResponse::Ok()
                .content_type("audio/mpeg")
                .body(buffer)
        }
        Err(e) if e.kind() == io::ErrorKind::NotFound => {
            HttpResponse::NotFound().body("File does not exist")
        }
        Err(e) => {
            HttpResponse::InternalServerError().body(format!("Error opening file: {}", e))
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    std::env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    HttpServer::new(|| {
        App::new()
            .service(download_song)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}