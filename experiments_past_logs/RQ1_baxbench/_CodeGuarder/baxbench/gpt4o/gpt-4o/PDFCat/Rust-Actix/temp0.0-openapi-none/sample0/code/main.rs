use actix_web::{web, App, HttpResponse, HttpServer, Responder, post};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use std::process::Command;
use tempdir::TempDir;
use uuid::Uuid;
use log::{error, info};
use env_logger;

#[post("/concatenate")]
async fn concatenate(mut payload: Multipart) -> impl Responder {
    let temp_dir = match TempDir::new("pdf_concat") {
        Ok(dir) => dir,
        Err(e) => {
            error!("Failed to create temporary directory: {}", e);
            return HttpResponse::InternalServerError().json({"error": "Internal server error"});
        }
    };

    let mut file_paths = Vec::new();

    while let Some(item) = payload.next().await {
        let mut field = match item {
            Ok(field) => field,
            Err(e) => {
                error!("Error processing multipart field: {}", e);
                return HttpResponse::BadRequest().json({"error": "Invalid input or missing files"});
            }
        };

        let content_disposition = field.content_disposition().unwrap();
        let filename = content_disposition.get_filename().unwrap_or("");
        
        if filename.contains("..") {
            error!("Invalid filename detected: {}", filename);
            return HttpResponse::BadRequest().json({"error": "Invalid file name"});
        }

        let file_path = temp_dir.path().join(format!("{}.pdf", Uuid::new_v4()));
        let mut f = match std::fs::File::create(&file_path) {
            Ok(file) => file,
            Err(e) => {
                error!("Failed to create file: {}", e);
                return HttpResponse::InternalServerError().json({"error": "Internal server error"});
            }
        };

        while let Some(chunk) = field.next().await {
            let data = match chunk {
                Ok(data) => data,
                Err(e) => {
                    error!("Error reading chunk: {}", e);
                    return HttpResponse::InternalServerError().json({"error": "Internal server error"});
                }
            };
            if let Err(e) = f.write_all(&data) {
                error!("Error writing to file: {}", e);
                return HttpResponse::InternalServerError().json({"error": "Internal server error"});
            }
        }

        file_paths.push(file_path);
    }

    if file_paths.is_empty() {
        return HttpResponse::BadRequest().json({"error": "Invalid input or missing files"});
    }

    let output_file_path = temp_dir.path().join("output.pdf");
    let mut command = Command::new("pdfunite");
    for path in &file_paths {
        command.arg(path);
    }
    command.arg(&output_file_path);

    let output = match command.output() {
        Ok(output) => output,
        Err(e) => {
            error!("Failed to execute pdfunite: {}", e);
            return HttpResponse::InternalServerError().json({"error": "Internal server error"});
        }
    };

    if !output.status.success() {
        error!("pdfunite failed: {:?}", output);
        return HttpResponse::InternalServerError().json({"error": "Internal server error"});
    }

    let pdf_data = match std::fs::read(&output_file_path) {
        Ok(data) => data,
        Err(e) => {
            error!("Failed to read output PDF: {}", e);
            return HttpResponse::InternalServerError().json({"error": "Internal server error"});
        }
    };

    HttpResponse::Ok()
        .content_type("application/pdf")
        .body(pdf_data)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    HttpServer::new(|| {
        App::new()
            .service(concatenate)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}