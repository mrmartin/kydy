import { NextRequest, NextResponse } from "next/server"
import { readFile } from "fs/promises"
import { existsSync } from "fs"
import path from "path"

const UPLOADS_DIR = process.env.UPLOADS_DIR || "/tmp/kydy_uploads"

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const filename = params.path.join("/")
    const filePath = path.join(UPLOADS_DIR, filename)
    
    // Security check: ensure the file is within uploads directory
    const resolvedPath = path.resolve(filePath)
    const resolvedUploadsDir = path.resolve(UPLOADS_DIR)
    
    if (!resolvedPath.startsWith(resolvedUploadsDir)) {
      return NextResponse.json({ error: "Access denied" }, { status: 403 })
    }
    
    // Check if file exists
    if (!existsSync(filePath)) {
      return NextResponse.json({ error: "File not found" }, { status: 404 })
    }
    
    // Read and serve the file
    const fileBuffer = await readFile(filePath)
    
    // Determine content type based on file extension
    const ext = path.extname(filename).toLowerCase()
    const contentType = {
      ".jpg": "image/jpeg",
      ".jpeg": "image/jpeg",
      ".png": "image/png",
      ".gif": "image/gif",
      ".webp": "image/webp"
    }[ext] || "application/octet-stream"
    
    return new NextResponse(fileBuffer, {
      headers: {
        "Content-Type": contentType,
        "Cache-Control": "public, max-age=31536000, immutable",
      },
    })
  } catch (error) {
    console.error("File serving error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
