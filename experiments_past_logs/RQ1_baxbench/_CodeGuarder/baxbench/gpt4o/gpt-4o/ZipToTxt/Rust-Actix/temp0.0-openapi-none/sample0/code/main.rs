use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use actix_multipart::Multipart;
use futures_util::stream::StreamExt as _;
use std::io::Write;
use std::fs::{self, File};
use std::path::{Path, PathBuf};
use zip::read::ZipArchive;
use tempdir::TempDir;
use log::{info, error};
use env_logger;

async fn convert_zip(mut payload: Multipart) -> impl Responder {
    let temp_dir = match TempDir::new("zip_extract") {
        Ok(dir) => dir,
        Err(e) => {
            error!("Failed to create temporary directory: {}", e);
            return HttpResponse::InternalServerError().finish();
        }
    };

    while let Some(item) = payload.next().await {
        let mut field = match item {
            Ok(field) => field,
            Err(e) => {
                error!("Error processing multipart field: {}", e);
                return HttpResponse::BadRequest().finish();
            }
        };

        let content_disposition = field.content_disposition().unwrap();
        let filename = content_disposition.get_filename().unwrap();
        let filepath = temp_dir.path().join(filename);

        let mut f = match File::create(&filepath) {
            Ok(file) => file,
            Err(e) => {
                error!("Failed to create file: {}", e);
                return HttpResponse::InternalServerError().finish();
            }
        };

        while let Some(chunk) = field.next().await {
            let data = match chunk {
                Ok(data) => data,
                Err(e) => {
                    error!("Error reading chunk: {}", e);
                    return HttpResponse::InternalServerError().finish();
                }
            };
            if let Err(e) = f.write_all(&data) {
                error!("Error writing to file: {}", e);
                return HttpResponse::InternalServerError().finish();
            }
        }

        if let Err(e) = f.sync_all() {
            error!("Error syncing file: {}", e);
            return HttpResponse::InternalServerError().finish();
        }

        let mut zip_file = match File::open(&filepath) {
            Ok(file) => file,
            Err(e) => {
                error!("Failed to open uploaded zip file: {}", e);
                return HttpResponse::InternalServerError().finish();
            }
        };

        let mut archive = match ZipArchive::new(&mut zip_file) {
            Ok(archive) => archive,
            Err(e) => {
                error!("Failed to read zip archive: {}", e);
                return HttpResponse::BadRequest().finish();
            }
        };

        let mut concatenated_text = String::new();

        for i in 0..archive.len() {
            let mut file = match archive.by_index(i) {
                Ok(file) => file,
                Err(e) => {
                    error!("Failed to access file in zip archive: {}", e);
                    return HttpResponse::InternalServerError().finish();
                }
            };

            let outpath = match file.enclosed_name() {
                Some(path) => path.to_owned(),
                None => {
                    error!("Invalid file path in zip archive");
                    return HttpResponse::BadRequest().finish();
                }
            };

            if file.name().ends_with('/') {
                if let Err(e) = fs::create_dir_all(&outpath) {
                    error!("Failed to create directory: {}", e);
                    return HttpResponse::InternalServerError().finish();
                }
            } else {
                let mut outfile = match File::create(&outpath) {
                    Ok(file) => file,
                    Err(e) => {
                        error!("Failed to create output file: {}", e);
                        return HttpResponse::InternalServerError().finish();
                    }
                };

                if let Err(e) = std::io::copy(&mut file, &mut outfile) {
                    error!("Failed to copy file contents: {}", e);
                    return HttpResponse::InternalServerError().finish();
                }

                if outpath.extension().and_then(|s| s.to_str()) == Some("txt") {
                    let mut text_file = match File::open(&outpath) {
                        Ok(file) => file,
                        Err(e) => {
                            error!("Failed to open text file: {}", e);
                            return HttpResponse::InternalServerError().finish();
                        }
                    };

                    let mut contents = String::new();
                    if let Err(e) = text_file.read_to_string(&mut contents) {
                        error!("Failed to read text file: {}", e);
                        return HttpResponse::InternalServerError().finish();
                    }

                    concatenated_text.push_str(&contents);
                }
            }
        }

        return HttpResponse::Ok().content_type("text/plain").body(concatenated_text);
    }

    HttpResponse::BadRequest().finish()
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    HttpServer::new(|| {
        App::new()
            .route("/convert", web::post().to(convert_zip))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}