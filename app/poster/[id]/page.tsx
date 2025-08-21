import { createClient } from "@/lib/supabase/server"
import { notFound } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Vote, MapPin, Calendar, User, ArrowLeft, Maximize2 } from "lucide-react"
import Link from "next/link"
import Image from "next/image"
import CommentSection from "@/components/comment-section"
import RatingSection from "@/components/rating-section"
import FullscreenPosterModal from "@/components/fullscreen-poster-modal"

interface PosterPageProps {
  params: {
    id: string
  }
}

export default async function PosterPage({ params }: PosterPageProps) {
  const supabase = await createClient()
  const resolvedParams = await params

  // Get user (for navigation context)
  const {
    data: { user },
  } = await supabase.auth.getUser()

  const { data: poster, error } = await supabase
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
        full_name,
        username,
        avatar_url
      )
    `)
    .eq("id", resolvedParams.id)
    .single()

  if (error || !poster) {
    console.log("[v0] Poster query error:", error)
    console.log("[v0] Poster ID:", resolvedParams.id)
    notFound()
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Vote className="h-8 w-8 text-primary" />
            <h1 className="text-2xl font-bold">KYDY.cz - Politické Plakáty</h1>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="outline" asChild>
              <Link href="/">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Zpět domů
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/gallery">Galerie</Link>
            </Button>
            {user ? (
              // Logged in user navigation
              <>
                <Button variant="outline" asChild>
                  <Link href="/dashboard">Nástěnka</Link>
                </Button>
                <Button asChild>
                  <Link href="/upload">Nahrát plakát</Link>
                </Button>
              </>
            ) : (
              // Non-logged in user navigation
              <>
                <Button variant="outline" asChild>
                  <Link href="/auth/login">Přihlásit se</Link>
                </Button>
                <Button asChild>
                  <Link href="/auth/signup">Registrovat se</Link>
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Poster Details */}
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-3xl font-bold mb-2">{poster.title}</CardTitle>
                  {poster.description && <CardDescription className="text-lg">{poster.description}</CardDescription>}
                </div>
                {poster.political_parties && (
                  <Badge
                    variant="secondary"
                    className="ml-4"
                    style={{
                      backgroundColor: `${poster.political_parties.color_hex}20`,
                      color: poster.political_parties.color_hex,
                      borderColor: poster.political_parties.color_hex,
                    }}
                  >
                    {poster.political_parties.name}
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Poster Image */}
              <div className="relative aspect-video w-full overflow-hidden rounded-lg bg-muted group">
                <Image
                  src={poster.image_url || "/placeholder.svg"}
                  alt={poster.title}
                  fill
                  className="object-contain"
                  priority
                />
                {/* Fullscreen button */}
                <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <FullscreenPosterModal
                    imageUrl={poster.image_url}
                    title={poster.title}
                    triggerClassName="bg-black/50 hover:bg-black/70 text-white border-none"
                  />
                </div>
              </div>

              {/* Metadata */}
              <div className="grid md:grid-cols-2 gap-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4" />
                  <span>Nahráno: {poster.profiles?.full_name || poster.profiles?.username || "Anonymní uživatel"}</span>
                </div>

                {poster.location && (
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    <span>{poster.location}</span>
                  </div>
                )}

                {poster.date_photographed && (
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    <span>Vyfotografováno {new Date(poster.date_photographed).toLocaleDateString()}</span>
                  </div>
                )}

                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  <span>Nahráno {new Date(poster.created_at).toLocaleDateString()}</span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-4 pt-4 border-t">
                <Button variant="outline" asChild>
                  <Link href="/gallery">Zobrazit další plakáty</Link>
                </Button>
                <Button asChild>
                  <Link href="/upload">Nahrajte vlastní</Link>
                </Button>
              </div>
            </CardContent>
          </Card>

          <RatingSection posterId={poster.id} user={user} />

          <CommentSection posterId={poster.id} user={user} />
        </div>
      </main>
    </div>
  )
}
