package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/mattn/go-sqlite3"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

type Entry struct {
	ID             string `json:"id"`
	Title          string `json:"title"`
	Content        string `json:"content"`
	LastModifiedBy string `json:"lastModifiedBy"`
	LastModifiedAt string `json:"lastModifiedAt"`
}

type NewEntry struct {
	Title     string `json:"title"`
	Content   string `json:"content"`
	CreatedBy string `json:"createdBy"`
}

type UpdateEntry struct {
	Content   string `json:"content"`
	ModifiedBy string `json:"modifiedBy"`
	Summary   string `json:"summary"`
}

var db *gorm.DB

func init() {
	var err error
	db, err = gorm.Open(sqlite.Open("db.sqlite3"), &gorm.Config{})
	if err != nil {
		log.Fatalf("failed to connect to database: %v", err)
	}

	db.AutoMigrate(&Entry{})
}

func main() {
	app := fiber.New()

	app.Get("/entries", getEntries)
	app.Post("/entries", createEntry)
	app.Get("/entries/:entryId", getEntry)
	app.Put("/entries/:entryId", updateEntry)

	log.Fatal(app.Listen(":5000"))
}

func getEntries(c *fiber.Ctx) error {
	var entries []Entry
	if err := db.Find(&entries).Error; err != nil {
		return c.Status(http.StatusInternalServerError).SendString("Error retrieving entries")
	}
	return c.JSON(entries)
}

func createEntry(c *fiber.Ctx) error {
	var newEntry NewEntry
	if err := c.BodyParser(&newEntry); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	entry := Entry{
		ID:             uuid.NewString(),
		Title:          newEntry.Title,
		Content:        newEntry.Content,
		LastModifiedBy: newEntry.CreatedBy,
		LastModifiedAt: fmt.Sprintf("%s", time.Now().Format(time.RFC3339)),
	}

	if err := db.Create(&entry).Error; err != nil {
		return c.Status(http.StatusInternalServerError).SendString("Error creating entry")
	}
	return c.Status(http.StatusCreated).JSON(entry)
}

func getEntry(c *fiber.Ctx) error {
	entryId := c.Params("entryId")
	var entry Entry
	if err := db.First(&entry, "id = ?", entryId).Error; err != nil {
		return c.Status(http.StatusNotFound).SendString("Entry not found")
	}
	return c.JSON(entry)
}

func updateEntry(c *fiber.Ctx) error {
	entryId := c.Params("entryId")
	var updateEntry UpdateEntry
	if err := c.BodyParser(&updateEntry); err != nil {
		return c.Status(http.StatusBadRequest).SendString("Invalid input")
	}

	var entry Entry
	if err := db.First(&entry, "id = ?", entryId).Error; err != nil {
		return c.Status(http.StatusNotFound).SendString("Entry not found")
	}

	entry.Content = updateEntry.Content
	entry.LastModifiedBy = updateEntry.ModifiedBy
	entry.LastModifiedAt = fmt.Sprintf("%s", time.Now().Format(time.RFC3339))

	if err := db.Save(&entry).Error; err != nil {
		return c.Status(http.StatusInternalServerError).SendString("Error updating entry")
	}
	return c.JSON(entry)
}