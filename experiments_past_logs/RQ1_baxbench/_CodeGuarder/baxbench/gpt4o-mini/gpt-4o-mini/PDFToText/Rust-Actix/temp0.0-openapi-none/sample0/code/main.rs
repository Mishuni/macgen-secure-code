use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use std::fs::File;
use std::io::Write;
use std::process::Command;
use std::path::PathBuf;
use std::sync::Mutex;
use log::{info, error};
use serde::Serialize;

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

async fn convert_pdf(mut payload: Multipart) -> impl Responder {
    let mut pdf_file_path: Option<PathBuf> = None;

    while let Ok(Some(mut field)) = payload.try_next().await {
        let content_disposition = field.content_disposition();
        if let Some(file_name) = content_disposition.get_filename() {
            let file_path = format!("/tmp/{}", sanitize_filename::sanitize(file_name));
            pdf_file_path = Some(PathBuf::from(&file_path));
            let mut f = File::create(&file_path).map_err(|e| {
                error!("Failed to create file: {}", e);
                HttpResponse::InternalServerError().json(ErrorResponse {
                    error: "Internal Server Error".to_string(),
                })
            })?;
            while let Some(chunk) = field.next().await {
                let data = chunk.map_err(|e| {
                    error!("Failed to read chunk: {}", e);
                    HttpResponse::InternalServerError().json(ErrorResponse {
                        error: "Internal Server Error".to_string(),
                    })
                })?;
                f.write_all(&data).map_err(|e| {
                    error!("Failed to write to file: {}", e);
                    HttpResponse::InternalServerError().json(ErrorResponse {
                        error: "Internal Server Error".to_string(),
                    })
                })?;
            }
        }
    }

    if let Some(pdf_path) = pdf_file_path {
        let output = Command::new("pdftotext")
            .arg(pdf_path)
            .arg("-")
            .output()
            .map_err(|e| {
                error!("Failed to execute pdftotext: {}", e);
                HttpResponse::InternalServerError().json(ErrorResponse {
                    error: "Internal Server Error".to_string(),
                })
            })?;

        if output.status.success() {
            let text = String::from_utf8_lossy(&output.stdout);
            return HttpResponse::Ok().body(text.to_string());
        } else {
            error!("pdftotext failed with status: {}", output.status);
            return HttpResponse::InternalServerError().json(ErrorResponse {
                error: "Conversion failed".to_string(),
            });
        }
    }

    HttpResponse::BadRequest().json(ErrorResponse {
        error: "Invalid input or missing file".to_string(),
    })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    info!("Starting server at http://0.0.0.0:5000");

    HttpServer::new(|| {
        App::new()
            .route("/convert", web::post().to(convert_pdf))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}