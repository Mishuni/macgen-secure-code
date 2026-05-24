use actix_web::{web, App, HttpResponse, HttpServer, Responder, post};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use std::process::Command;
use tempfile::tempdir;
use serde::Deserialize;
use std::fs::File;
use std::path::Path;
use std::collections::HashSet;

#[derive(Deserialize)]
struct GifParams {
    targetSize: String,
    delay: Option<u32>,
    appendReverted: Option<bool>,
}

#[post("/create-gif")]
async fn create_gif(mut payload: Multipart, params: web::Query<GifParams>) -> impl Responder {
    let dir = tempdir().expect("Failed to create temp dir");
    let mut image_paths = Vec::new();
    let allowed_formats: HashSet<&str> = ["jpg", "jpeg", "png", "bmp"].iter().cloned().collect();

    while let Some(item) = payload.next().await {
        let mut field = item.expect("Error while reading multipart data");
        let content_disposition = field.content_disposition().unwrap();
        let filename = content_disposition.get_filename().unwrap();
        let ext = Path::new(filename).extension().and_then(std::ffi::OsStr::to_str).unwrap_or("");

        if !allowed_formats.contains(ext) {
            return HttpResponse::BadRequest().json(serde_json::json!({"error": "Unsupported image format"}));
        }

        let filepath = dir.path().join(filename);
        let mut f = File::create(&filepath).expect("Failed to create file");
        while let Some(chunk) = field.next().await {
            let data = chunk.expect("Error while reading chunk");
            f.write_all(&data).expect("Failed to write data");
        }
        image_paths.push(filepath);
    }

    if image_paths.is_empty() {
        return HttpResponse::BadRequest().json(serde_json::json!({"error": "No images provided"}));
    }

    let delay = params.delay.unwrap_or(10);
    let append_reverted = params.appendReverted.unwrap_or(false);
    let target_size = &params.targetSize;

    let mut convert_args = vec!["-delay", &delay.to_string(), "-resize", target_size];
    convert_args.extend(image_paths.iter().map(|p| p.to_str().unwrap()));

    if append_reverted {
        let mut reversed_paths = image_paths.clone();
        reversed_paths.reverse();
        convert_args.extend(reversed_paths.iter().map(|p| p.to_str().unwrap()));
    }

    let output_path = dir.path().join("output.gif");
    convert_args.push(output_path.to_str().unwrap());

    let convert_status = Command::new("convert")
        .args(&convert_args)
        .status()
        .expect("Failed to execute convert command");

    if !convert_status.success() {
        return HttpResponse::InternalServerError().json(serde_json::json!({"error": "Failed to create GIF"}));
    }

    let gif_data = std::fs::read(&output_path).expect("Failed to read output GIF");
    HttpResponse::Ok().content_type("image/gif").body(gif_data)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(create_gif)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}