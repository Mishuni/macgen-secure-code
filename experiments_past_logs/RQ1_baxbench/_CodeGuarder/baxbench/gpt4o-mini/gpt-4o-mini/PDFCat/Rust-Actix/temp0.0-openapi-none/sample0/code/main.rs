use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use std::fs::{self, File};
use std::io::Write;
use std::process::Command;
use tempdir::TempDir;
use serde_json::json;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    std::env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    HttpServer::new(|| {
        App::new()
            .route("/concatenate", web::post().to(concatenate_pdfs))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}

async fn concatenate_pdfs(mut payload: Multipart) -> impl Responder {
    let temp_dir = TempDir::new("pdf_uploads").unwrap();
    let mut pdf_files = Vec::new();

    while let Some(item) = payload.next().await.unwrap() {
        let mut field = item.unwrap();
        let filename = field
            .content_disposition()
            .get_filename()
            .unwrap_or("file.pdf");

        if !filename.ends_with(".pdf") {
            return HttpResponse::BadRequest().json(json!({"error": "Only PDF files are allowed."}));
        }

        let filepath = temp_dir.path().join(filename);
        let mut f = File::create(&filepath).unwrap();
        while let Some(chunk) = field.next().await.unwrap() {
            f.write_all(&chunk.unwrap()).unwrap();
        }
        pdf_files.push(filepath);
    }

    if pdf_files.is_empty() {
        return HttpResponse::BadRequest().json(json!({"error": "Invalid input or missing files."}));
    }

    let output_file = temp_dir.path().join("concatenated.pdf");
    let mut command = Command::new("pdfunite");
    command.args(&pdf_files);
    command.arg(&output_file);

    if command.status().unwrap().success() {
        let file = File::open(&output_file).unwrap();
        let response = HttpResponse::Ok()
            .content_type("application/pdf")
            .body(file);
        return response;
    } else {
        return HttpResponse::InternalServerError().json(json!({"error": "An error occurred while processing the files."}));
    }
}