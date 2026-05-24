use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use futures::StreamExt;
use std::io::Cursor;
use std::collections::HashMap;
use zip::read::ZipArchive;
use std::str;

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

async fn convert_zip(mut payload: Multipart) -> impl Responder {
    let mut text_content = String::new();

    while let Some(item) = payload.next().await {
        match item {
            Ok(field) => {
                let content_type = field.content_type().to_string();
                if content_type == "application/zip" {
                    let mut zip_file = field.bytes().await.unwrap();
                    let cursor = Cursor::new(zip_file);
                    let mut archive = ZipArchive::new(cursor).unwrap();

                    for i in 0..archive.len() {
                        let mut file = archive.by_index(i).unwrap();
                        let file_name = file.name().to_string();

                        // Check for path traversal
                        if file_name.contains("..") {
                            return HttpResponse::BadRequest().body("Invalid file path in zip entry");
                        }

                        if file_name.ends_with(".txt") {
                            let mut contents = String::new();
                            file.read_to_string(&mut contents).unwrap();
                            text_content.push_str(&contents);
                        }
                    }
                } else {
                    return HttpResponse::BadRequest().body("Invalid file type, only zip files are accepted");
                }
            }
            Err(_) => {
                return HttpResponse::BadRequest().body("Error processing the file");
            }
        }
    }

    HttpResponse::Ok()
        .content_type("text/plain")
        .body(text_content)
}