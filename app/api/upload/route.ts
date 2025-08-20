import { put } from "@vercel/blob"
import { type NextRequest, NextResponse } from "next/server"
import { createClient } from "@/lib/supabase/server"

// Check if Vercel Blob is configured
const isBlobConfigured = typeof process.env.BLOB_READ_WRITE_TOKEN === "string" && 
  process.env.BLOB_READ_WRITE_TOKEN.length > 0 && 
  process.env.BLOB_READ_WRITE_TOKEN !== "your-vercel-blob-token-here"

export async function POST(request: NextRequest) {
  try {
    // Check authentication
    const supabase = await createClient()
    const {
      data: { user },
    } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const formData = await request.formData()
    const file = formData.get("file") as File

    if (!file) {
      return NextResponse.json({ error: "No file provided" }, { status: 400 })
    }

    // Validate file type
    if (!file.type.startsWith("image/")) {
      return NextResponse.json({ error: "File must be an image" }, { status: 400 })
    }

    // Validate file size (10MB limit)
    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      return NextResponse.json({ error: "File size must be less than 10MB" }, { status: 400 })
    }

    // Generate unique filename
    const timestamp = Date.now()
    const extension = file.name.split(".").pop()
    const filename = `poster-${timestamp}-${user.id}.${extension}`

    let url: string

    if (isBlobConfigured) {
      // Upload to Vercel Blob
      const blob = await put(filename, file, {
        access: "public",
      })
      url = blob.url
    } else {
      // Fallback: Return a placeholder URL for development
      console.warn("Vercel Blob not configured. Using placeholder image URL.")
      url = "/placeholder.jpg" // This should point to a placeholder image in your public folder
    }

    return NextResponse.json({
      url: url,
      filename: filename,
      size: file.size,
      type: file.type,
    })
  } catch (error) {
    console.error("Upload error:", error)
    return NextResponse.json({ error: "Upload failed" }, { status: 500 })
  }
}
