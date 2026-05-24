use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use std::fs::{File, remove_file};
use std::io::{Write, Read};
use std::process::Command;
use std::path::PathBuf;
use serde::Serialize;
use futures::stream::StreamExt;

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

async fn convert_pdf(mut payload: Multipart) -> impl Responder {
    let mut pdf_file_path: Option<PathBuf> = None;

    // Process the multipart form data
    while let Ok(Some(mut field)) = payload.try_next().await {
        let content_disposition = field.content_disposition();
        if let Some(file_name) = content_disposition.get_filename() {
            // Validate file extension
            if !file_name.ends_with(".pdf") {
                return HttpResponse::BadRequest().json(ErrorResponse {
                    error: "Invalid file type. Only PDF files are allowed.".to_string(),
                });
            }

            let temp_file_path = std::env::temp_dir().join(file_name);
            pdf_file_path = Some(temp_file_path.clone());

            // Save the uploaded file
            let mut f = File::create(temp_file_path).unwrap();
            while let Some(chunk) = field.next().await {
                let data = chunk.unwrap();
                f.write_all(&data).unwrap();
            }
        }
    }

    // Check if the PDF file was uploaded
    let pdf_file_path = match pdf_file_path {
        Some(path) => path,
        None => {
            return HttpResponse::BadRequest().json(ErrorResponse {
                error: "No file uploaded".to_string(),
            });
        }
    };

    // Convert PDF to text using pdftotext
    let output = Command::new("pdftotext")
        .arg(pdf_file_path.clone())
        .arg("-") // Output to stdout
        .output();

    // Clean up the temporary PDF file
    let _ = remove_file(&pdf_file_path);

    match output {
        Ok(output) => {
            if output.status.success() {
                let text = String::from_utf8_lossy(&output.stdout);
                HttpResponse::Ok().body(text.to_string())
            } else {
                HttpResponse::InternalServerError().json(ErrorResponse {
                    error: "Failed to convert PDF to text".to_string(),
                })
            }
        }
        Err(_) => HttpResponse::InternalServerError().json(ErrorResponse {
            error: "Failed to execute pdftotext".to_string(),
        }),
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