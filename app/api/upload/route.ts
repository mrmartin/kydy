import { writeFile, mkdir } from "fs/promises"
import { existsSync } from "fs"
import path from "path"
import { type NextRequest, NextResponse } from "next/server"
import { createClient } from "@/lib/supabase/server"
import { validateImageFile, getSafeFilename } from "@/lib/file-validation"

// Get uploads directory from environment
const UPLOADS_DIR = process.env.UPLOADS_DIR || "/tmp/kydy_uploads"

// Ensure uploads directory exists
async function ensureUploadsDir() {
  if (!existsSync(UPLOADS_DIR)) {
    await mkdir(UPLOADS_DIR, { recursive: true })
  }
}

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
    const uploadType = (formData.get("type") as string) || "poster" // 'poster' or 'avatar'

    if (!file) {
      return NextResponse.json({ 
        error: "No file provided",
        message: "Nebyl vybrán žádný soubor" 
      }, { status: 400 })
    }

    // Convert file to buffer for comprehensive validation
    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)

    // Comprehensive file validation including magic number checking
    const validationResult = await validateImageFile(
      file, 
      buffer, 
      uploadType as 'poster' | 'avatar'
    );

    if (!validationResult.isValid) {
      return NextResponse.json({ 
        error: validationResult.errorCode || "VALIDATION_FAILED",
        message: validationResult.error || "Soubor nesplňuje požadavky pro nahrání"
      }, { status: 400 })
    }

    // Ensure uploads directory exists
    await ensureUploadsDir()

    // Generate safe filename
    const filename = getSafeFilename(file.name, user.id, uploadType as 'poster' | 'avatar')
    const filePath = path.join(UPLOADS_DIR, filename)
    
    // Save file to local storage (buffer already created for validation)
    await writeFile(filePath, buffer)
    
    // Create URL that points to our static file serving route
    const url = `/uploads/${filename}`

    return NextResponse.json({
      url: url,
      filename: filename,
      size: file.size,
      type: file.type,
      message: "Soubor byl úspěšně nahrán"
    })
  } catch (error) {
    console.error("Upload error:", error)
    return NextResponse.json({ 
      error: "UPLOAD_FAILED",
      message: "Nahrání souboru selhalo. Zkuste to prosím znovu." 
    }, { status: 500 })
  }
}
