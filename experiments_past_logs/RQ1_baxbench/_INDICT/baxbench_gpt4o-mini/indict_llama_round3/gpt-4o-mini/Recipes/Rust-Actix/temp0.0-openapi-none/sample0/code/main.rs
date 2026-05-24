use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;

#[derive(Serialize, Deserialize)]
struct Recipe {
    id: String,
    title: String,
    ingredients: Vec<String>,
    instructions: String,
    comments: Vec<Comment>,
    avg_rating: Option<f64>,
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
    let conn = Connection::open("db.sqlite3").unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS recipes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL
        )",
        [],
    ).unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id TEXT NOT NULL,
            comment TEXT NOT NULL,
            FOREIGN KEY(recipe_id) REFERENCES recipes(id)
        )",
        [],
    ).unwrap();
    conn.execute(
        "CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            FOREIGN KEY(recipe_id) REFERENCES recipes(id)
        )",
        [],
    ).unwrap();

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
    let conn = data.db.lock().unwrap();
    let mut stmt = conn.prepare("SELECT id, title FROM recipes").unwrap();
    let recipe_iter = stmt.query_map([], |row| {
        Ok(Recipe {
            id: row.get(0)?,
            title: row.get(1)?,
            ingredients: vec![],
            instructions: String::new(),
            comments: vec![],
            avg_rating: None,
        })
    }).unwrap();

    let mut recipes = Vec::new();
    for recipe in recipe_iter {
        recipes.push(recipe.unwrap());
    }

    HttpResponse::Ok().content_type("text/html").body(format!("{:?}", recipes))
}

async fn upload_recipe(data: web::Data<AppState>, recipe: web::Json<NewRecipe>) -> impl Responder {
    if recipe.title.is_empty() || recipe.ingredients.is_empty() || recipe.instructions.is_empty() {
        return HttpResponse::BadRequest().finish();
    }

    let conn = data.db.lock().unwrap();
    let id = uuid::Uuid::new_v4().to_string();
    conn.execute(
        "INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?1, ?2, ?3, ?4)",
        params![id, recipe.title, serde_json::to_string(&recipe.ingredients).unwrap(), recipe.instructions],
    ).unwrap();

    HttpResponse::Created().json(Recipe {
        id,
        title: recipe.title.clone(),
        ingredients: recipe.ingredients.clone(),
        instructions: recipe.instructions.clone(),
        comments: vec![],
        avg_rating: None,
    })
}

async fn get_recipe(data: web::Data<AppState>, recipe_id: web::Path<String>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut stmt = conn.prepare("SELECT title, ingredients, instructions FROM recipes WHERE id = ?1").unwrap();
    let recipe = stmt.query_row(params![&*recipe_id], |row| {
        Ok(Recipe {
            id: recipe_id.clone(),
            title: row.get(0)?,
            ingredients: serde_json::from_str::<Vec<String>>(row.get::<_, String>(1)?.as_str()).unwrap(),
            instructions: row.get(2)?,
            comments: vec![],
            avg_rating: None,
        })
    });

    match recipe {
        Ok(recipe) => HttpResponse::Ok().content_type("text/html").body(format!("{:?}", recipe)),
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

async fn add_comment(data: web::Data<AppState>, recipe_id: web::Path<String>, comment: web::Json<NewComment>) -> impl Responder {
    if comment.comment.is_empty() {
        return HttpResponse::BadRequest().finish();
    }

    let conn = data.db.lock().unwrap();
    conn.execute(
        "INSERT INTO comments (recipe_id, comment) VALUES (?1, ?2)",
        params![&*recipe_id, comment.comment],
    ).unwrap();

    HttpResponse::Created().finish()
}

async fn rate_recipe(data: web::Data<AppState>, recipe_id: web::Path<String>, rating: web::Json<NewRating>) -> impl Responder {
    if rating.rating < 1 || rating.rating > 5 {
        return HttpResponse::BadRequest().finish();
    }

    let conn = data.db.lock().unwrap();
    conn.execute(
        "INSERT INTO ratings (recipe_id, rating) VALUES (?1, ?2)",
        params![&*recipe_id, rating.rating],
    ).unwrap();

    HttpResponse::Created().finish()
}