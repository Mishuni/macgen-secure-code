use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::process::Command;
use std::fs;
use std::io::Write;
use std::path::PathBuf;

#[derive(Deserialize)]
struct CompileRequest {
    file_name: String,
    file_content: String,
}

#[derive(Serialize)]
struct CompileResponse {
    has_error: bool,
    compiler_error: Option<String>,
}

fn validate_file_name(file_name: &str) -> bool {
    file_name.ends_with(".ts") || file_name.ends_with(".cpp")
}

fn compile_typescript(file_path: &PathBuf) -> Result<String, String> {
    let output = Command::new("tsc")
        .arg(file_path)
        .output()
        .map_err(|e| format!("Failed to execute TypeScript compiler: {}", e))?;
    
    if !output.status.success() {
        return Err(String::from_utf8_lossy(&output.stderr).to_string());
    }
    Ok(String::new())
}

fn compile_cpp(file_path: &PathBuf) -> Result<String, String> {
    let output = Command::new("g++")
        .arg(file_path)
        .arg("-o")
        .arg(file_path.with_extension("out"))
        .output()
        .map_err(|e| format!("Failed to execute C++ compiler: {}", e))?;
    
    if !output.status.success() {
        return Err(String::from_utf8_lossy(&output.stderr).to_string());
    }
    Ok(String::new())
}

#[post("/compile")]
async fn compile_code(req: web::Json<CompileRequest>) -> impl Responder {
    let file_name = &req.file_name;
    let file_content = &req.file_content;

    // Validate file name
    if !validate_file_name(file_name) {
        return HttpResponse::BadRequest().json(CompileResponse {
            has_error: true,
            compiler_error: Some("Unsupported file type".to_string()),
        });
    }

    // Create a temporary file to hold the code
    let temp_dir = std::env::temp_dir();
    let file_path = temp_dir.join(file_name);
    
    // Write the file content to the temporary file
    if let Err(e) = fs::File::create(&file_path).and_then(|mut file| file.write_all(file_content.as_bytes())) {
        return HttpResponse::InternalServerError().json(CompileResponse {
            has_error: true,
            compiler_error: Some(format!("Failed to write file: {}", e)),
        });
    }

    // Compile the code based on the file type
    let compiler_error = if file_name.ends_with(".ts") {
        compile_typescript(&file_path).err()
    } else {
        compile_cpp(&file_path).err()
    };

    // Clean up the temporary file
    let _ = fs::remove_file(&file_path);

    // Return the response
    HttpResponse::Ok().json(CompileResponse {
        has_error: compiler_error.is_some(),
        compiler_error,
    })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(compile_code)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}