use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use std::fs::{File, create_dir_all};
use std::io::Write;
use std::process::Command;
use std::path::{PathBuf, Path};
use serde::Serialize;
use uuid::Uuid;

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

async fn extract_frame(mut payload: Multipart) -> impl Responder {
    let mut video_file_name: Option<String> = None;
    let mut frame_number: Option<u32> = None;
    let mut video_path: Option<PathBuf> = None;

    while let Some(field) = payload.next().await.unwrap() {
        let field_name = field.name().to_string();
        let content_type = field.content_type().to_string();

        if field_name == "videoFileName" {
            video_file_name = Some(field.try_into_string().unwrap());
        } else if field_name == "frameNumber" {
            if let Ok(num) = field.try_into_string().unwrap().parse::<u32>() {
                frame_number = Some(num);
            } else {
                return HttpResponse::BadRequest().json(ErrorResponse { error: "Invalid frame number".to_string() });
            }
        } else if field_name == "video" {
            // Validate file type (for example, only allow mp4)
            if !content_type.contains("video/mp4") {
                return HttpResponse::BadRequest().json(ErrorResponse { error: "Only MP4 video files are allowed".to_string() });
            }

            // Generate a unique filename to prevent overwriting
            let unique_filename = format!("uploads/uploaded_video_{}.mp4", Uuid::new_v4());
            video_path = Some(PathBuf::from(&unique_filename));
            let mut f = File::create(&unique_filename).map_err(|_| HttpResponse::InternalServerError().json(ErrorResponse { error: "Failed to create file".to_string() }))?;
            while let Some(chunk) = field.try_next().await.unwrap() {
                f.write_all(&chunk).map_err(|_| HttpResponse::InternalServerError().json(ErrorResponse { error: "Failed to write to file".to_string() }))?;
            }
        }
    }

    if let (Some(video_file_name), Some(frame_number), Some(video_path)) = (video_file_name, frame_number, video_path) {
        let output_image = format!("uploads/frame_{}.png", frame_number);
        
        let status = Command::new("ffmpeg")
            .args(&["-i", video_path.to_str().unwrap(), "-vf", &format!("select=eq(n\\,{})", frame_number), "-vframes", "1", &output_image])
            .status()
            .expect("Failed to execute ffmpeg");

        if status.success() {
            let image_data = std::fs::read(&output_image).map_err(|_| HttpResponse::InternalServerError().json(ErrorResponse { error: "Failed to read output image".to_string() }))?;
            return HttpResponse::Ok()
                .content_type("image/png")
                .body(image_data);
        } else {
            let error_message = format!("Frame at index {} could not be found.", frame_number);
            return HttpResponse::NotFound()
                .json(ErrorResponse { error: error_message });
        }
    }

    HttpResponse::BadRequest().json(ErrorResponse { error: "Invalid input".to_string() })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Create a directory for uploads if it doesn't exist
    create_dir_all("uploads")?;
    
    HttpServer::new(|| {
        App::new()
            .route("/extract", web::post().to(extract_frame))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}