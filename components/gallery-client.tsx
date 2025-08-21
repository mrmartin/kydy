"use client"

import { useState, useMemo } from "react"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Search, Filter, Calendar, MapPin, User, Eye, Maximize2 } from "lucide-react"
import Link from "next/link"
import Image from "next/image"
import FullscreenPosterModal from "@/components/fullscreen-poster-modal"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

interface Poster {
  id: string
  title: string
  description: string | null
  image_url: string
  location: string | null
  date_photographed: string | null
  created_at: string
  political_parties: {
    id: number
    name: string
    color_hex: string
  } | null
  profiles: {
    id: string
    username: string | null
    full_name: string | null
    avatar_url: string | null
  } | null
}

interface Party {
  id: number
  name: string
  color_hex: string
}

interface GalleryClientProps {
  posters: Poster[]
  parties: Party[]
}

export default function GalleryClient({ posters, parties }: GalleryClientProps) {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedParty, setSelectedParty] = useState<string>("all")
  const [sortBy, setSortBy] = useState<string>("newest")

  const filteredAndSortedPosters = useMemo(() => {
    let filtered = posters

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(
        (poster) =>
          poster.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          poster.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          poster.location?.toLowerCase().includes(searchTerm.toLowerCase()),
      )
    }

    // Filter by political party
    if (selectedParty !== "all") {
      filtered = filtered.filter((poster) => poster.political_parties?.id.toString() === selectedParty)
    }

    // Sort posters
    filtered.sort((a, b) => {
      switch (sortBy) {
        case "newest":
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        case "oldest":
          return new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        case "title":
          return a.title.localeCompare(b.title)
        default:
          return 0
      }
    })

    return filtered
  }, [posters, searchTerm, selectedParty, sortBy])

  return (
    <div className="space-y-6">
      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filtrovat a vyhledávat
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Hledat plakáty..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Party Filter */}
            <Select value={selectedParty} onValueChange={setSelectedParty}>
              <SelectTrigger>
                <SelectValue placeholder="Filtrovat podle strany" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Všechny strany</SelectItem>
                {parties.map((party) => (
                  <SelectItem key={party.id} value={party.id.toString()}>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: party.color_hex }} />
                      {party.name}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Sort */}
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger>
                <SelectValue placeholder="Seřadit podle" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="newest">Nejnovější první</SelectItem>
                <SelectItem value="oldest">Nejstarší první</SelectItem>
                <SelectItem value="title">Název A-Z</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Results Count */}
      <div className="flex items-center justify-between">
        <p className="text-muted-foreground">
          {filteredAndSortedPosters.length} plakát{filteredAndSortedPosters.length !== 1 ? "ů" : ""} nalezeno
        </p>
        {(searchTerm || selectedParty !== "all") && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setSearchTerm("")
              setSelectedParty("all")
            }}
          >
            Vymazat filtry
          </Button>
        )}
      </div>

      {/* Poster Grid */}
      {filteredAndSortedPosters.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-muted-foreground text-lg mb-4">Nebyly nalezeny žádné plakáty odpovídající kritériím</p>
            <Button asChild>
              <Link href="/upload">Nahrajte první plakát</Link>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredAndSortedPosters.map((poster) => (
            <Card key={poster.id} className="group hover:shadow-lg transition-shadow">
              <CardHeader className="p-0">
                <div className="relative aspect-[4/3] overflow-hidden rounded-t-lg bg-muted">
                  <Image
                    src={poster.image_url || "/placeholder.svg"}
                    alt={poster.title}
                    fill
                    className="object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors" />
                  {/* Fullscreen button */}
                  <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                    <FullscreenPosterModal
                      imageUrl={poster.image_url}
                      title={poster.title}
                    >
                      <Button 
                        variant="secondary" 
                        size="sm"
                        className="bg-black/50 hover:bg-black/70 text-white border-none p-2 h-auto"
                      >
                        <Maximize2 className="h-4 w-4" />
                        <span className="sr-only">Celá obrazovka</span>
                      </Button>
                    </FullscreenPosterModal>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-4">
                <div className="space-y-3">
                  {/* Title and Party */}
                  <div>
                    <h3 className="font-semibold line-clamp-2 mb-1">{poster.title}</h3>
                    {poster.political_parties && (
                      <Badge
                        variant="secondary"
                        className="text-xs"
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

                  {/* Description */}
                  {poster.description && (
                    <p className="text-sm text-muted-foreground line-clamp-2">{poster.description}</p>
                  )}

                  {/* Metadata */}
                  <div className="space-y-1 text-xs text-muted-foreground">
                    {poster.profiles && (
                      <div className="flex items-center gap-2">
                        <Avatar className="h-4 w-4">
                          {poster.profiles.avatar_url && (
                            <AvatarImage src={poster.profiles.avatar_url} alt={poster.profiles.full_name || poster.profiles.username || "User"} />
                          )}
                          <AvatarFallback className="text-[8px]">
                            {(poster.profiles.full_name || poster.profiles.username || "A").charAt(0).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <span>{poster.profiles.full_name || poster.profiles.username || "Anonymní uživatel"}</span>
                      </div>
                    )}

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

                  {/* View Button */}
                  <Button asChild size="sm" className="w-full">
                    <Link href={`/poster/${poster.id}`}>
                      <Eye className="mr-2 h-4 w-4" />
                      Zobrazit detail
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
