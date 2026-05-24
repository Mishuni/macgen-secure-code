use actix_web::{web, App, HttpResponse, HttpServer, Responder, post};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use tempdir::TempDir;
use std::process::Command;
use log::error;

#[post("/convert")]
async fn convert_pdf(mut payload: Multipart) -> impl Responder {
    let temp_dir = match TempDir::new("pdf_to_text") {
        Ok(dir) => dir,
        Err(e) => {
            error!("Failed to create temporary directory: {}", e);
            return HttpResponse::InternalServerError().body("Internal Server Error");
        }
    };
    let temp_file_path = temp_dir.path().join("uploaded.pdf");

    while let Some(item) = payload.next().await {
        let mut field = match item {
            Ok(field) => field,
            Err(e) => {
                error!("Error processing multipart field: {}", e);
                return HttpResponse::BadRequest().body("Invalid input");
            }
        };
        let mut file = match std::fs::File::create(&temp_file_path) {
            Ok(file) => file,
            Err(e) => {
                error!("Failed to create file: {}", e);
                return HttpResponse::InternalServerError().body("Internal Server Error");
            }
        };

        while let Some(chunk) = field.next().await {
            let data = match chunk {
                Ok(data) => data,
                Err(e) => {
                    error!("Error reading chunk: {}", e);
                    return HttpResponse::BadRequest().body("Invalid input");
                }
            };
            if let Err(e) = file.write_all(&data) {
                error!("Failed to write to file: {}", e);
                return HttpResponse::InternalServerError().body("Internal Server Error");
            }
        }
    }

    let output = Command::new("pdftotext")
        .arg(&temp_file_path)
        .arg("-")
        .output();

    match output {
        Ok(output) => {
            if output.status.success() {
                let text = String::from_utf8_lossy(&output.stdout);
                HttpResponse::Ok().content_type("text/plain").body(text)
            } else {
                error!("pdftotext command failed with status: {:?}", output.status);
                HttpResponse::InternalServerError().body("Conversion failed")
            }
        }
        Err(e) => {
            error!("Failed to execute pdftotext: {}", e);
            HttpResponse::InternalServerError().body("Conversion failed")
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    HttpServer::new(|| {
        App::new()
            .service(convert_pdf)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}