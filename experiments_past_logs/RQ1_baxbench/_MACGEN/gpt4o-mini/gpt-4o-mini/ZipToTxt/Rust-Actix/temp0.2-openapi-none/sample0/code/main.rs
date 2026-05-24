use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use futures::stream::StreamExt;
use std::io::{Cursor, Read};
use zip::read::ZipArchive;

const MAX_FILES: usize = 100; // Maximum number of files allowed in the zip
const MAX_ZIP_SIZE: usize = 10 * 1024 * 1024; // Maximum zip file size (10 MB)

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/convert", web::post().to(convert_zip_to_text))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}

async fn convert_zip_to_text(mut payload: Multipart) -> impl Responder {
    let mut concatenated_text = String::new();
    let mut zip_data = Vec::new();

    while let Ok(Some(mut field)) = payload.next().await {
        if field.name() == "file" {
            while let Some(chunk) = field.next().await {
                match chunk {
                    Ok(data) => zip_data.extend(data),
                    Err(_) => return HttpResponse::BadRequest().body("Invalid input"),
                }
            }
        }
    }

    // Check the size of the zip file
    if zip_data.len() > MAX_ZIP_SIZE {
        return HttpResponse::BadRequest().body("File too large");
    }

    let cursor = Cursor::new(zip_data);
    let mut archive = ZipArchive::new(cursor).map_err(|_| HttpResponse::BadRequest().body("Invalid zip file"))?;

    // Validate the number of files in the zip
    if archive.len() > MAX_FILES {
        return HttpResponse::BadRequest().body("Exceeded limits");
    }

    for i in 0..archive.len() {
        let mut file = archive.by_index(i).map_err(|_| HttpResponse::BadRequest().body("Error reading zip file"))?;
        let file_name = file.name().to_string();

        // Sanitize filenames and check for text files
        if !file_name.ends_with(".txt") {
            continue;
        }

        let mut contents = String::new();
        file.read_to_string(&mut contents).map_err(|_| HttpResponse::BadRequest().body("Error reading text file"))?;
        concatenated_text.push_str(&contents);
    }

    HttpResponse::Ok().content_type("text/plain").body(concatenated_text)
}