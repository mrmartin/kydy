"use client"

import { useState, useMemo } from "react"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Search, Filter, Calendar, MapPin, User, Eye } from "lucide-react"
import Link from "next/link"
import Image from "next/image"

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
            Filter & Search
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search posters..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Party Filter */}
            <Select value={selectedParty} onValueChange={setSelectedParty}>
              <SelectTrigger>
                <SelectValue placeholder="Filter by party" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Parties</SelectItem>
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
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="newest">Newest First</SelectItem>
                <SelectItem value="oldest">Oldest First</SelectItem>
                <SelectItem value="title">Title A-Z</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Results Count */}
      <div className="flex items-center justify-between">
        <p className="text-muted-foreground">
          {filteredAndSortedPosters.length} poster{filteredAndSortedPosters.length !== 1 ? "s" : ""} found
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
            Clear Filters
          </Button>
        )}
      </div>

      {/* Poster Grid */}
      {filteredAndSortedPosters.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-muted-foreground text-lg mb-4">No posters found matching your criteria</p>
            <Button asChild>
              <Link href="/upload">Upload the First Poster</Link>
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
                      <div className="flex items-center gap-1">
                        <User className="h-3 w-3" />
                        <span>{poster.profiles.full_name || poster.profiles.username || "Anonymous"}</span>
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
                      View Details
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
