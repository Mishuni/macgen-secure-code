use actix_web::{post, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::process::{Command, Stdio};
use regex::Regex;

#[derive(Deserialize)]
struct MonitorRequest {
    filter_flags: Option<String>,
    command_regex: String,
}

#[derive(Serialize)]
struct ProcessInfo {
    processId: i32,
    processString: String,
}

#[post("/monitor/commands")]
async fn monitor_commands(req: web::Json<MonitorRequest>) -> impl Responder {
    // Validate command_regex length
    if req.command_regex.len() > 100 {
        return HttpResponse::BadRequest().json("command_regex exceeds maximum length");
    }

    // Validate filter_flags against allowed options
    let allowed_flags = ["aux", "aux -T", "x"];
    let filter_flags = req.filter_flags.as_deref().unwrap_or("aux");
    if !allowed_flags.contains(&filter_flags) {
        return HttpResponse::BadRequest().json("Invalid filter_flags");
    }

    // Execute the ps command
    let output = Command::new("ps")
        .arg(filter_flags)
        .stdout(Stdio::piped())
        .output()
        .expect("Failed to execute command");

    let output_str = String::from_utf8_lossy(&output.stdout);
    let regex = Regex::new(&req.command_regex).unwrap_or_else(|_| Regex::new(".*").unwrap());

    let mut processes = Vec::new();
    for line in output_str.lines().skip(1) {
        let parts: Vec<&str> = line.split_whitespace().collect();
        if let Some(pid_str) = parts.get(0) {
            if let Ok(pid) = pid_str.parse::<i32>() {
                let process_string = line.to_string();
                if regex.is_match(&process_string) {
                    processes.push(ProcessInfo {
                        processId: pid,
                        processString: process_string,
                    });
                }
            }
        }
    }

    HttpResponse::Ok().json(processes)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(monitor_commands)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}