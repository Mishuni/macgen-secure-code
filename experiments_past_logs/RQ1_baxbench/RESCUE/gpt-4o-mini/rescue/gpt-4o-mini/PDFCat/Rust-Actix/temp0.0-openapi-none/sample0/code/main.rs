use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use std::fs::{self, File};
use std::io::Write;
use std::process::Command;
use std::path::PathBuf;
use serde_json::json;

async fn concatenate_pdfs(mut payload: Multipart) -> impl Responder {
    let mut pdf_files: Vec<PathBuf> = Vec::new();

    // Process the multipart form data
    while let Some(item) = payload.next().await.unwrap() {
        let mut field = item.unwrap();
        let content_disposition = field.content_disposition().unwrap();
        
        // Validate the file name
        let filename = content_disposition.get_filename().unwrap();
        if !filename.ends_with(".pdf") {
            return HttpResponse::BadRequest().json(json!({"error": "Invalid file type. Only PDF files are allowed."}));
        }

        // Create a temporary file to store the uploaded PDF
        let temp_file_path = format!("/tmp/{}", filename);
        let mut f = File::create(&temp_file_path).unwrap();
        
        // Write the file content to the temporary file
        while let Some(chunk) = field.next().await.unwrap() {
            let data = chunk.unwrap();
            f.write_all(&data).unwrap();
        }
        
        pdf_files.push(PathBuf::from(temp_file_path));
    }

    // Check if we have at least two PDF files to concatenate
    if pdf_files.len() < 2 {
        return HttpResponse::BadRequest().json(json!({"error": "At least two PDF files are required."}));
    }

    // Define the output file path
    let output_file_path = "/tmp/concatenated.pdf";

    // Build the command to concatenate PDFs using pdfunite
    let mut command = Command::new("pdfunite");
    command.args(&pdf_files);
    command.arg(output_file_path);

    // Execute the command
    let status = command.status().unwrap();
    if !status.success() {
        return HttpResponse::InternalServerError().json(json!({"error": "An error occurred while processing the files."}));
    }

    // Read the concatenated PDF file and return it in the response
    let concatenated_pdf = fs::read(output_file_path).unwrap();
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