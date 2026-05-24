use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use tempfile::NamedTempFile;
use std::io::Write;
use std::process::Command;
use std::path::{PathBuf, Path};
use serde_json::json;
use std::io::Error as IoError;

async fn convert_pdf(mut payload: Multipart) -> impl Responder {
    let mut file_path: Option<PathBuf> = None;

    // Process the multipart form data
    while let Ok(Some(mut field)) = payload.try_next().await {
        let content_disposition = field.content_disposition();
        if let Some(filename) = content_disposition.get_filename() {
            // Validate the file type and size
            if !is_valid_pdf(filename) {
                return HttpResponse::BadRequest().json(json!({"error": "Invalid file type. Only PDF files are allowed."}));
            }

            // Create a secure temporary file to store the uploaded PDF
            let temp_file = NamedTempFile::new().map_err(|e| {
                HttpResponse::InternalServerError().json(json!({"error": format!("Failed to create temporary file: {}", e)}))
            })?;
            file_path = Some(temp_file.path().to_path_buf());

            // Write the file to the temporary location
            while let Some(chunk) = field.next().await.unwrap() {
                temp_file.as_file().write_all(&chunk).map_err(|e| {
                    HttpResponse::InternalServerError().json(json!({"error": format!("Failed to write to file: {}", e)}))
                })?;
            }
        }
    }

    // Check if the file was uploaded
    if let Some(pdf_path) = file_path {
        // Prepare the command to convert PDF to text
        let output = Command::new("pdftotext")
            .arg(pdf_path.clone())
            .arg("-") // Output to stdout
            .output();

        match output {
            Ok(output) => {
                if output.status.success() {
                    // Convert the output to a string
                    let text = String::from_utf8_lossy(&output.stdout);
                    return HttpResponse::Ok().content_type("text/plain").body(text.to_string());
                } else {
                    return HttpResponse::InternalServerError().json(json!({"error": "Conversion failed"}));
                }
            }
            Err(e) => {
                return HttpResponse::InternalServerError().json(json!({"error": format!("Failed to execute conversion command: {}", e)}));
            }
        }
    }

    HttpResponse::BadRequest().json(json!({"error": "Invalid input or missing file"}))
}

// Function to validate if the uploaded file is a PDF
fn is_valid_pdf(filename: &str) -> bool {
    let extension = Path::new(filename).extension().and_then(|s| s.to_str()).unwrap_or("");
    extension.eq_ignore_ascii_case("pdf")
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