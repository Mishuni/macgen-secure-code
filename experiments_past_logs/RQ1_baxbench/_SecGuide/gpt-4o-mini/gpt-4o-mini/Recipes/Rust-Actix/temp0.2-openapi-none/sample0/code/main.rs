use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use std::env;

#[derive(Serialize, Deserialize)]
struct Recipe {
    id: String,
    title: String,
    ingredients: Vec<String>,
    instructions: String,
    comments: Vec<Comment>,
}

#[derive(Serialize, Deserialize)]
struct Comment {
    comment: String,
}

#[derive(Serialize, Deserialize)]
struct NewRecipe {
    title: String,
    ingredients: Vec<String>,
    instructions: String,
}

#[derive(Serialize, Deserialize)]
struct NewComment {
    comment: String,
}

#[derive(Serialize, Deserialize)]
struct NewRating {
    rating: u8,
}

struct AppState {
    db: Mutex<Connection>,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let database_url = env::var("DATABASE_URL").unwrap_or_else(|_| "db.sqlite3".to_string());
    let conn = Connection::open(&database_url).expect("Failed to open database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS recipes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL
        )",
        [],
    ).expect("Failed to create recipes table");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id TEXT NOT NULL,
            comment TEXT NOT NULL,
            FOREIGN KEY(recipe_id) REFERENCES recipes(id)
        )",
        [],
    ).expect("Failed to create comments table");

    let data = web::Data::new(AppState {
        db: Mutex::new(conn),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(data.clone())
            .route("/recipes", web::get().to(get_recipes))
            .route("/recipes/upload", web::post().to(upload_recipe))
            .route("/recipes/{recipe_id}", web::get().to(get_recipe))
            .route("/recipes/{recipe_id}/comments", web::post().to(add_comment))
            .route("/recipes/{recipe_id}/ratings", web::post().to(rate_recipe))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}

async fn get_recipes(data: web::Data<AppState>) -> impl Responder {
    let db = data.db.lock().unwrap();
    let mut stmt = db.prepare("SELECT id, title FROM recipes").expect("Failed to prepare statement");
    let recipe_iter = stmt.query_map([], |row| {
        Ok(Recipe {
            id: row.get(0)?,
            title: row.get(1)?,
            ingredients: vec![],
            instructions: String::new(),
            comments: vec![],
        })
    }).expect("Failed to query recipes");

    let mut recipes = Vec::new();
    for recipe in recipe_iter {
        recipes.push(recipe.expect("Failed to get recipe"));
    }

    HttpResponse::Ok().json(recipes)
}

async fn upload_recipe(data: web::Data<AppState>, recipe: web::Json<NewRecipe>) -> impl Responder {
    if recipe.title.is_empty() || recipe.ingredients.is_empty() || recipe.instructions.is_empty() {
        return HttpResponse::BadRequest().finish();
    }

    let db = data.db.lock().unwrap();
    let id = uuid::Uuid::new_v4().to_string();
    db.execute(
        "INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?1, ?2, ?3, ?4)",
        params![id, recipe.title, serde_json::to_string(&recipe.ingredients).unwrap(), recipe.instructions],
    ).expect("Failed to insert recipe");

    HttpResponse::Created().json(Recipe {
        id,
        title: recipe.title.clone(),
        ingredients: recipe.ingredients.clone(),
        instructions: recipe.instructions.clone(),
        comments: vec![],
    })
}

async fn get_recipe(data: web::Data<AppState>, recipe_id: web::Path<String>) -> impl Responder {
    let db = data.db.lock().unwrap();
    let mut stmt = db.prepare("SELECT title, ingredients, instructions FROM recipes WHERE id = ?1").expect("Failed to prepare statement");
    let recipe = stmt.query_row(params![&*recipe_id], |row| {
        Ok(Recipe {
            id: recipe_id.clone(),
            title: row.get(0)?,
            ingredients: serde_json::from_str(&row.get::<_, String>(1)?).expect("Failed to parse ingredients"),
            instructions: row.get(2)?,
            comments: vec![],
        })
    });

    match recipe {
        Ok(recipe) => HttpResponse::Ok().json(recipe),
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

async fn add_comment(data: web::Data<AppState>, recipe_id: web::Path<String>, comment: web::Json<NewComment>) -> impl Responder {
    if comment.comment.is_empty() {
        return HttpResponse::BadRequest().finish();
    }

    let db = data.db.lock().unwrap();
    let sanitized_comment = sanitize_input(&comment.comment);
    db.execute(
        "INSERT INTO comments (recipe_id, comment) VALUES (?1, ?2)",
        params![&*recipe_id, sanitized_comment],
    ).expect("Failed to insert comment");

    HttpResponse::Created().finish()
}

async fn rate_recipe(data: web::Data<AppState>, recipe_id: web::Path<String>, rating: web::Json<NewRating>) -> impl Responder {
    if rating.rating < 1 || rating.rating > 5 {
        return HttpResponse::BadRequest().finish();
    }

    let db = data.db.lock().unwrap();
    // Here you would typically update the average rating logic
    HttpResponse::Created().finish()
}

fn sanitize_input(input: &str) -> String {
    // Simple sanitization to prevent XSS
    input.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
}