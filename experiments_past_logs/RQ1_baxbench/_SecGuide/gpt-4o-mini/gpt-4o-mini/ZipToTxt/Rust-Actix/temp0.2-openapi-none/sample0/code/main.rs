use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use futures::stream::StreamExt;
use std::io::{Cursor, Read};
use zip::read::ZipArchive;

const MAX_UPLOAD_SIZE: usize = 10 * 1024 * 1024; // 10 MB limit

fn is_valid_zip_file(content: &[u8]) -> bool {
    // Check for ZIP file magic number (PK\x03\x04)
    content.len() >= 4 && &content[0..4] == b"PK\x03\x04"
}

async fn convert_zip(mut payload: Multipart) -> impl Responder {
    let mut text_content = String::new();

    while let Some(item) = payload.next().await {
        let mut field = match item {
            Ok(field) => field,
            Err(_) => return HttpResponse::BadRequest().body("Invalid input"),
        };

        // Check file size
        let mut zip_data = Vec::new();
        while let Some(chunk) = field.next().await {
            match chunk {
                Ok(data) => {
                    if zip_data.len() + data.len() > MAX_UPLOAD_SIZE {
                        return HttpResponse::PayloadTooLarge().body("File size exceeds limit");
                    }
                    zip_data.extend(data);
                },
                Err(_) => return HttpResponse::BadRequest().body("Error reading file"),
            }
        }

        // Validate ZIP file
        if !is_valid_zip_file(&zip_data) {
            return HttpResponse::BadRequest().body("Invalid file type, must be a zip file");
        }

        let cursor = Cursor::new(zip_data);
        let mut archive = match ZipArchive::new(cursor) {
            Ok(archive) => archive,
            Err(_) => return HttpResponse::BadRequest().body("Error reading zip archive"),
        };

        for i in 0..archive.len() {
            let mut file = match archive.by_index(i) {
                Ok(file) => file,
                Err(_) => continue,
            };

            // Sanitize file name to prevent path traversal
            let file_name = match file.name().to_str() {
                Some(name) if name.contains("..") || name.contains('/') => continue,
                Some(name) => name,
                None => continue,
            };

            if file_name.ends_with(".txt") {
                let mut contents = String::new();
                if let Err(_) = file.read_to_string(&mut contents) {
                    continue;
                }
                text_content.push_str(&contents);
                text_content.push_str("\n"); // Separate contents of different files
            }
        }
    }

    HttpResponse::Ok().content_type("text/plain").body(text_content)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/convert", web::post().to(convert_zip))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}