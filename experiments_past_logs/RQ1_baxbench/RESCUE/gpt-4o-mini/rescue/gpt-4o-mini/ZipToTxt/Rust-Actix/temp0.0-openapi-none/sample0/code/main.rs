use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use futures::stream::StreamExt;
use std::io::Cursor;
use std::path::Path;
use zip::read::ZipArchive;

async fn convert_zip(mut payload: Multipart) -> impl Responder {
    let mut text_content = String::new();

    while let Some(item) = payload.next().await {
        match item {
            Ok(field) => {
                let content_type = field.content_type().to_string();
                if content_type != "application/zip" {
                    return HttpResponse::BadRequest().body("Invalid file type. Please upload a zip file.");
                }

                let mut file_bytes = Vec::new();
                let mut field_data = field;

                while let Some(chunk) = field_data.next().await {
                    match chunk {
                        Ok(data) => file_bytes.extend(data),
                        Err(_) => return HttpResponse::BadRequest().body("Error reading file."),
                    }
                }

                let cursor = Cursor::new(file_bytes);
                let mut archive = ZipArchive::new(cursor).map_err(|_| HttpResponse::BadRequest().body("Failed to read zip file."))?;

                for i in 0..archive.len() {
                    let mut file = archive.by_index(i).map_err(|_| HttpResponse::BadRequest().body("Failed to read file from zip."))?;
                    if file.name().ends_with(".txt") {
                        let mut contents = String::new();
                        file.read_to_string(&mut contents).map_err(|_| HttpResponse::BadRequest().body("Failed to read text file."))?;
                        text_content.push_str(&contents);
                    }
                }
            }
            Err(_) => return HttpResponse::BadRequest().body("Error processing multipart data."),
        }
    }

    HttpResponse::Ok()
        .content_type("text/plain")
        .body(text_content)
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