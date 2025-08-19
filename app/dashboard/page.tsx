import { createClient } from "@/lib/supabase/server"
import { redirect } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Vote, Upload, MessageSquare, Star, Calendar, MapPin, Eye, Edit } from "lucide-react"
import Link from "next/link"
import Image from "next/image"
import { signOut } from "@/lib/actions"

export default async function DashboardPage() {
  const supabase = createClient()
  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
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
      // Fallback to user metadata if profile fetch fails
      profile = {
        full_name: user.user_metadata?.full_name || user.email?.split("@")[0] || "User",
        avatar_url: user.user_metadata?.avatar_url || null,
        admin: false,
      }
    } else {
      profile = profileData
    }
  } catch (error) {
    console.error("Error fetching profile:", error)
    // Fallback to user metadata
    profile = {
      full_name: user.user_metadata?.full_name || user.email?.split("@")[0] || "User",
      avatar_url: user.user_metadata?.avatar_url || null,
      admin: false,
    }
  }

  const { data: userPosters } = await supabase
    .from("posters")
    .select(`
      *,
      political_parties (
        id,
        name,
        color
      )
    `)
    .eq("uploaded_by", user.id)
    .order("created_at", { ascending: false })

  const { data: userComments } = await supabase
    .from("comments")
    .select(`
      *,
      posters (
        id,
        title
      )
    `)
    .eq("user_id", user.id)
    .order("created_at", { ascending: false })
    .limit(5)

  const { count: ratingsCount } = await supabase
    .from("ratings")
    .select("*", { count: "exact", head: true })
    .eq("user_id", user.id)

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Vote className="h-8 w-8 text-primary" />
            <h1 className="text-2xl font-bold">Political Posters</h1>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="outline" asChild>
              <Link href="/">Home</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/gallery">Gallery</Link>
            </Button>
            <form action={signOut}>
              <Button variant="outline" type="submit">
                Sign Out
              </Button>
            </form>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto space-y-8">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Avatar className="h-16 w-16">
                    <AvatarImage src={profile?.avatar_url || "/placeholder.svg"} alt="Profile picture" />
                    <AvatarFallback className="text-lg">
                      {profile?.full_name ? profile.full_name.charAt(0).toUpperCase() : "U"}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <div className="flex items-center gap-2">
                      <CardTitle className="text-2xl">{profile?.full_name || "User"}</CardTitle>
                      {profile?.admin && (
                        <Badge variant="secondary" className="bg-amber-100 text-amber-800 border-amber-300">
                          🛡️ Admin
                        </Badge>
                      )}
                    </div>
                    <CardDescription className="text-lg">{user.email}</CardDescription>
                  </div>
                </div>
                <Button variant="outline" asChild>
                  <Link href="/profile/edit">
                    <Edit className="mr-2 h-4 w-4" />
                    Edit Profile
                  </Link>
                </Button>
              </div>
            </CardHeader>
          </Card>

          <div className="grid md:grid-cols-3 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Posters Uploaded</CardTitle>
                <Upload className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{userPosters?.length || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {userPosters?.length === 1 ? "poster" : "posters"} shared with the community
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Comments Posted</CardTitle>
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{userComments?.length || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {userComments?.length === 1 ? "comment" : "comments"} on community posters
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Ratings Given</CardTitle>
                <Star className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{ratingsCount || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {ratingsCount === 1 ? "rating" : "ratings"} provided to posters
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common tasks and navigation</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                <Button asChild size="lg" className="h-auto p-4">
                  <Link href="/upload" className="flex flex-col items-center gap-2">
                    <Upload className="h-6 w-6" />
                    <div className="text-center">
                      <div className="font-semibold">Upload New Poster</div>
                      <div className="text-sm text-muted-foreground">Share a political poster you've found</div>
                    </div>
                  </Link>
                </Button>
                <Button variant="outline" asChild size="lg" className="h-auto p-4 bg-transparent">
                  <Link href="/gallery" className="flex flex-col items-center gap-2">
                    <Eye className="h-6 w-6" />
                    <div className="text-center">
                      <div className="font-semibold">Browse Gallery</div>
                      <div className="text-sm text-muted-foreground">Explore community posters</div>
                    </div>
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Your Posters ({userPosters?.length || 0})</CardTitle>
              <CardDescription>Posters you've uploaded to the community</CardDescription>
            </CardHeader>
            <CardContent>
              {!userPosters || userPosters.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-muted-foreground mb-4">You haven't uploaded any posters yet</p>
                  <Button asChild>
                    <Link href="/upload">Upload Your First Poster</Link>
                  </Button>
                </div>
              ) : (
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {userPosters.map((poster) => (
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
                        <div className="space-y-1 text-xs text-muted-foreground mb-3">
                          {poster.location && (
                            <div className="flex items-center gap-1">
                              <MapPin className="h-3 w-3" />
                              <span className="truncate">{poster.location}</span>
                            </div>
                          )}
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            <span>{new Date(poster.created_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                        <Button asChild size="sm" className="w-full">
                          <Link href={`/poster/${poster.id}`}>
                            <Eye className="mr-2 h-4 w-4" />
                            View Details
                          </Link>
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recent Comments</CardTitle>
              <CardDescription>Your latest comments on community posters</CardDescription>
            </CardHeader>
            <CardContent>
              {!userComments || userComments.length === 0 ? (
                <p className="text-muted-foreground text-center py-8">
                  You haven't posted any comments yet. Visit the gallery to start engaging with the community!
                </p>
              ) : (
                <div className="space-y-4">
                  {userComments.map((comment) => (
                    <div key={comment.id} className="border-l-2 border-primary/20 pl-4 py-2">
                      <div className="flex items-center justify-between mb-2">
                        <Link href={`/poster/${comment.posters?.id}`} className="font-medium text-sm hover:underline">
                          {comment.posters?.title}
                        </Link>
                        <span className="text-xs text-muted-foreground">
                          {new Date(comment.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2">{comment.content}</p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
