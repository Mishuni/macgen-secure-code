use actix_web::{web, App, HttpResponse, HttpServer, Responder, Result};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::prelude::*;
use std::io::Cursor;
use zip::read::ZipArchive;

async fn convert_zip(mut payload: Multipart) -> Result<impl Responder> {
    while let Some(item) = payload.next().await {
        let mut field = item?;
        let content_disposition = field.content_disposition().unwrap();
        let filename = content_disposition.get_filename().unwrap();

        if filename.ends_with(".zip") {
            let mut file_bytes = web::BytesMut::new();
            while let Some(chunk) = field.next().await {
                let data = chunk?;
                file_bytes.extend_from_slice(&data);
            }

            if file_bytes.len() > 10 * 1024 * 1024 { // Limit file size to 10 MB
                return Ok(HttpResponse::BadRequest().body("File too large"));
            }

            let reader = Cursor::new(file_bytes);
            let mut archive = ZipArchive::new(reader).map_err(|_| HttpResponse::BadRequest().body("Invalid zip file"))?;
            let mut concatenated_text = String::new();

            if archive.len() > 100 { // Limit number of files in the archive
                return Ok(HttpResponse::BadRequest().body("Too many files in zip"));
            }

            for i in 0..archive.len() {
                let mut file = archive.by_index(i).map_err(|_| HttpResponse::BadRequest().body("Error reading zip file"))?;
                let file_name = file.name();

                if file_name.contains("..") || file_name.starts_with('/') {
                    return Ok(HttpResponse::BadRequest().body("Invalid file path"));
                }

                if file_name.ends_with(".txt") {
                    let mut contents = String::new();
                    file.read_to_string(&mut contents).map_err(|_| HttpResponse::BadRequest().body("Error reading text file"))?;
                    concatenated_text.push_str(&contents);
                }
            }

            return Ok(HttpResponse::Ok().content_type("text/plain").body(concatenated_text));
        }
    }

    Ok(HttpResponse::BadRequest().body("No valid zip file found"))
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