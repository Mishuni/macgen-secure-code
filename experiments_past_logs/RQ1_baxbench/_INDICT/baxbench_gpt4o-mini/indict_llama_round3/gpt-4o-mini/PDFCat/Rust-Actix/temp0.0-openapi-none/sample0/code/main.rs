use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use futures::stream::StreamExt;
use std::fs::{self, File};
use std::io::Write;
use std::process::Command;
use std::path::PathBuf;
use serde_json::json;
use uuid::Uuid;

async fn concatenate_pdfs(mut payload: Multipart) -> impl Responder {
    let mut pdf_files: Vec<PathBuf> = Vec::new();

    // Process the multipart form data
    while let Ok(Some(mut field)) = payload.try_next().await {
        let content_disposition = field.content_disposition();
        let filename = content_disposition.get_filename().unwrap_or("file.pdf");

        // Validate filename to prevent directory traversal attacks
        if filename.contains("..") || filename.contains("/") || filename.contains("\\") {
            return HttpResponse::BadRequest().json(json!({"error": "Invalid filename."}));
        }

        // Generate a unique temporary file name to prevent overwriting
        let unique_filename = format!("/tmp/{}.pdf", Uuid::new_v4());
        let filepath = PathBuf::from(unique_filename);

        // Save the uploaded file to a temporary location
        let mut f = File::create(&filepath).map_err(|_| HttpResponse::InternalServerError().json(json!({"error": "Failed to create temporary file."})))?;
        while let Some(chunk) = field.next().await.unwrap() {
            f.write_all(&chunk).map_err(|_| HttpResponse::InternalServerError().json(json!({"error": "Failed to write to temporary file."})))?;
        }
        pdf_files.push(filepath);
    }

    // Check if any files were uploaded
    if pdf_files.is_empty() {
        return HttpResponse::BadRequest().json(json!({"error": "No files uploaded."}));
    }

    // Create a path for the concatenated PDF
    let output_filepath = format!("/tmp/{}.pdf", Uuid::new_v4());

    // Prepare the command to concatenate PDFs using pdfunite
    let mut command = Command::new("pdfunite");
    command.args(pdf_files.iter().map(|p| p.to_str().unwrap()).chain(std::iter::once(output_filepath.as_str())));

    // Execute the command
    let status = command.status().map_err(|_| HttpResponse::InternalServerError().json(json!({"error": "Failed to execute pdfunite."})))?;
    if !status.success() {
        // Clean up temporary files
        for path in pdf_files {
            let _ = fs::remove_file(path);
        }
        return HttpResponse::InternalServerError().json(json!({"error": "An error occurred while processing the files."}));
    }

    // Read the concatenated PDF file
    let concatenated_pdf = fs::read(&output_filepath).map_err(|_| HttpResponse::InternalServerError().json(json!({"error": "Failed to read concatenated PDF."})))?;

    // Clean up temporary files
    for path in pdf_files {
        let _ = fs::remove_file(path);
    }
    let _ = fs::remove_file(output_filepath);

    // Return the concatenated PDF
    HttpResponse::Ok()
        .content_type("application/pdf")
        .body(concatenated_pdf)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/concatenate", web::post().to(concatenate_pdfs))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}