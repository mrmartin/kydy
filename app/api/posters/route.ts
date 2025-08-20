import { type NextRequest, NextResponse } from "next/server"
import { createClient } from "@/lib/supabase/server"

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
        image_filename: filename || 'unknown',
        party_id: partyId || null,
        uploaded_by: user.id,
        location: location?.trim() || null,
        date_photographed: datePhotographed || null,
      })
      .select()
      .single()

    if (error) {
      console.error("Database error:", error)
      
      // If error is due to missing profile, try to create one
      if (error.code === '23503' && error.message.includes('posters_uploaded_by_fkey')) {
        console.log("Missing user profile, attempting to create one...")
        
        // Create profile for the user
        const { error: profileError } = await supabase
          .from("profiles")
          .insert({
            id: user.id,
            email: user.email || 'unknown@example.com',
            full_name: user.user_metadata?.full_name || user.email || 'Unknown User',
            avatar_url: user.user_metadata?.avatar_url || null
          })
        
        if (profileError) {
          console.error("Failed to create profile:", profileError)
          return NextResponse.json({ 
            error: "Failed to create user profile. Please try signing up again." 
          }, { status: 500 })
        }
        
        // Retry the poster insertion
        const { data: retryPoster, error: retryError } = await supabase
          .from("posters")
          .insert({
            title: title.trim(),
            description: description?.trim() || null,
            image_url: imageUrl,
            image_filename: filename || 'unknown',
            party_id: partyId || null,
            uploaded_by: user.id,
            location: location?.trim() || null,
            date_photographed: datePhotographed || null,
          })
          .select()
          .single()
        
        if (retryError) {
          console.error("Retry failed:", retryError)
          return NextResponse.json({ error: "Failed to save poster after profile creation" }, { status: 500 })
        }
        
        return NextResponse.json({ poster: retryPoster })
      }
      
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
    const supabase = await createClient()

    // Get all posters with related data
    const { data: posters, error } = await supabase
      .from("posters")
      .select(`
        *,
        political_parties (
          id,
          name,
          color_hex
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
