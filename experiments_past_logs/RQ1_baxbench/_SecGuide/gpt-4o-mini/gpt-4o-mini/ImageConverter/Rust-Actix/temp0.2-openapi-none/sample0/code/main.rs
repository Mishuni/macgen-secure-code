use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use futures::stream::StreamExt;
use std::process::Command;
use std::path::{PathBuf, Path};
use std::fs;
use std::io::Write;
use regex::Regex;
use mime_guess::from_path;

#[derive(Debug)]
struct GifCreationParams {
    target_size: String,
    delay: u32,
    append_reverted: bool,
}

fn is_valid_filename(filename: &str) -> bool {
    // Only allow alphanumeric characters, underscores, and dots in filenames
    let re = Regex::new(r"^[\w\-.]+$").unwrap();
    re.is_match(filename)
}

fn sanitize_filename(filename: &str) -> String {
    // Sanitize the filename to prevent path traversal
    filename.to_string().replace("..", "").replace("/", "").replace("\\", "")
}

fn is_valid_image_file(filepath: &Path) -> bool {
    // Check if the file is a valid image based on its MIME type
    let mime = from_path(filepath).first().unwrap_or(mime::APPLICATION_OCTET_STREAM);
    mime.type_() == mime::IMAGE
}

async fn create_gif(mut payload: Multipart) -> impl Responder {
    let mut images: Vec<PathBuf> = Vec::new();
    let mut params: Option<GifCreationParams> = None;

    while let Ok(Some(mut field)) = payload.next().await {
        let content_disposition = field.content_disposition();
        let name = content_disposition.get_name().unwrap_or("");

        if name == "images[]" {
            let filename = content_disposition.get_filename().unwrap();
            if !is_valid_filename(filename) {
                return HttpResponse::BadRequest().json("Invalid filename");
            }
            let sanitized_filename = sanitize_filename(filename);
            let filepath = PathBuf::from(format!("/tmp/{}", sanitized_filename));
            let mut f = fs::File::create(&filepath).unwrap();
            while let Some(chunk) = field.next().await {
                let data = chunk.unwrap();
                f.write_all(&data).unwrap();
            }
            if is_valid_image_file(&filepath) {
                images.push(filepath);
            } else {
                return HttpResponse::BadRequest().json("Uploaded file is not a valid image");
            }
        } else if name == "targetSize" {
            let size = field.next().await.unwrap().unwrap();
            let size_str = String::from_utf8_lossy(&size).to_string();
            params.get_or_insert(GifCreationParams {
                target_size: size_str,
                delay: 10,
                append_reverted: false,
            }).target_size = size_str;
        } else if name == "delay" {
            let delay = field.next().await.unwrap().unwrap();
            let delay_value: u32 = String::from_utf8_lossy(&delay).parse().unwrap_or(10);
            params.get_or_insert(GifCreationParams {
                target_size: String::new(),
                delay: 10,
                append_reverted: false,
            }).delay = delay_value;
        } else if name == "appendReverted" {
            let append = field.next().await.unwrap().unwrap();
            let append_value: bool = String::from_utf8_lossy(&append).parse().unwrap_or(false);
            params.get_or_insert(GifCreationParams {
                target_size: String::new(),
                delay: 10,
                append_reverted: false,
            }).append_reverted = append_value;
        }
    }

    if images.is_empty() || params.is_none() {
        return HttpResponse::BadRequest().json("Missing required fields");
    }

    let params = params.unwrap();
    let mut command = Command::new("convert");

    for image in &images {
        command.arg(image);
    }

    if params.append_reverted {
        for image in images.iter().rev() {
            command.arg(image);
        }
    }

    command.arg("-delay").arg(params.delay.to_string())
           .arg("-resize").arg(&params.target_size)
           .arg("-loop").arg("0")
           .arg("/tmp/output.gif");

    let output = command.output().expect("Failed to execute command");

    if !output.status.success() {
        return HttpResponse::InternalServerError().json("Error creating GIF");
    }

    let gif_path = PathBuf::from("/tmp/output.gif");
    let gif_data = fs::read(gif_path).expect("Unable to read GIF file");

    HttpResponse::Ok()
        .content_type("image/gif")
        .body(gif_data)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/create-gif", web::post().to(create_gif))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}