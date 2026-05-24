use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use std::process::Command;
use tempdir::TempDir;
use serde::Deserialize;
use regex::Regex;

#[derive(Deserialize)]
struct GifParams {
    targetSize: String,
    delay: Option<u64>,
    appendReverted: Option<bool>,
}

async fn create_gif(mut payload: Multipart) -> impl Responder {
    let temp_dir = TempDir::new("gif_creator").unwrap();
    let mut image_paths = Vec::new();
    let mut params: Option<GifParams> = None;

    while let Some(item) = payload.next().await {
        let mut field = item.unwrap();
        let content_disposition = field.content_disposition().unwrap();
        let name = content_disposition.get_name().unwrap();

        if name == "images" {
            let file_path = temp_dir.path().join(format!("{}.png", uuid::Uuid::new_v4()));
            let mut f = std::fs::File::create(&file_path).unwrap();
            while let Some(chunk) = field.next().await {
                let data = chunk.unwrap();
                f.write_all(&data).unwrap();
            }
            image_paths.push(file_path);
        } else if name == "targetSize" || name == "delay" || name == "appendReverted" {
            let mut data = Vec::new();
            while let Some(chunk) = field.next().await {
                let chunk_data = chunk.unwrap();
                data.extend_from_slice(&chunk_data);
            }
            let value = String::from_utf8(data).unwrap();
            if params.is_none() {
                params = Some(GifParams {
                    targetSize: String::new(),
                    delay: None,
                    appendReverted: None,
                });
            }
            let params = params.as_mut().unwrap();
            match name {
                "targetSize" => params.targetSize = value,
                "delay" => params.delay = value.parse().ok(),
                "appendReverted" => params.appendReverted = value.parse().ok(),
                _ => {}
            }
        }
    }

    if image_paths.is_empty() || params.is_none() {
        return HttpResponse::BadRequest().json(serde_json::json!({"error": "Invalid input"}));
    }

    let params = params.unwrap();
    let delay = params.delay.unwrap_or(10);
    let append_reverted = params.appendReverted.unwrap_or(false);

    let target_size_regex = Regex::new(r"^\d+x\d+$").unwrap();
    if !target_size_regex.is_match(&params.targetSize) {
        return HttpResponse::BadRequest().json(serde_json::json!({"error": "Invalid target size format"}));
    }

    let mut convert_args = vec!["-delay", &delay.to_string()];
    for path in &image_paths {
        convert_args.push(path.to_str().unwrap());
    }

    if append_reverted {
        for path in image_paths.iter().rev() {
            convert_args.push(path.to_str().unwrap());
        }
    }

    convert_args.push("-resize");
    convert_args.push(&params.targetSize);
    convert_args.push("gif:-");

    let output = Command::new("convert")
        .args(&convert_args)
        .output();

    match output {
        Ok(output) => {
            if output.status.success() {
                HttpResponse::Ok()
                    .content_type("image/gif")
                    .body(output.stdout)
            } else {
                HttpResponse::InternalServerError().json(serde_json::json!({"error": "Failed to create GIF"}))
            }
        }
        Err(_) => HttpResponse::InternalServerError().json(serde_json::json!({"error": "Failed to execute ImageMagick"})),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    HttpServer::new(|| {
        App::new()
            .route("/create-gif", web::post().to(create_gif))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}