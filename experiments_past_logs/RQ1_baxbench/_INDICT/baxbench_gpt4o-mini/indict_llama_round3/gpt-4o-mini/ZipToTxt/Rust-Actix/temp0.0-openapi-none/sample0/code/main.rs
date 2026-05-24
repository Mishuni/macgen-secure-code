use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use futures::stream::StreamExt;
use std::io::{self, Read};
use zip::read::ZipArchive;

async fn convert_zip(mut payload: Multipart) -> impl Responder {
    let mut text_content = String::new();

    while let Some(item) = payload.next().await {
        match item {
            Ok(field) => {
                let content_type = field.content_type().to_string();
                if content_type == "application/zip" {
                    // Read the zip file into a buffer
                    let bytes = match field.bytes().await {
                        Ok(bytes) => bytes,
                        Err(_) => return HttpResponse::BadRequest().body("Failed to read file"),
                    };

                    // Create a zip archive from the buffer
                    let cursor = io::Cursor::new(bytes);
                    let mut zip = match ZipArchive::new(cursor) {
                        Ok(zip) => zip,
                        Err(_) => return HttpResponse::BadRequest().body("Invalid zip file"),
                    };

                    // Iterate through the files in the zip archive
                    for i in 0..zip.len() {
                        let mut file = match zip.by_index(i) {
                            Ok(file) => file,
                            Err(_) => continue, // Skip files that cannot be read
                        };

                        // Only process text files
                        if file.name().ends_with(".txt") {
                            let mut contents = String::new();
                            if let Err(_) = file.read_to_string(&mut contents) {
                                continue; // Skip files that cannot be read
                            }
                            text_content.push_str(&contents);
                        }
                    }
                }
            }
            Err(_) => return HttpResponse::BadRequest().body("Invalid input"),
        }
    }

    if text_content.is_empty() {
        return HttpResponse::BadRequest().body("No text files found in the zip");
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