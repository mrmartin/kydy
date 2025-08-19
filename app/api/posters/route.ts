import { type NextRequest, NextResponse } from "next/server"
import { createClient } from "@/lib/supabase/server"

export async function POST(request: NextRequest) {
  try {
    // Check authentication
    const supabase = createClient()
    const {
      data: { user },
    } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await request.json()
    const { title, description, imageUrl, filename, partyId, location, datePhotographed } = body

    if (!title || !imageUrl) {
      return NextResponse.json({ error: "Missing required fields" }, { status: 400 })
    }

    // Insert poster into database
    const { data: poster, error } = await supabase
      .from("posters")
      .insert({
        title: title.trim(),
        description: description?.trim() || null,
        image_url: imageUrl,
        political_party_id: partyId || null,
        uploaded_by: user.id,
        location: location?.trim() || null,
        date_photographed: datePhotographed || null,
      })
      .select()
      .single()

    if (error) {
      console.error("Database error:", error)
      return NextResponse.json({ error: "Failed to save poster" }, { status: 500 })
    }

    return NextResponse.json({ poster })
  } catch (error) {
    console.error("API error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}

export async function GET() {
  try {
    const supabase = createClient()

    // Get all posters with related data
    const { data: posters, error } = await supabase
      .from("posters")
      .select(`
        *,
        political_parties (
          id,
          name,
          color
        ),
        profiles (
          id,
          full_name
        )
      `)
      .order("created_at", { ascending: false })

    if (error) {
      console.error("Database error:", error)
      return NextResponse.json({ error: "Failed to fetch posters" }, { status: 500 })
    }

    return NextResponse.json({ posters })
  } catch (error) {
    console.error("API error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
