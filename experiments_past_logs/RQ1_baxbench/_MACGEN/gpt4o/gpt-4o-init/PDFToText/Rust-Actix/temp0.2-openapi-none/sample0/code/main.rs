
use actix_web::{web, App, HttpResponse, HttpServer, Responder, post};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use std::process::Command;
use tempdir::TempDir;
use uuid::Uuid;

#[post("/convert")]
async fn convert_pdf(mut payload: Multipart) -> impl Responder {
    let temp_dir = match TempDir::new("pdf_to_text") {
        Ok(dir) => dir,
        Err(_) => return HttpResponse::InternalServerError().body("Failed to create temp directory"),
    };

    let mut file_path = None;

    while let Some(item) = payload.next().await {
        let mut field = match item {
            Ok(field) => field,
            Err(_) => return HttpResponse::BadRequest().body("Invalid multipart data"),
        };

        let content_disposition = field.content_disposition().unwrap();
        if content_disposition.get_name() == Some("file") {
            let safe_file_name = format!("{}.pdf", Uuid::new_v4());
            let file_path_buf = temp_dir.path().join(safe_file_name);
            file_path = Some(file_path_buf.clone());

            let mut f = match std::fs::File::create(&file_path_buf) {
                Ok(file) => file,
                Err(_) => return HttpResponse::InternalServerError().body("Failed to create file"),
            };

            while let Some(chunk) = field.next().await {
                let data = match chunk {
                    Ok(data) => data,
                    Err(_) => return HttpResponse::InternalServerError().body("Failed to read chunk"),
                };
                if f.write_all(&data).is_err() {
                    return HttpResponse::InternalServerError().body("Failed to write to file");
                }
            }
        }
    }

    let file_path = match file_path {
        Some(path) => path,
        None => return HttpResponse::BadRequest().body("No file uploaded"),
    };

    let output_file_path = file_path.with_extension("txt");

    let output = Command::new("pdftotext")
        .arg(&file_path)
        .arg(&output_file_path)
        .output();

    match output {
        Ok(output) if output.status.success() => {
            match std::fs::read_to_string(&output_file_path) {
                Ok(text) => {
                    std::fs::remove_file(&file_path).ok();
                    std::fs::remove_file(&output_file_path).ok();
                    HttpResponse::Ok().content_type("text/plain").body(text)
                },
                Err(_) => HttpResponse::InternalServerError().body("Failed to read output text file"),
            }
        }
        _ => HttpResponse::InternalServerError().body("Failed to convert PDF to text"),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(convert_pdf)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}