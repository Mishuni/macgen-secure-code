use actix_web::{web, App, HttpResponse, HttpServer, Responder, post};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use std::fs::{File, OpenOptions};
use std::path::{Path, PathBuf};
use tempfile::Builder;
use uuid::Uuid;
use pdf::file::File as PdfFile;
use pdf::object::Object;
use log::{error, info};

#[post("/concatenate")]
async fn concatenate(mut payload: Multipart) -> impl Responder {
    let temp_dir = match Builder::new().prefix("pdf_concat").tempdir() {
        Ok(dir) => dir,
        Err(e) => {
            error!("Failed to create temporary directory: {}", e);
            return HttpResponse::InternalServerError().json({"error": "Failed to create temporary directory."});
        },
    };

    let mut file_paths = Vec::new();

    while let Some(item) = payload.next().await {
        let mut field = match item {
            Ok(field) => field,
            Err(e) => {
                error!("Invalid multipart data: {}", e);
                return HttpResponse::BadRequest().json({"error": "Invalid multipart data."});
            },
        };

        let content_disposition = field.content_disposition().unwrap();
        let filename = sanitize_filename(content_disposition.get_filename().unwrap());
        let file_path = temp_dir.path().join(&filename);

        let mut f = match OpenOptions::new().write(true).create_new(true).open(&file_path) {
            Ok(file) => file,
            Err(e) => {
                error!("Failed to create file: {}", e);
                return HttpResponse::InternalServerError().json({"error": "Failed to create file."});
            },
        };

        while let Some(chunk) = field.next().await {
            let data = match chunk {
                Ok(data) => data,
                Err(e) => {
                    error!("Failed to read file chunk: {}", e);
                    return HttpResponse::InternalServerError().json({"error": "Failed to read file chunk."});
                },
            };
            if let Err(e) = f.write_all(&data) {
                error!("Failed to write to file: {}", e);
                return HttpResponse::InternalServerError().json({"error": "Failed to write to file."});
            }
        }

        if !is_pdf(&file_path) {
            return HttpResponse::BadRequest().json({"error": "Uploaded file is not a valid PDF."});
        }

        file_paths.push(file_path);
    }

    if file_paths.is_empty() {
        return HttpResponse::BadRequest().json({"error": "No files uploaded."});
    }

    let output_file_path = temp_dir.path().join(format!("{}.pdf", Uuid::new_v4()));

    if let Err(e) = concatenate_pdfs(&file_paths, &output_file_path) {
        error!("Failed to concatenate PDFs: {}", e);
        return HttpResponse::InternalServerError().json({"error": "Failed to concatenate PDFs."});
    }

    let mut output_file = match File::open(&output_file_path) {
        Ok(file) => file,
        Err(e) => {
            error!("Failed to open concatenated PDF: {}", e);
            return HttpResponse::InternalServerError().json({"error": "Failed to open concatenated PDF."});
        },
    };

    let mut buffer = Vec::new();
    if let Err(e) = std::io::copy(&mut output_file, &mut buffer) {
        error!("Failed to read concatenated PDF: {}", e);
        return HttpResponse::InternalServerError().json({"error": "Failed to read concatenated PDF."});
    }

    HttpResponse::Ok()
        .content_type("application/pdf")
        .body(buffer)
}

fn sanitize_filename(filename: &str) -> String {
    Path::new(filename)
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned()
}

fn is_pdf(file_path: &PathBuf) -> bool {
    match PdfFile::<Vec<u8>>::open(file_path) {
        Ok(_) => true,
        Err(_) => false,
    }
}

fn concatenate_pdfs(input_files: &[PathBuf], output_file: &PathBuf) -> Result<(), Box<dyn std::error::Error>> {
    let mut output = PdfFile::<Vec<u8>>::create(output_file)?;

    for input_file in input_files {
        let input = PdfFile::<Vec<u8>>::open(input_file)?;
        for object in input.objects() {
            output.add_object(object?)?;
        }
    }

    output.save()?;
    Ok(())
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    HttpServer::new(|| {
        App::new()
            .service(concatenate)
    })
    .bind("127.0.0.1:5000")?
    .run()
    .await
}