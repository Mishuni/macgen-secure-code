use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use std::fs::File;
use std::io::Write;
use std::path::PathBuf;
use std::process::Command;
use serde_json::json;

async fn convert_pdf(mut payload: Multipart) -> impl Responder {
    let mut pdf_file_path: Option<PathBuf> = None;

    // Process the multipart form data
    while let Ok(Some(mut field)) = payload.try_next().await {
        if field.name() == "file" {
            // Create a temporary file to store the uploaded PDF
            let temp_file = tempfile::NamedTempFile::new().expect("Failed to create temp file");
            pdf_file_path = Some(temp_file.path().to_path_buf());

            // Write the uploaded file to the temporary file
            while let Some(chunk) = field.next().await {
                let data = chunk.expect("Failed to read chunk");
                temp_file.write_all(&data).expect("Failed to write to temp file");
            }
        }
    }

    // Check if the PDF file was uploaded
    let pdf_file_path = match pdf_file_path {
        Some(path) => path,
        None => return HttpResponse::BadRequest().json(json!({"error": "Missing file"})),
    };

    // Prepare the command to convert PDF to text
    let output = Command::new("pdftotext")
        .arg(pdf_file_path)
        .arg("-") // Output to stdout
        .output()
        .expect("Failed to execute pdftotext");

    // Check if the conversion was successful
    if output.status.success() {
        let text = String::from_utf8_lossy(&output.stdout);
        HttpResponse::Ok().content_type("text/plain").body(text.to_string())
    } else {
        let error_message = String::from_utf8_lossy(&output.stderr);
        HttpResponse::InternalServerError().json(json!({"error": error_message}))
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