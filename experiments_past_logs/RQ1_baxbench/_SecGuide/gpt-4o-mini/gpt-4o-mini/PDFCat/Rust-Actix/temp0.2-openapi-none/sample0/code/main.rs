use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use std::process::Command;
use std::fs::{self, File};
use std::io::{self, Write};
use std::path::{PathBuf, Path};
use tempfile::tempdir;
use mime_guess::from_path;

async fn concatenate_pdfs(mut payload: Multipart) -> impl Responder {
    let temp_dir = tempdir().expect("Failed to create temporary directory");
    let mut pdf_files: Vec<PathBuf> = Vec::new();

    while let Ok(Some(mut field)) = payload.try_next().await {
        let content_disposition = field.content_disposition();
        let filename = content_disposition.get_filename().unwrap_or("file.pdf");
        
        // Validate the file type
        if !is_valid_pdf(&field).await {
            return HttpResponse::BadRequest().json("Invalid file type. Only PDF files are allowed.");
        }

        let filepath = temp_dir.path().join(sanitize_filename(filename));
        
        // Save the uploaded file to the temporary directory
        let mut f = File::create(&filepath).expect("Failed to create file");
        while let Some(chunk) = field.next().await {
            let data = chunk.expect("Failed to read chunk");
            f.write_all(&data).expect("Failed to write data");
        }
        pdf_files.push(filepath);
    }

    // Prepare the output file path
    let output_file = temp_dir.path().join("concatenated.pdf");

    // Build the command to concatenate PDFs
    let mut command = Command::new("pdfunite");
    command.args(pdf_files.iter().map(|p| p.to_str().unwrap()).chain(std::iter::once(output_file.to_str().unwrap())));

    // Execute the command
    let status = command.status().expect("Failed to execute pdfunite");
    if !status.success() {
        return HttpResponse::InternalServerError().json("An error occurred while processing the files.");
    }

    // Read the concatenated PDF file
    let concatenated_pdf = File::open(&output_file).expect("Failed to open concatenated PDF");
    let mut buffer = Vec::new();
    io::copy(&mut concatenated_pdf.take(10_000_000), &mut buffer).expect("Failed to read concatenated PDF");

    // Clean up temporary files
    if let Err(e) = fs::remove_dir_all(temp_dir) {
        eprintln!("Failed to remove temporary directory: {}", e);
    }

    HttpResponse::Ok()
        .content_type("application/pdf")
        .body(buffer)
}

// Function to validate if the file is a PDF
async fn is_valid_pdf(field: &actix_multipart::Field) -> bool {
    let content_type = field.content_type().to_string();
    content_type == "application/pdf"
}

// Function to sanitize the filename
fn sanitize_filename(filename: &str) -> String {
    let path = Path::new(filename);
    path.file_name()
        .and_then(|name| name.to_str())
        .unwrap_or("file.pdf")
        .to_string()
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