import { createClient } from "@/lib/supabase/server"
import { redirect } from "next/navigation"
import EditProfileForm from "@/components/edit-profile-form"

export default async function EditProfilePage() {
  const supabase = await createClient()

  const {
    data: { user },
    error: userError,
  } = await supabase.auth.getUser()

  if (userError || !user) {
    redirect("/auth/login")
  }

  let profile
  try {
    const { data: profileData, error: profileError } = await supabase
      .from("profiles")
      .select("*")
      .eq("id", user.id)
      .single()

    if (profileError || !profileData) {
      // Fallback to user metadata if profile doesn't exist
      profile = {
        id: user.id,
        user_id: user.id,
        full_name: user.user_metadata?.full_name || user.email?.split("@")[0] || "User",
        avatar_url: user.user_metadata?.avatar_url || null,
        admin: false,
        created_at: user.created_at,
        updated_at: user.updated_at,
      }
    } else {
      profile = profileData
    }
  } catch (error) {
    console.error("Error fetching profile:", error)
    // Fallback to user metadata
    profile = {
      id: user.id,
      user_id: user.id,
      full_name: user.user_metadata?.full_name || user.email?.split("@")[0] || "User",
      avatar_url: user.user_metadata?.avatar_url || null,
      admin: false,
      created_at: user.created_at,
      updated_at: user.updated_at,
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-8">
      <div className="container mx-auto px-4 max-w-2xl">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Upravit profil</h1>
            <p className="text-slate-600">Aktualizujte informace o profilu a obrázek</p>
          </div>

          <EditProfileForm profile={profile} />
        </div>
      </div>
    </div>
  )
}
