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
  const supabase = createClient()
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
            <h1 className="text-2xl font-bold">Political Posters</h1>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" asChild>
              <Link href="/dashboard">Dashboard</Link>
            </Button>
            <span className="text-sm text-muted-foreground">Welcome, {user.email}</span>
            <form action={signOut}>
              <Button variant="outline" type="submit">
                Sign Out
              </Button>
            </form>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">Discover Political Posters from Around the World</h2>
          <p className="text-xl text-muted-foreground mb-8">
            A community-driven platform for sharing, discussing, and rating political campaign materials
          </p>
          <div className="flex gap-4 justify-center">
            <Button asChild size="lg">
              <Link href="/upload">
                <Upload className="mr-2 h-5 w-5" />
                Upload Poster
              </Link>
            </Button>
            <Button variant="outline" asChild size="lg">
              <Link href="/gallery">Browse Gallery</Link>
            </Button>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <Card>
            <CardHeader>
              <Upload className="h-8 w-8 text-primary mb-2" />
              <CardTitle>Upload & Share</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>Share photos of political posters you've spotted in your community</CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <MessageSquare className="h-8 w-8 text-primary mb-2" />
              <CardTitle>Discuss & Comment</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>Engage in meaningful discussions about political messaging and design</CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Star className="h-8 w-8 text-primary mb-2" />
              <CardTitle>Rate & Review</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>Rate posters based on design, message clarity, and overall impact</CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Users className="h-8 w-8 text-primary mb-2" />
              <CardTitle>Community Driven</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>Join a community of citizens documenting political campaigns</CardDescription>
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
  const supabase = createClient()

  const { data: recentPosters } = await supabase
    .from("posters")
    .select(`
      *,
      political_parties (
        id,
        name,
        color
      )
    `)
    .order("created_at", { ascending: false })
    .limit(3)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
        <CardDescription>Latest posters shared by the community</CardDescription>
      </CardHeader>
      <CardContent>
        {!recentPosters || recentPosters.length === 0 ? (
          <p className="text-muted-foreground text-center py-8">
            No posters uploaded yet. Be the first to share a political poster!
          </p>
        ) : (
          <div className="grid md:grid-cols-3 gap-4">
            {recentPosters.map((poster) => (
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
                        backgroundColor: `${poster.political_parties.color}20`,
                        color: poster.political_parties.color,
                        borderColor: poster.political_parties.color,
                      }}
                    >
                      {poster.political_parties.name}
                    </Badge>
                  )}
                  <Button asChild size="sm" className="w-full">
                    <Link href={`/poster/${poster.id}`}>View Details</Link>
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
