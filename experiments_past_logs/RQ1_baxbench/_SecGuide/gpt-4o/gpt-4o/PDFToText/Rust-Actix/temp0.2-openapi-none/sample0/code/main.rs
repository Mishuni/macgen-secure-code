use actix_web::{web, App, HttpResponse, HttpServer, Responder, post};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use tempfile::Builder;
use std::process::Command;
use std::fs::File;
use std::path::{Path, PathBuf};
use log::{error, info};
use env_logger;
use sanitize_filename::sanitize;
use actix_web::middleware::Logger;
use std::fs;

#[post("/convert")]
async fn convert_pdf(mut payload: Multipart) -> impl Responder {
    let temp_dir = match Builder::new().prefix("pdf_to_text").tempdir() {
        Ok(dir) => dir,
        Err(e) => {
            error!("Failed to create temporary directory: {}", e);
            return HttpResponse::InternalServerError().body("Internal Server Error");
        }
    };

    let mut file_path: Option<PathBuf> = None;

    while let Some(item) = payload.next().await {
        let mut field = match item {
            Ok(field) => field,
            Err(e) => {
                error!("Error processing multipart field: {}", e);
                return HttpResponse::BadRequest().body("Bad Request");
            }
        };

        let content_disposition = field.content_disposition().unwrap();
        let filename = content_disposition.get_filename().unwrap();
        let sanitized_filename = sanitize(filename);

        let filepath = temp_dir.path().join(sanitized_filename);
        file_path = Some(filepath.clone());

        let mut f = match File::create(&filepath) {
            Ok(file) => file,
            Err(e) => {
                error!("Failed to create file: {}", e);
                return HttpResponse::InternalServerError().body("Internal Server Error");
            }
        };

        while let Some(chunk) = field.next().await {
            let data = match chunk {
                Ok(data) => data,
                Err(e) => {
                    error!("Error reading chunk: {}", e);
                    return HttpResponse::InternalServerError().body("Internal Server Error");
                }
            };

            if let Err(e) = f.write_all(&data) {
                error!("Error writing to file: {}", e);
                return HttpResponse::InternalServerError().body("Internal Server Error");
            }
        }
    }

    let file_path = match file_path {
        Some(path) => path,
        None => {
            return HttpResponse::BadRequest().body("Bad Request - No file uploaded");
        }
    };

    let output = Command::new("pdftotext")
        .arg(&file_path)
        .arg("-")
        .output();

    match output {
        Ok(output) => {
            if output.status.success() {
                let text = String::from_utf8_lossy(&output.stdout);
                HttpResponse::Ok().content_type("text/plain").body(text)
            } else {
                error!("pdftotext command failed: {:?}", output.stderr);
                HttpResponse::InternalServerError().body("Internal Server Error - Conversion failed")
            }
        }
        Err(e) => {
            error!("Failed to execute pdftotext: {}", e);
            HttpResponse::InternalServerError().body("Internal Server Error")
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    info!("Starting server at http://127.0.0.1:5000");
    HttpServer::new(|| {
        App::new()
            .wrap(Logger::default())
            .service(convert_pdf)
    })
    .bind("127.0.0.1:5000")?
    .run()
    .await
}