use actix_web::{web, App, HttpResponse, HttpServer, Responder, Result};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use uuid::Uuid;
use std::fs;
use std::path::PathBuf;
use serde::Serialize;
use mime_guess;

#[derive(Serialize)]
struct UploadResponse {
    id: String,
}

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

async fn upload_image(mut payload: Multipart) -> Result<HttpResponse> {
    let file_id = Uuid::new_v4().to_string();
    let mut file_path = PathBuf::from(format!("./uploads/{}", file_id));

    while let Some(item) = payload.next().await {
        let mut field = item?;
        let content_disposition = field.content_disposition().ok_or_else(|| {
            HttpResponse::BadRequest().json(ErrorResponse {
                error: "Missing content disposition".to_string(),
            })
        })?;
        
        let filename = content_disposition.get_filename().unwrap_or("default");
        let file_extension = PathBuf::from(filename).extension().unwrap_or_default().to_str().unwrap_or("");
        file_path.set_extension(file_extension);

        // Check if file already exists to prevent overwriting
        if file_path.exists() {
            return Ok(HttpResponse::BadRequest().json(ErrorResponse {
                error: "File already exists".to_string(),
            }));
        }

        let mut f = web::block(|| std::fs::File::create(&file_path)).await??;

        while let Some(chunk) = field.next().await {
            let data = chunk?;
            f = web::block(move || f.write_all(&data).map(|_| f)).await??;
        }
    }

    Ok(HttpResponse::Ok().json(UploadResponse { id: file_id }))
}

async fn get_image(image_id: web::Path<String>) -> Result<impl Responder> {
    let file_path = PathBuf::from(format!("./uploads/{}", image_id));
    if !file_path.exists() {
        return Ok(HttpResponse::NotFound().json(ErrorResponse {
            error: "Image not found".to_string(),
        }));
    }

    let mime_type = mime_guess::from_path(&file_path).first_or_octet_stream();
    let file = web::block(|| fs::read(file_path)).await?;

    Ok(HttpResponse::Ok()
        .content_type(mime_type.as_ref())
        .body(file))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    std::fs::create_dir_all("./uploads")?;
    HttpServer::new(|| {
        App::new()
            .route("/upload", web::post().to(upload_image))
            .route("/images/{imageId}", web::get().to(get_image))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}