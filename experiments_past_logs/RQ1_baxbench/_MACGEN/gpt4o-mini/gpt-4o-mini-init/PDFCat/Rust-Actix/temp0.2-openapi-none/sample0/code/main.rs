use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use std::fs::{self, File};
use std::io::Write;
use std::process::Command;
use std::path::PathBuf;
use tempfile::tempdir;

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

async fn concatenate_pdfs(mut payload: Multipart) -> impl Responder {
    let temp_dir = match tempdir() {
        Ok(dir) => dir,
        Err(_) => return HttpResponse::InternalServerError().json("Failed to create temporary directory."),
    };

    let mut pdf_files: Vec<PathBuf> = Vec::new();

    while let Ok(Some(mut field)) = payload.try_next().await {
        let content_disposition = field.content_disposition();
        let filename = content_disposition.get_filename().unwrap_or("file.pdf");

        // Validate filename
        if !filename.chars().all(|c| c.is_alphanumeric() || c == '.') {
            return HttpResponse::BadRequest().json("Invalid filename.");
        }

        let filepath = temp_dir.path().join(filename);
        let mut f = match File::create(&filepath) {
            Ok(file) => file,
            Err(_) => return HttpResponse::InternalServerError().json("Failed to create file."),
        };

        while let Some(chunk) = field.next().await.unwrap() {
            if let Err(_) = f.write_all(&chunk) {
                return HttpResponse::InternalServerError().json("Failed to write to file.");
            }
        }

        pdf_files.push(filepath);
    }

    if pdf_files.is_empty() {
        return HttpResponse::BadRequest().json("Invalid input or missing files.");
    }

    let output_file = temp_dir.path().join("concatenated.pdf");
    let mut command = Command::new("pdfunite");

    command.args(pdf_files.iter().map(|p| p.to_str().unwrap_or("")).chain(std::iter::once(output_file.to_str().unwrap())));

    if command.status().is_err() {
        return HttpResponse::InternalServerError().json("An error occurred while processing the files.");
    }

    let response = HttpResponse::Ok()
        .content_type("application/pdf")
        .body(fs::read(output_file).unwrap_or_else(|_| vec![]));

    // Clean up temporary directory
    let _ = fs::remove_dir_all(temp_dir);

    response
}