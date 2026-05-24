use actix_web::{web, App, HttpResponse, HttpServer, Responder, post};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use std::process::Command;
use tempdir::TempDir;
use serde::Serialize;

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

#[post("/extract")]
async fn extract(mut payload: Multipart) -> impl Responder {
    let temp_dir = TempDir::new("video_frames").expect("Failed to create temp dir");
    let mut video_path = None;
    let mut frame_number = None;

    while let Some(item) = payload.next().await {
        let mut field = item.expect("Failed to get field");
        let content_disposition = field.content_disposition().expect("Failed to get content disposition");
        let name = content_disposition.get_name().expect("Failed to get name");

        if name == "video" {
            let file_path = temp_dir.path().join("uploaded_video.mp4");
            let mut f = std::fs::File::create(&file_path).expect("Failed to create file");
            while let Some(chunk) = field.next().await {
                let data = chunk.expect("Failed to read chunk");
                f.write_all(&data).expect("Failed to write data");
            }
            video_path = Some(file_path);
        } else if name == "frameNumber" {
            let mut data = Vec::new();
            while let Some(chunk) = field.next().await {
                let bytes = chunk.expect("Failed to read chunk");
                data.extend_from_slice(&bytes);
            }
            frame_number = Some(String::from_utf8(data).expect("Failed to parse frame number").parse::<u32>().expect("Invalid frame number"));
        }
    }

    if let (Some(video_path), Some(frame_number)) = (video_path, frame_number) {
        let output_image_path = temp_dir.path().join("frame.png");
        let status = Command::new("ffmpeg")
            .args(&[
                "-i",
                video_path.to_str().expect("Failed to convert path to str"),
                "-vf",
                &format!("select=eq(n\\,{})", frame_number),
                "-vframes",
                "1",
                output_image_path.to_str().expect("Failed to convert path to str"),
            ])
            .status()
            .expect("Failed to execute ffmpeg");

        if status.success() {
            if output_image_path.exists() {
                let image_data = std::fs::read(output_image_path).expect("Failed to read image data");
                return HttpResponse::Ok()
                    .content_type("image/png")
                    .body(image_data);
            }
        }
    }

    HttpResponse::NotFound().json(ErrorResponse {
        error: format!("Frame at index {} could not be found.", frame_number.unwrap_or(0)),
    })
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