use actix_web::{web, App, HttpResponse, HttpServer, Responder, post, Error};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use tempdir::TempDir;
use std::process::Command;
use serde::Deserialize;
use std::path::PathBuf;
use regex::Regex;

#[derive(Deserialize)]
struct GifParams {
    targetSize: String,
    delay: Option<u64>,
    appendReverted: Option<bool>,
}

#[post("/create-gif")]
async fn create_gif(mut payload: Multipart, web::Query(params): web::Query<GifParams>) -> Result<impl Responder, Error> {
    let temp_dir = TempDir::new("gif_creator").map_err(|_| HttpResponse::InternalServerError().json(serde_json::json!({"error": "Failed to create temp directory"})))?;
    let mut image_paths = Vec::new();

    while let Some(item) = payload.next().await {
        let mut field = item.map_err(|_| HttpResponse::BadRequest().json(serde_json::json!({"error": "Failed to read multipart data"})))?;
        let content_disposition = field.content_disposition().ok_or_else(|| HttpResponse::BadRequest().json(serde_json::json!({"error": "Missing content disposition"})))?;
        let filename = content_disposition.get_filename().ok_or_else(|| HttpResponse::BadRequest().json(serde_json::json!({"error": "Missing filename"})))?;
        
        // Sanitize filename to prevent directory traversal
        let sanitized_filename = sanitize_filename::sanitize(&filename);
        let filepath = temp_dir.path().join(sanitized_filename);
        let mut f = std::fs::File::create(&filepath).map_err(|_| HttpResponse::InternalServerError().json(serde_json::json!({"error": "Failed to create file"})))?;

        while let Some(chunk) = field.next().await {
            let data = chunk.map_err(|_| HttpResponse::InternalServerError().json(serde_json::json!({"error": "Failed to read chunk"})))?;
            f.write_all(&data).map_err(|_| HttpResponse::InternalServerError().json(serde_json::json!({"error": "Failed to write to file"})))?;
        }
        image_paths.push(filepath);
    }

    if image_paths.is_empty() {
        return Ok(HttpResponse::BadRequest().json(serde_json::json!({"error": "No images uploaded"})));
    }

    // Validate targetSize format
    let size_regex = Regex::new(r"^\d+x\d+$").unwrap();
    if !size_regex.is_match(&params.targetSize) {
        return Ok(HttpResponse::BadRequest().json(serde_json::json!({"error": "Invalid targetSize format"})));
    }

    let delay = params.delay.unwrap_or(10);
    let append_reverted = params.appendReverted.unwrap_or(false);
    let target_size = &params.targetSize;

    let mut convert_args = vec!["-delay", &delay.to_string(), "-resize", target_size];

    for path in &image_paths {
        convert_args.push(path.to_str().unwrap());
    }

    if append_reverted {
        for path in image_paths.iter().rev() {
            convert_args.push(path.to_str().unwrap());
        }
    }

    let output_path = temp_dir.path().join("output.gif");
    convert_args.push(output_path.to_str().unwrap());

    let convert_status = Command::new("convert")
        .args(&convert_args)
        .status()
        .map_err(|_| HttpResponse::InternalServerError().json(serde_json::json!({"error": "Failed to execute convert command"})))?;

    if !convert_status.success() {
        return Ok(HttpResponse::InternalServerError().json(serde_json::json!({"error": "Failed to create GIF"})));
    }

    let gif_data = std::fs::read(&output_path).map_err(|_| HttpResponse::InternalServerError().json(serde_json::json!({"error": "Failed to read GIF file"})))?;
    Ok(HttpResponse::Ok().content_type("image/gif").body(gif_data))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    HttpServer::new(|| {
        App::new()
            .service(create_gif)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}