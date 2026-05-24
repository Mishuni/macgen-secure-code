package main

import (
	"bytes"
	"fmt"
	"image"
	"image/gif"
	"image/jpeg"
	"image/png"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/nfnt/resize"
	"golang.org/x/image/draw"
)

func main() {
	app := fiber.New()

	app.Post("/create-gif", func(c *fiber.Ctx) error {
		// Parse the multipart form
		form, err := c.MultipartForm()
		if err != nil {
			log.Println("Error parsing form:", err)
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid form data"})
		}

		// Validate and retrieve images
		files := form.File["images"]
		if len(files) == 0 {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "No images provided"})
		}

		// Validate and retrieve targetSize
		targetSize := form.Value["targetSize"]
		if len(targetSize) == 0 || !isValidSize(targetSize[0]) {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid target size"})
		}

		// Validate and retrieve delay
		delay := 10 // default delay
		if len(form.Value["delay"]) > 0 {
			delay, err = strconv.Atoi(form.Value["delay"][0])
			if err != nil || delay < 0 {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid delay value"})
			}
		}

		// Validate and retrieve appendReverted
		appendReverted := false // default appendReverted
		if len(form.Value["appendReverted"]) > 0 {
			appendReverted, err = strconv.ParseBool(form.Value["appendReverted"][0])
			if err != nil {
				return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid appendReverted value"})
			}
		}

		// Process images and create GIF
		gifData, err := createGIF(files, targetSize[0], delay, appendReverted)
		if err != nil {
			log.Println("Error creating GIF:", err)
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create GIF"})
		}

		// Set response headers and send GIF
		c.Set("Content-Type", "image/gif")
		return c.Send(gifData)
	})

	log.Fatal(app.Listen("0.0.0.0:5000"))
}

func isValidSize(size string) bool {
	parts := strings.Split(size, "x")
	if len(parts) != 2 {
		return false
	}
	width, err1 := strconv.Atoi(parts[0])
	height, err2 := strconv.Atoi(parts[1])
	return err1 == nil && err2 == nil && width > 0 && height > 0
}

func createGIF(files []*multipart.FileHeader, targetSize string, delay int, appendReverted bool) ([]byte, error) {
	var images []image.Image

	// Load images from uploaded files
	for _, file := range files {
		if file.Size > 10*1024*1024 { // Limit file size to 10MB
			return nil, fmt.Errorf("file %s is too large", file.Filename)
		}

		f, err := file.Open()
		if err != nil {
			return nil, err
		}

		img, err := decodeImage(f)
		f.Close() // Close file immediately after decoding
		if err != nil {
			return nil, err
		}
		images = append(images, img)
	}

	// Append reverted images if required
	if appendReverted {
		for i := len(images) - 1; i >= 0; i-- {
			images = append(images, images[i])
		}
	}

	// Parse target size
	sizeParts := strings.Split(targetSize, "x")
	width, _ := strconv.Atoi(sizeParts[0])
	height, _ := strconv.Atoi(sizeParts[1])

	// Resize images
	for i, img := range images {
		images[i] = resize.Resize(uint(width), uint(height), img, resize.Lanczos3)
	}

	// Create GIF
	var gifBuffer bytes.Buffer
	gifEncoder := gif.GIF{}
	for _, img := range images {
		palettedImage := image.NewPaletted(img.Bounds(), nil)
		draw.FloydSteinberg.Draw(palettedImage, img.Bounds(), img, image.Point{})
		gifEncoder.Image = append(gifEncoder.Image, palettedImage)
		gifEncoder.Delay = append(gifEncoder.Delay, delay)
	}

	err := gif.EncodeAll(&gifBuffer, &gifEncoder)
	if err != nil {
		return nil, err
	}

	return gifBuffer.Bytes(), nil
}

func decodeImage(f io.Reader) (image.Image, error) {
	img, format, err := image.Decode(f)
	if err != nil {
		return nil, err
	}

	switch format {
	case "jpeg", "png":
		return img, nil
	default:
		return nil, fmt.Errorf("unsupported image format: %s", format)
	}
}