import { createClient } from "@/lib/supabase/server"
import { redirect } from "next/navigation"
import UploadForm from "@/components/upload-form"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Vote, Upload } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"

export default async function UploadPage() {
  const supabase = await createClient()
  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect("/auth/login")
  }

  // Get political parties for the form
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
              <Link href="/">Zpět domů</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/dashboard">Nástěnka</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/gallery">Galerie</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <Upload className="h-12 w-12 text-primary" />
              </div>
              <CardTitle className="text-3xl font-bold">Nahrajte politický plakát</CardTitle>
              <CardDescription className="text-lg">
                Sdílejte fotku politického plakátu, který jste objevili ve vaší komunitě
              </CardDescription>
            </CardHeader>
            <CardContent>
              <UploadForm parties={parties || []} />
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
