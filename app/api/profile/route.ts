import { createClient } from "@/lib/supabase/server"
import { type NextRequest, NextResponse } from "next/server"

export async function PUT(request: NextRequest) {
  try {
    const supabase = await createClient()

    const {
      data: { user },
      error: userError,
    } = await supabase.auth.getUser()

    if (userError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const { full_name, avatar_url } = await request.json()

    try {
      const { data, error } = await supabase
        .from("profiles")
        .update({
          full_name,
          avatar_url,
          updated_at: new Date().toISOString(),
        })
        .eq("id", user.id)
        .select()
        .single()

      if (error) {
        console.error("Database error:", error)
        return NextResponse.json({ error: "Failed to update profile" }, { status: 500 })
      }

      return NextResponse.json({ success: true, profile: data })
    } catch (dbError) {
      console.error("Profile update database error:", dbError)
      return NextResponse.json({ error: "Database error occurred" }, { status: 500 })
    }
  } catch (error) {
    console.error("Profile update error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
