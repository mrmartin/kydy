import { createClient } from "@/lib/supabase/server"
import { redirect } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Vote, Upload, MessageSquare, Star, Users } from "lucide-react"
import Link from "next/link"
import { signOut } from "@/lib/actions"
import Image from "next/image"

export default async function Home() {
  const supabase = await createClient()
  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect("/auth/login")
  }

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
            <Button variant="ghost" asChild>
              <Link href="/dashboard">Nástěnka</Link>
            </Button>
            <span className="text-sm text-muted-foreground">Vítejte, {user.email}</span>
            <form action={signOut}>
              <Button variant="outline" type="submit">
                Odhlásit se
              </Button>
            </form>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">Objevte politické plakáty z celé republiky</h2>
          <p className="text-xl text-muted-foreground mb-8">
            Komunitní platforma pro sdílení, diskuzi a hodnocení politických kampaní
          </p>
          <div className="flex gap-4 justify-center">
            <Button asChild size="lg">
              <Link href="/upload">
                <Upload className="mr-2 h-5 w-5" />
                Nahrát plakát
              </Link>
            </Button>
            <Button variant="outline" asChild size="lg">
              <Link href="/gallery">Procházet galerii</Link>
            </Button>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <Card>
            <CardHeader>
              <Upload className="h-8 w-8 text-primary mb-2" />
              <CardTitle>Nahrát a sdílet</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>Sdílejte fotky politických plakátů, které jste našli ve vaší komunitě</CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <MessageSquare className="h-8 w-8 text-primary mb-2" />
              <CardTitle>Diskutovat a komentovat</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>Zapojte se do smysluplných diskuzí o politickém sdělení a designu</CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Star className="h-8 w-8 text-primary mb-2" />
              <CardTitle>Hodnotit a recenzovat</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>Odnoťte plakáty podle designu, srozumitelnosti sdělení a celkového dopadu</CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Users className="h-8 w-8 text-primary mb-2" />
              <CardTitle>Komunitní řízení</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>Připojte se ke komunitě občanů dokumentujících politické kampaně</CardDescription>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity Placeholder */}
        <RecentActivity />
      </main>
    </div>
  )
}

async function RecentActivity() {
  const supabase = await createClient()

  const { data: recentPosters } = await supabase
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
    .limit(3)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Nedávná aktivita</CardTitle>
        <CardDescription>Nejnovější plakáty sdílené komunitou</CardDescription>
      </CardHeader>
      <CardContent>
        {!recentPosters || recentPosters.length === 0 ? (
          <p className="text-muted-foreground text-center py-8">
            Zatím nebyly nahrány žádné plakáty. Buďte první, kdo sdílí politický plakát!
          </p>
        ) : (
          <div className="grid md:grid-cols-3 gap-4">
            {recentPosters.map((poster: any) => (
              <Card key={poster.id} className="group hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="aspect-video relative mb-3 overflow-hidden rounded-lg bg-muted">
                    <Image
                      src={poster.image_url || "/placeholder.svg"}
                      alt={poster.title}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  </div>
                  <h4 className="font-semibold line-clamp-1 mb-1">{poster.title}</h4>
                  {poster.political_parties && (
                    <Badge
                      variant="secondary"
                      className="text-xs mb-2"
                      style={{
                        backgroundColor: `${poster.political_parties.color_hex}20`,
                        color: poster.political_parties.color_hex,
                        borderColor: poster.political_parties.color_hex,
                      }}
                    >
                      {poster.political_parties.name}
                    </Badge>
                  )}
                  <Button asChild size="sm" className="w-full">
                    <Link href={`/poster/${poster.id}`}>Zobrazit detail</Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
