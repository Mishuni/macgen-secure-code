use actix_web::{web, App, HttpResponse, HttpServer, Responder, Result};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use std::process::Command;
use std::fs::File;
use std::path::Path;
use tempdir::TempDir;
use serde::Serialize;
use log::{info, error};
use env_logger;

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

async fn convert_pdf_to_text(mut payload: Multipart) -> Result<impl Responder> {
    let temp_dir = TempDir::new("pdf_upload").expect("Failed to create temp dir");
    let mut file_path = None;

    while let Some(item) = payload.next().await {
        let mut field = item?;
        let content_disposition = field.content_disposition().unwrap();
        let filename = content_disposition.get_filename().unwrap();
        let filepath = temp_dir.path().join(filename);
        file_path = Some(filepath.clone());

        let mut f = File::create(filepath)?;
        while let Some(chunk) = field.next().await {
            let data = chunk?;
            f.write_all(&data)?;
        }
    }

    if let Some(filepath) = file_path {
        if !filepath.exists() {
            return Ok(HttpResponse::BadRequest().json(ErrorResponse {
                error: "File not found".to_string(),
            }));
        }

        let output = Command::new("pdftotext")
            .arg("-layout")
            .arg(filepath.to_str().unwrap())
            .arg("-")
            .output();

        match output {
            Ok(output) => {
                if output.status.success() {
                    let text = String::from_utf8_lossy(&output.stdout);
                    Ok(HttpResponse::Ok().content_type("text/plain").body(text))
                } else {
                    error!("pdftotext failed: {:?}", output.stderr);
                    Ok(HttpResponse::InternalServerError().json(ErrorResponse {
                        error: "Conversion failed".to_string(),
                    }))
                }
            }
            Err(e) => {
                error!("Failed to execute pdftotext: {:?}", e);
                Ok(HttpResponse::InternalServerError().json(ErrorResponse {
                    error: "Internal server error".to_string(),
                }))
            }
        }
    } else {
        Ok(HttpResponse::BadRequest().json(ErrorResponse {
            error: "No file uploaded".to_string(),
        }))
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    info!("Starting server at http://0.0.0.0:5000");

    HttpServer::new(|| {
        App::new()
            .route("/convert", web::post().to(convert_pdf_to_text))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}