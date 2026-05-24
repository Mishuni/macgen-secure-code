use actix_web::{web, App, HttpServer, HttpResponse, Responder, middleware};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::fs::{self, File};
use std::io::Write;
use std::path::{Path, PathBuf};
use tempdir::TempDir;
use std::process::Command;

async fn concatenate_pdfs(mut payload: Multipart) -> impl Responder {
    // Create a temporary directory for storing uploaded files
    let temp_dir = match TempDir::new("pdf_concat") {
        Ok(dir) => dir,
        Err(_) => return HttpResponse::InternalServerError().json({"error": "Failed to create temporary directory"}),
    };

    let mut file_paths = Vec::new();

    // Process each uploaded file
    while let Some(item) = payload.next().await {
        let mut field = match item {
            Ok(f) => f,
            Err(_) => return HttpResponse::BadRequest().json({"error": "Invalid multipart data"}),
        };

        let content_disposition = field.content_disposition();
        let file_name = match content_disposition.get_filename() {
            Some(name) => sanitize_filename::sanitize(name),
            None => return HttpResponse::BadRequest().json({"error": "Missing file name in multipart data"}),
        };

        // Ensure the file has a .pdf extension
        if !file_name.to_lowercase().ends_with(".pdf") {
            return HttpResponse::BadRequest().json({"error": "Only PDF files are allowed"});
        }

        let file_path = temp_dir.path().join(file_name);
        let mut file = match File::create(&file_path) {
            Ok(f) => f,
            Err(_) => return HttpResponse::InternalServerError().json({"error": "Failed to create temporary file"}),
        };

        // Write the file contents
        while let Some(chunk) = field.next().await {
            let data = match chunk {
                Ok(d) => d,
                Err(_) => return HttpResponse::BadRequest().json({"error": "Failed to read file data"}),
            };

            if let Err(_) = file.write_all(&data) {
                return HttpResponse::InternalServerError().json({"error": "Failed to write file data"});
            }
        }

        file_paths.push(file_path);
    }

    // Ensure at least two files were uploaded
    if file_paths.len() < 2 {
        return HttpResponse::BadRequest().json({"error": "At least two PDF files are required for concatenation"});
    }

    // Create the output file path
    let output_file_path = temp_dir.path().join("concatenated.pdf");

    // Use pdfunite to concatenate the files
    let mut command = Command::new("pdfunite");
    for path in &file_paths {
        command.arg(path);
    }
    command.arg(&output_file_path);

    let output = match command.output() {
        Ok(o) => o,
        Err(_) => return HttpResponse::InternalServerError().json({"error": "Failed to execute pdfunite command"}),
    };

    if !output.status.success() {
        return HttpResponse::InternalServerError().json({"error": "Failed to concatenate PDF files"});
    }

    // Read the concatenated file and return it as a response
    let concatenated_pdf = match fs::read(&output_file_path) {
        Ok(data) => data,
        Err(_) => return HttpResponse::InternalServerError().json({"error": "Failed to read concatenated PDF file"}),
    };

    HttpResponse::Ok()
        .content_type("application/pdf")
        .body(concatenated_pdf)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    HttpServer::new(|| {
        App::new()
            .wrap(middleware::Logger::default())
            .route("/concatenate", web::post().to(concatenate_pdfs))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}