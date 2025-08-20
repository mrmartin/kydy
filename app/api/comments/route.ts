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
    const { posterId, content } = body

    if (!posterId || !content?.trim()) {
      return NextResponse.json({ error: "Missing required fields" }, { status: 400 })
    }

    // Insert comment into database
    const { data: comment, error } = await supabase
      .from("comments")
      .insert({
        poster_id: posterId,
        user_id: user.id,
        content: content.trim(),
      })
      .select("*")
      .single()

    if (error) {
      console.error("Database error:", error)
      return NextResponse.json({ error: "Failed to save comment" }, { status: 500 })
    }

    const commentWithProfile = {
      ...comment,
      profiles: {
        id: user.id,
        full_name: "Community Member",
      },
    }

    return NextResponse.json({ comment: commentWithProfile })
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

    const supabase = await createClient()

    // Get comments for the poster
    const { data: comments, error } = await supabase
      .from("comments")
      .select("*")
      .eq("poster_id", posterId)
      .order("created_at", { ascending: false })

    if (error) {
      console.error("Database error:", error)
      return NextResponse.json({ error: "Failed to fetch comments" }, { status: 500 })
    }

    const commentsWithProfiles =
      comments?.map((comment) => ({
        ...comment,
        profiles: {
          id: comment.user_id,
          full_name: "Community Member",
        },
      })) || []

    return NextResponse.json({ comments: commentsWithProfiles })
  } catch (error) {
    console.error("API error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
