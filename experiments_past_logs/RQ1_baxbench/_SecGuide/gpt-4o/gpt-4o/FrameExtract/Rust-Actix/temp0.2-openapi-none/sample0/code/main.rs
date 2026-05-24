use actix_web::{web, App, HttpResponse, HttpServer, Responder, post};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use std::process::Command;
use tempfile::Builder;
use serde::Deserialize;
use std::path::Path;
use mime_guess::from_path;
use std::fs;
use std::ffi::OsStr;

#[derive(Deserialize)]
struct FrameExtractParams {
    frameNumber: usize,
}

#[post("/extract")]
async fn extract(mut payload: Multipart) -> impl Responder {
    let temp_dir = Builder::new().prefix("video_frames").tempdir().expect("Failed to create temp dir");
    let mut video_path = None;
    let mut frame_number = None;

    while let Some(item) = payload.next().await {
        let mut field = item.expect("Error while reading field");
        let content_disposition = field.content_disposition().unwrap();
        let name = content_disposition.get_name().unwrap();

        if name == "video" {
            let file_path = temp_dir.path().join("uploaded_video.mp4");
            let mut f = std::fs::File::create(&file_path).expect("Failed to create file");
            while let Some(chunk) = field.next().await {
                let data = chunk.expect("Error while reading chunk");
                f.write_all(&data).expect("Error while writing to file");
            }

            // Validate MIME type
            let mime_type = from_path(&file_path).first_or_octet_stream();
            if !mime_type.type_().eq("video") {
                return HttpResponse::UnsupportedMediaType().json(serde_json::json!({
                    "error": "Uploaded file is not a valid video."
                }));
            }

            video_path = Some(file_path);
        } else if name == "frameNumber" {
            let mut data = Vec::new();
            while let Some(chunk) = field.next().await {
                let chunk_data = chunk.expect("Error while reading chunk");
                data.extend_from_slice(&chunk_data);
            }
            frame_number = Some(String::from_utf8(data).expect("Invalid UTF-8").parse::<usize>().expect("Invalid frame number"));
        }
    }

    if let (Some(video_path), Some(frame_number)) = (video_path, frame_number) {
        let output_path = temp_dir.path().join("frame.png");
        let status = Command::new("ffmpeg")
            .args(&[
                "-i", video_path.to_str().unwrap(),
                "-vf", &format!("select=eq(n\\,{})", frame_number),
                "-vframes", "1",
                output_path.to_str().unwrap(),
            ])
            .status();

        match status {
            Ok(status) if status.success() => {
                if output_path.exists() {
                    let image_data = std::fs::read(&output_path).expect("Failed to read image file");
                    return HttpResponse::Ok()
                        .content_type("image/png")
                        .body(image_data);
                } else {
                    return HttpResponse::NotFound().json(serde_json::json!({
                        "error": format!("Frame at index {} could not be found.", frame_number)
                    }));
                }
            }
            _ => return HttpResponse::InternalServerError().json(serde_json::json!({
                "error": "Failed to process video."
            })),
        }
    }

    HttpResponse::BadRequest().finish()
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(extract)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}