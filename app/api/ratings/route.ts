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
    const { posterId, rating } = body

    if (!posterId || !rating || rating < 1 || rating > 5) {
      return NextResponse.json({ error: "Invalid rating (must be 1-5)" }, { status: 400 })
    }

    // Upsert rating (insert or update if exists)
    const { data: ratingData, error } = await supabase
      .from("ratings")
      .upsert(
        {
          poster_id: posterId,
          user_id: user.id,
          rating: rating,
        },
        {
          onConflict: "poster_id,user_id",
        },
      )
      .select()
      .single()

    if (error) {
      console.error("Database error:", error)
      return NextResponse.json({ error: "Failed to save rating" }, { status: 500 })
    }

    return NextResponse.json({ rating: ratingData })
  } catch (error) {
    console.error("API error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const posterId = searchParams.get("posterId")

    if (!posterId) {
      return NextResponse.json({ error: "Poster ID required" }, { status: 400 })
    }

    const supabase = createClient()

    // Get rating statistics for the poster
    const { data: ratings, error } = await supabase.from("ratings").select("rating").eq("poster_id", posterId)

    if (error) {
      console.error("Database error:", error)
      return NextResponse.json({ error: "Failed to fetch ratings" }, { status: 500 })
    }

    const totalRatings = ratings.length
    const averageRating = totalRatings > 0 ? ratings.reduce((sum, r) => sum + r.rating, 0) / totalRatings : 0

    // Get current user's rating if authenticated
    const {
      data: { user },
    } = await supabase.auth.getUser()

    let userRating = null
    if (user) {
      const { data: userRatingData } = await supabase
        .from("ratings")
        .select("rating")
        .eq("poster_id", posterId)
        .eq("user_id", user.id)
        .single()

      userRating = userRatingData?.rating || null
    }

    return NextResponse.json({
      averageRating: Math.round(averageRating * 10) / 10, // Round to 1 decimal
      totalRatings,
      userRating,
    })
  } catch (error) {
    console.error("API error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
