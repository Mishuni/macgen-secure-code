use actix_web::{web, App, HttpResponse, HttpServer, Responder, post};
use serde::Deserialize;
use std::fs::File;
use std::io::Read;
use std::path::{Path, PathBuf};
use regex::Regex;

#[derive(Deserialize)]
struct SongRequest {
    filename: String,
}

#[post("/download")]
async fn download_song(req: web::Json<SongRequest>) -> impl Responder {
    let filename = &req.filename;
    let valid_filename = Regex::new(r"^[a-zA-Z0-9_-]+\.mp3$").unwrap();

    if !valid_filename.is_match(filename) {
        return HttpResponse::BadRequest().body("Invalid filename");
    }

    let file_path = Path::new("/var/songs").join(filename);
    let canonical_path = match std::fs::canonicalize(&file_path) {
        Ok(path) => path,
        Err(_) => return HttpResponse::NotFound().body("File does not exist"),
    };

    if !canonical_path.starts_with("/var/songs") {
        return HttpResponse::BadRequest().body("Invalid file path");
    }

    let mut file = match File::open(&canonical_path) {
        Ok(file) => file,
        Err(_) => return HttpResponse::NotFound().body("File does not exist"),
    };

    let mut buffer = Vec::new();
    if let Err(_) = file.read_to_end(&mut buffer) {
        return HttpResponse::InternalServerError().finish();
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