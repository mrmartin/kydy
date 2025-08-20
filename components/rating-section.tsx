"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Star, Loader2 } from "lucide-react"
import { toast } from "@/hooks/use-toast"
import { cn } from "@/lib/utils"

interface RatingData {
  averageRating: number
  totalRatings: number
  userRating: number | null
}

interface RatingSectionProps {
  posterId: string
}

export default function RatingSection({ posterId }: RatingSectionProps) {
  const [ratingData, setRatingData] = useState<RatingData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [hoveredRating, setHoveredRating] = useState<number | null>(null)

  // Load rating data
  useEffect(() => {
    const loadRatings = async () => {
      try {
        const response = await fetch(`/api/ratings?posterId=${posterId}`)
        if (response.ok) {
          const data = await response.json()
          setRatingData(data)
        }
      } catch (error) {
        console.error("Failed to load ratings:", error)
      } finally {
        setIsLoading(false)
      }
    }

    loadRatings()
  }, [posterId])

  const handleRatingSubmit = async (rating: number) => {
    setIsSubmitting(true)

    try {
      const response = await fetch("/api/ratings", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          posterId,
          rating,
        }),
      })

      if (response.ok) {
        // Reload rating data
        const ratingResponse = await fetch(`/api/ratings?posterId=${posterId}`)
        if (ratingResponse.ok) {
          const data = await ratingResponse.json()
          setRatingData(data)
        }

        toast({
          title: "Hodnocení odesláno",
          description: `Ohodnotil jste tento plakát ${rating} hvězdičk${rating !== 1 ? "ami" : "ou"}`,
        })
      } else {
        throw new Error("Failed to submit rating")
      }
    } catch (error) {
      console.error("Failed to submit rating:", error)
      toast({
        title: "Nepodařilo se odeslat hodnocení",
        description: "Zkuste to znovu později",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const renderStars = (rating: number, interactive = false) => {
    return Array.from({ length: 5 }, (_, i) => {
      const starValue = i + 1
      const isFilled = starValue <= rating
      const isHovered = hoveredRating !== null && starValue <= hoveredRating

      return (
        <Star
          key={i}
          className={cn(
            "h-5 w-5 transition-colors",
            interactive && "cursor-pointer hover:scale-110 transition-transform",
            isFilled || isHovered ? "fill-yellow-400 text-yellow-400" : "text-muted-foreground",
          )}
          onClick={interactive ? () => handleRatingSubmit(starValue) : undefined}
          onMouseEnter={interactive ? () => setHoveredRating(starValue) : undefined}
          onMouseLeave={interactive ? () => setHoveredRating(null) : undefined}
        />
      )
    })
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin" />
        </CardContent>
      </Card>
    )
  }

  if (!ratingData) {
    return null
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Star className="h-5 w-5" />
          Hodnocení a recenze
        </CardTitle>
        <CardDescription>Odnoťte tento plakát a podívejte se, co si myslí ostatní</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Average Rating Display */}
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center gap-2">
            {renderStars(ratingData.averageRating)}
            <span className="text-2xl font-bold">{ratingData.averageRating.toFixed(1)}</span>
          </div>
          <p className="text-sm text-muted-foreground">
            Na základě {ratingData.totalRatings} hodnocení{ratingData.totalRatings !== 1 ? "" : ""}
          </p>
        </div>

        {/* User Rating Section */}
        <div className="border-t pt-6">
          <h4 className="font-medium mb-3">{ratingData.userRating ? "Vaše hodnocení" : "Odnoťte tento plakát"}</h4>

          {ratingData.userRating ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                {renderStars(ratingData.userRating)}
                <span className="text-sm text-muted-foreground">
                  Ohodnotil jste {ratingData.userRating} hvězdičk{ratingData.userRating !== 1 ? "ami" : "ou"}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">Klikněte na hvězdičky pro aktualizaci hodnocení</p>
              <div className="flex items-center gap-1" onMouseLeave={() => setHoveredRating(null)}>
                {isSubmitting ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  renderStars(hoveredRating || ratingData.userRating, true)
                )}
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">Klikněte na hvězdičky pro ohodnocení plakátu</p>
              <div className="flex items-center gap-1" onMouseLeave={() => setHoveredRating(null)}>
                {isSubmitting ? <Loader2 className="h-5 w-5 animate-spin" /> : renderStars(hoveredRating || 0, true)}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
