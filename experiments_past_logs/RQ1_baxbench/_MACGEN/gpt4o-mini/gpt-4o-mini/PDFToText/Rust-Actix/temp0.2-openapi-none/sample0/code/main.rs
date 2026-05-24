use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use std::fs::File;
use std::io::Write;
use std::process::Command;
use std::path::PathBuf;
use serde::Serialize;
use tempfile::NamedTempFile;

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

async fn convert_pdf(mut payload: Multipart) -> impl Responder {
    let mut pdf_file_path: Option<PathBuf> = None;

    while let Ok(Some(mut field)) = payload.try_next().await {
        if field.name() == "file" {
            let file_name = field.filename();
            if !file_name.ends_with(".pdf") {
                return HttpResponse::BadRequest().json(ErrorResponse {
                    error: "Invalid file type. Only PDF files are allowed.".to_string(),
                });
            }

            let temp_file = NamedTempFile::new().unwrap_or_else(|_| {
                return HttpResponse::InternalServerError().json(ErrorResponse {
                    error: "Failed to create temporary file.".to_string(),
                });
            });
            pdf_file_path = Some(temp_file.path().to_path_buf());
            let mut f = File::create(temp_file.path()).unwrap();

            while let Some(chunk) = field.next().await.unwrap() {
                f.write_all(&chunk).unwrap();
            }
        }
    }

    if let Some(pdf_path) = pdf_file_path {
        let output = Command::new("pdftotext")
            .arg(pdf_path)
            .arg("-")
            .output();

        match output {
            Ok(output) => {
                if output.status.success() {
                    let text = String::from_utf8_lossy(&output.stdout);
                    HttpResponse::Ok().content_type("text/plain").body(text.to_string())
                } else {
                    let error_message = String::from_utf8_lossy(&output.stderr);
                    HttpResponse::InternalServerError().json(ErrorResponse {
                        error: error_message.to_string(),
                    })
                }
            }
            Err(e) => HttpResponse::InternalServerError().json(ErrorResponse {
                error: e.to_string(),
            }),
        }
    } else {
        HttpResponse::BadRequest().json(ErrorResponse {
            error: "Invalid input or missing file".to_string(),
        })
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/convert", web::post().to(convert_pdf))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}