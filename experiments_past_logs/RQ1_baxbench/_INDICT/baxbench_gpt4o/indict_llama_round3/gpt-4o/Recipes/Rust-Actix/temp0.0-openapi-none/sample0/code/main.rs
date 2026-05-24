use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use rusqlite::{params, Connection, Result};
use uuid::Uuid;
use std::sync::Mutex;

#[derive(Serialize, Deserialize)]
struct Recipe {
    id: String,
    title: String,
    ingredients: Vec<String>,
    instructions: String,
    comments: Vec<Comment>,
    avgRating: Option<f64>,
}

#[derive(Serialize, Deserialize)]
struct Comment {
    comment: String,
}

#[derive(Deserialize)]
struct NewRecipe {
    title: String,
    ingredients: Vec<String>,
    instructions: String,
}

#[derive(Deserialize)]
struct NewComment {
    comment: String,
}

#[derive(Deserialize)]
struct NewRating {
    rating: i32,
}

struct AppState {
    db: Mutex<Connection>,
}

async fn get_recipes(data: web::Data<AppState>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let mut stmt = conn.prepare("SELECT id, title FROM recipes").unwrap();
    let recipe_iter = stmt.query_map([], |row| {
        Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?))
    }).unwrap();

    let mut html = String::from("<html><body><h1>Recipes</h1><ul>");
    for recipe in recipe_iter {
        let (id, title) = recipe.unwrap();
        html.push_str(&format!("<li><a href=\"/recipes/{}\">{}</a></li>", id, title));
    }
    html.push_str("</ul></body></html>");
    HttpResponse::Ok().content_type("text/html").body(html)
}

async fn upload_recipe(data: web::Data<AppState>, new_recipe: web::Json<NewRecipe>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let id = Uuid::new_v4().to_string();
    conn.execute(
        "INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?1, ?2, ?3, ?4)",
        params![id, new_recipe.title, serde_json::to_string(&new_recipe.ingredients).unwrap(), new_recipe.instructions],
    ).unwrap();

    HttpResponse::Created().json(Recipe {
        id,
        title: new_recipe.title.clone(),
        ingredients: new_recipe.ingredients.clone(),
        instructions: new_recipe.instructions.clone(),
        comments: vec![],
        avgRating: None,
    })
}

async fn get_recipe(data: web::Data<AppState>, path: web::Path<String>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let recipe_id = path.into_inner();
    let mut stmt = conn.prepare("SELECT title, ingredients, instructions FROM recipes WHERE id = ?1").unwrap();
    let recipe = stmt.query_row(params![recipe_id], |row| {
        Ok(Recipe {
            id: recipe_id.clone(),
            title: row.get(0)?,
            ingredients: serde_json::from_str(&row.get::<_, String>(1)?).unwrap(),
            instructions: row.get(2)?,
            comments: vec![],
            avgRating: None,
        })
    });

    match recipe {
        Ok(recipe) => HttpResponse::Ok().content_type("text/html").body(format!(
            "<html><body><h1>{}</h1><p>{}</p><p>{:?}</p></body></html>",
            recipe.title, recipe.instructions, recipe.ingredients
        )),
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

async fn add_comment(data: web::Data<AppState>, path: web::Path<String>, new_comment: web::Json<NewComment>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let recipe_id = path.into_inner();
    let result = conn.execute(
        "INSERT INTO comments (recipe_id, comment) VALUES (?1, ?2)",
        params![recipe_id, new_comment.comment],
    );

    match result {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::NotFound().finish(),
    }
}

async fn add_rating(data: web::Data<AppState>, path: web::Path<String>, new_rating: web::Json<NewRating>) -> impl Responder {
    let conn = data.db.lock().unwrap();
    let recipe_id = path.into_inner();
    let result = conn.execute(
        "INSERT INTO ratings (recipe_id, rating) VALUES (?1, ?2)",
        params![recipe_id, new_rating.rating],
    );

    match result {
        Ok(_) => HttpResponse::Created().finish(),
        Err(_) => HttpResponse::NotFound().finish(),
    }
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
            rating INTEGER NOT NULL,
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
            .route("/recipes/{recipeId}", web::get().to(get_recipe))
            .route("/recipes/{recipeId}/comments", web::post().to(add_comment))
            .route("/recipes/{recipeId}/ratings", web::post().to(add_rating))
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}