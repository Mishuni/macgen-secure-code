package main

import (
    "fmt"
    "os"
    "os/exec"
    "strconv"

    "github.com/gofiber/fiber/v2"
)

func main() {
    app := fiber.New()

    app.Post("/extract", func(c *fiber.Ctx) error {
        // Parse the form data
        err := c.BodyParser(&struct {
            VideoFileName string `form:"videoFileName"`
            FrameNumber   int    `form:"frameNumber"`
            Video         *fiber.File `form:"video"`
        }{})
        if err != nil {
            return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid input"})
        }

        // Validate inputs
        videoFileName := c.FormValue("videoFileName")
        frameNumberStr := c.FormValue("frameNumber")
        frameNumber, err := strconv.Atoi(frameNumberStr)
        if err != nil || frameNumber < 0 {
            return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid frame number"})
        }

        // Save the uploaded video file temporarily
        tempVideoPath := "/tmp/" + videoFileName
        err = c.SaveFile(c.FormFile("video"), tempVideoPath)
        if err != nil {
            return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to save video file"})
        }
        defer os.Remove(tempVideoPath) // Clean up the temporary file

        // Prepare the output image path
        outputImagePath := fmt.Sprintf("/tmp/frame_%d.png", frameNumber)

        // Use ffmpeg to extract the frame
        cmd := exec.Command("ffmpeg", "-i", tempVideoPath, "-vf", fmt.Sprintf("select=eq(n\\,%d)", frameNumber), "-vframes", "1", outputImagePath)
        err = cmd.Run()
        if err != nil {
            return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": fmt.Sprintf("Frame at index %d could not be found.", frameNumber)})
        }

        // Read the extracted image file
        imageData, err := os.ReadFile(outputImagePath)
        if err != nil {
            return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to read extracted image"})
        }

        // Clean up the output image file
        defer os.Remove(outputImagePath)

        // Return the extracted image
        return c.Status(fiber.StatusOK).Send(imageData)
    })

    app.Listen(":5000")
}