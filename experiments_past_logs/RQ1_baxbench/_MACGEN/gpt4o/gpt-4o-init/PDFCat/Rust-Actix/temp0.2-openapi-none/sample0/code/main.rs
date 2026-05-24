use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use std::process::Command;
use tempdir::TempDir;
use uuid::Uuid;

async fn concatenate_pdfs(mut payload: Multipart) -> impl Responder {
    let temp_dir = match TempDir::new("pdf_concat") {
        Ok(dir) => dir,
        Err(_) => return HttpResponse::InternalServerError().json({"error": "Failed to create temp directory"}),
    };

    let mut file_paths = Vec::new();

    while let Ok(Some(mut field)) = payload.try_next().await {
        let content_disposition = field.content_disposition().unwrap();
        let filename = content_disposition.get_filename().unwrap();
        let safe_filename = Uuid::new_v4().to_string() + ".pdf";
        let file_path = temp_dir.path().join(safe_filename);

        let mut f = match std::fs::File::create(&file_path) {
            Ok(file) => file,
            Err(_) => return HttpResponse::InternalServerError().json({"error": "Failed to create file"}),
        };

        while let Some(chunk) = field.next().await {
            let data = match chunk {
                Ok(data) => data,
                Err(_) => return HttpResponse::InternalServerError().json({"error": "Failed to read file chunk"}),
            };
            if let Err(_) = f.write_all(&data) {
                return HttpResponse::InternalServerError().json({"error": "Failed to write to file"});
            }
        }

        file_paths.push(file_path);
    }

    if file_paths.is_empty() {
        return HttpResponse::BadRequest().json({"error": "Invalid input or missing files"});
    }

    let output_file_path = temp_dir.path().join(format!("{}.pdf", Uuid::new_v4()));

    let mut command = Command::new("pdfunite");
    for path in &file_paths {
        command.arg(path);
    }
    command.arg(&output_file_path);

    if let Err(_) = command.output() {
        return HttpResponse::InternalServerError().json({"error": "An error occurred while processing the files"});
    }

    let output_file = match std::fs::read(&output_file_path) {
        Ok(data) => data,
        Err(_) => return HttpResponse::InternalServerError().json({"error": "Failed to read output file"}),
    };

    HttpResponse::Ok()
        .content_type("application/pdf")
        .body(output_file)
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