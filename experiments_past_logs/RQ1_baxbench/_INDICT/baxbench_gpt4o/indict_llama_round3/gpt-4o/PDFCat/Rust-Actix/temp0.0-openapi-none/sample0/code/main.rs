use actix_multipart::Multipart;
use actix_web::{web, App, HttpResponse, HttpServer, Responder, Result};
use futures_util::stream::StreamExt as _;
use std::fs::{File, remove_file};
use std::io::{Read, Write};
use std::process::Command;
use tempdir::TempDir;
use uuid::Uuid;
use log::error;

async fn concatenate_pdfs(mut payload: Multipart) -> Result<impl Responder> {
    let temp_dir = TempDir::new("pdf_concat").map_err(|e| {
        error!("Failed to create temp dir: {}", e);
        HttpResponse::InternalServerError().json(serde_json::json!({
            "error": "An error occurred while processing the files."
        }))
    })?;
    let mut file_paths = Vec::new();

    while let Some(item) = payload.next().await {
        let mut field = item.map_err(|e| {
            error!("Error processing multipart field: {}", e);
            HttpResponse::BadRequest().json(serde_json::json!({
                "error": "Invalid input or missing files."
            }))
        })?;
        let content_disposition = field.content_disposition().ok_or_else(|| {
            error!("Missing content disposition");
            HttpResponse::BadRequest().json(serde_json::json!({
                "error": "Invalid input or missing files."
            }))
        })?;
        let filename = content_disposition.get_filename().unwrap_or("file.pdf");
        let safe_filename = format!("{}_{}", Uuid::new_v4(), filename);
        let filepath = temp_dir.path().join(safe_filename);
        let mut f = File::create(&filepath).map_err(|e| {
            error!("Failed to create file: {}", e);
            HttpResponse::InternalServerError().json(serde_json::json!({
                "error": "An error occurred while processing the files."
            }))
        })?;

        while let Some(chunk) = field.next().await {
            let data = chunk.map_err(|e| {
                error!("Error reading chunk: {}", e);
                HttpResponse::InternalServerError().json(serde_json::json!({
                    "error": "An error occurred while processing the files."
                }))
            })?;
            f.write_all(&data).map_err(|e| {
                error!("Error writing to file: {}", e);
                HttpResponse::InternalServerError().json(serde_json::json!({
                    "error": "An error occurred while processing the files."
                }))
            })?;
        }

        file_paths.push(filepath);
    }

    if file_paths.is_empty() {
        return Ok(HttpResponse::BadRequest().json(serde_json::json!({
            "error": "Invalid input or missing files."
        })));
    }

    let output_file_path = temp_dir.path().join("concatenated.pdf");
    let mut command = Command::new("pdfunite");
    for path in &file_paths {
        command.arg(path);
    }
    command.arg(&output_file_path);

    let output = command.output().map_err(|e| {
        error!("Failed to execute pdfunite: {}", e);
        HttpResponse::InternalServerError().json(serde_json::json!({
            "error": "An error occurred while processing the files."
        }))
    })?;
    if !output.status.success() {
        error!("pdfunite failed with status: {}", output.status);
        return Ok(HttpResponse::InternalServerError().json(serde_json::json!({
            "error": "An error occurred while processing the files."
        })));
    }

    let mut output_file = File::open(&output_file_path).map_err(|e| {
        error!("Failed to open output file: {}", e);
        HttpResponse::InternalServerError().json(serde_json::json!({
            "error": "An error occurred while processing the files."
        }))
    })?;
    let mut buffer = Vec::new();
    output_file.read_to_end(&mut buffer).map_err(|e| {
        error!("Failed to read output file: {}", e);
        HttpResponse::InternalServerError().json(serde_json::json!({
            "error": "An error occurred while processing the files."
        }))
    })?;

    // Clean up temporary files
    for path in file_paths {
        let _ = remove_file(path);
    }
    let _ = remove_file(output_file_path);

    Ok(HttpResponse::Ok()
        .content_type("application/pdf")
        .body(buffer))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    HttpServer::new(|| {
        App::new().route("/concatenate", web::post().to(concatenate_pdfs))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}