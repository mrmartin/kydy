import { createClient } from "@/lib/supabase/server"
import { redirect } from "next/navigation"
import GalleryClient from "@/components/gallery-client"
import { Vote } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"

export default async function GalleryPage() {
  const supabase = await createClient()
  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect("/auth/login")
  }

  // Get all posters with related data
  const { data: posters } = await supabase
    .from("posters")
    .select(`
      *,
      political_parties (
        id,
        name,
        color_hex
      )
    `)
    .order("created_at", { ascending: false })

  // Get political parties for filtering
  const { data: parties } = await supabase.from("political_parties").select("*").order("name")

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Vote className="h-8 w-8 text-primary" />
            <h1 className="text-2xl font-bold">Politické plakáty</h1>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="outline" asChild>
              <Link href="/">Domů</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/dashboard">Nástěnka</Link>
            </Button>
            <Button asChild>
              <Link href="/upload">Nahrát plakát</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2">Galerie plakátů</h2>
          <p className="text-muted-foreground">Prozkoumejte politické plakáty sdílené komunitou</p>
        </div>

        <GalleryClient posters={posters || []} parties={parties || []} />
      </main>
    </div>
  )
}
