use actix_web::{web, App, HttpServer, HttpResponse, Responder, middleware};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use std::fs::{self, File};
use std::path::{Path, PathBuf};
use tempdir::TempDir;
use std::process::Command;
use serde::Serialize;

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

// Helper function to sanitize file names
fn sanitize_filename(filename: &str) -> String {
    filename.chars()
        .filter(|c| c.is_alphanumeric() || *c == '.' || *c == '_')
        .collect()
}

// Handler for the /convert endpoint
async fn convert_pdf(mut payload: Multipart) -> impl Responder {
    // Create a temporary directory for processing
    let temp_dir = match TempDir::new("pdf_to_text") {
        Ok(dir) => dir,
        Err(_) => {
            return HttpResponse::InternalServerError().json(ErrorResponse {
                error: "Failed to create temporary directory".to_string(),
            });
        }
    };

    let mut pdf_path: Option<PathBuf> = None;

    // Process the multipart form data
    while let Some(Ok(mut field)) = payload.next().await {
        let content_disposition = field.content_disposition();
        if let Some(filename) = content_disposition.get_filename() {
            let sanitized_filename = sanitize_filename(filename);
            let file_path = temp_dir.path().join(sanitized_filename);

            let mut file = match File::create(&file_path) {
                Ok(f) => f,
                Err(_) => {
                    return HttpResponse::InternalServerError().json(ErrorResponse {
                        error: "Failed to create file".to_string(),
                    });
                }
            };

            while let Some(Ok(chunk)) = field.next().await {
                if let Err(_) = file.write_all(&chunk) {
                    return HttpResponse::InternalServerError().json(ErrorResponse {
                        error: "Failed to write to file".to_string(),
                    });
                }
            }

            pdf_path = Some(file_path);
        }
    }

    // Ensure a file was uploaded
    let pdf_path = match pdf_path {
        Some(path) => path,
        None => {
            return HttpResponse::BadRequest().json(ErrorResponse {
                error: "No file uploaded".to_string(),
            });
        }
    };

    // Ensure the uploaded file is a PDF
    if pdf_path.extension().and_then(|ext| ext.to_str()) != Some("pdf") {
        return HttpResponse::BadRequest().json(ErrorResponse {
            error: "Uploaded file is not a PDF".to_string(),
        });
    }

    // Convert the PDF to text using `pdftotext`
    let output_path = temp_dir.path().join("output.txt");
    let output = Command::new("pdftotext")
        .arg(&pdf_path)
        .arg(&output_path)
        .output();

    if let Err(_) = output {
        return HttpResponse::InternalServerError().json(ErrorResponse {
            error: "Failed to execute pdftotext".to_string(),
        });
    }

    // Check if the output file was created
    if !output_path.exists() {
        return HttpResponse::InternalServerError().json(ErrorResponse {
            error: "Failed to convert PDF to text".to_string(),
        });
    }

    // Read the converted text
    let text = match fs::read_to_string(&output_path) {
        Ok(content) => content,
        Err(_) => {
            return HttpResponse::InternalServerError().json(ErrorResponse {
                error: "Failed to read converted text".to_string(),
            });
        }
    };

    // Return the text as plain text response
    HttpResponse::Ok()
        .content_type("text/plain")
        .body(text)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize logger
    env_logger::init();

    // Start the server
    HttpServer::new(|| {
        App::new()
            .wrap(middleware::Logger::default())
            .route("/convert", web::post().to(convert_pdf))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}