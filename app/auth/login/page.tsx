import { createClient } from "@/lib/supabase/server"
import { redirect } from "next/navigation"
import LoginForm from "@/components/login-form"

export default async function LoginPage() {
  const supabase = await createClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (session) {
    redirect("/")
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-12 sm:px-6 lg:px-8">
      <LoginForm />
    </div>
  )
}
