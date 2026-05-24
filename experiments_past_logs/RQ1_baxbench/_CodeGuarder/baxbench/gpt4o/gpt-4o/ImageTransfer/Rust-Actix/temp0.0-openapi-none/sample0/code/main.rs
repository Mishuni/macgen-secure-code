use actix_web::{web, App, HttpServer, HttpResponse, Responder, Error};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use serde::{Serialize, Deserialize};
use std::io::Write;
use uuid::Uuid;
use tempdir::TempDir;
use std::fs::File;
use std::path::PathBuf;
use actix_web::http::header::ContentType;

#[derive(Serialize)]
struct UploadResponse {
    id: String,
}

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

async fn upload(mut payload: Multipart) -> Result<HttpResponse, Error> {
    let temp_dir = TempDir::new("uploads").expect("Failed to create temp dir");
    let mut file_path: Option<PathBuf> = None;

    while let Some(item) = payload.next().await {
        let mut field = item?;
        let content_disposition = field.content_disposition().unwrap();
        let filename = content_disposition.get_filename().unwrap();

        if filename.contains("..") {
            return Ok(HttpResponse::BadRequest().json(ErrorResponse {
                error: "Invalid file name".to_string(),
            }));
        }

        let file_id = Uuid::new_v4().to_string();
        let sanitized_filename = format!("{}_{}", file_id, filename);
        let filepath = temp_dir.path().join(sanitized_filename);
        file_path = Some(filepath.clone());

        let mut f = File::create(filepath)?;
        while let Some(chunk) = field.next().await {
            let data = chunk?;
            f.write_all(&data)?;
        }
    }

    if let Some(path) = file_path {
        Ok(HttpResponse::Ok().json(UploadResponse {
            id: path.file_name().unwrap().to_str().unwrap().to_string(),
        }))
    } else {
        Ok(HttpResponse::BadRequest().json(ErrorResponse {
            error: "No file uploaded".to_string(),
        }))
    }
}

async fn get_image(web::Path(image_id): web::Path<String>) -> impl Responder {
    let temp_dir = TempDir::new("uploads").expect("Failed to create temp dir");
    let filepath = temp_dir.path().join(&image_id);

    if filepath.exists() {
        let file = actix_files::NamedFile::open(filepath).unwrap();
        file.set_content_type(ContentType::jpeg()).into_response()
    } else {
        HttpResponse::NotFound().json(ErrorResponse {
            error: "Image not found".to_string(),
        })
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/upload", web::post().to(upload))
            .route("/images/{imageId}", web::get().to(get_image))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}