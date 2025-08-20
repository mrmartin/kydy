"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Loader2, MessageSquare, Send } from "lucide-react"
import { toast } from "@/hooks/use-toast"

interface Comment {
  id: string
  content: string
  created_at: string
  profiles: {
    id: string
    username: string | null
    full_name: string | null
  } | null
}

interface CommentSectionProps {
  posterId: string
}

export default function CommentSection({ posterId }: CommentSectionProps) {
  const [comments, setComments] = useState<Comment[]>([])
  const [newComment, setNewComment] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Load comments
  useEffect(() => {
    const loadComments = async () => {
      try {
        const response = await fetch(`/api/comments?posterId=${posterId}`)
        if (response.ok) {
          const { comments } = await response.json()
          setComments(comments)
        }
      } catch (error) {
        console.error("Failed to load comments:", error)
      } finally {
        setIsLoading(false)
      }
    }

    loadComments()
  }, [posterId])

  const handleSubmitComment = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!newComment.trim()) {
              toast({
          title: "Komentář je povinný",
          description: "Prosím zadejte komentář před odesláním",
          variant: "destructive",
        })
      return
    }

    setIsSubmitting(true)

    try {
      const response = await fetch("/api/comments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          posterId,
          content: newComment.trim(),
        }),
      })

      if (response.ok) {
        const { comment } = await response.json()
        setComments([comment, ...comments])
        setNewComment("")
        toast({
          title: "Komentář odeslán",
          description: "Váš komentář byl úspěšně přidán",
        })
      } else {
        throw new Error("Failed to post comment")
      }
    } catch (error) {
      console.error("Failed to post comment:", error)
      toast({
        title: "Nepodařilo se odeslat komentář",
        description: "Zkuste to znovu později",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const getDisplayName = (profile: Comment["profiles"]) => {
    if (!profile) return "Anonymous"
    return profile.full_name || profile.username || "Anonymous"
  }

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2)
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

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5" />
          Komentáře ({comments.length})
        </CardTitle>
        <CardDescription>Podělte se o své myšlenky o tomto plakátu</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Comment Form */}
        <form onSubmit={handleSubmitComment} className="space-y-4">
          <Textarea
            placeholder="Napište svůj komentář..."
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            rows={3}
          />
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Odesílám...
              </>
            ) : (
              <>
                <Send className="mr-2 h-4 w-4" />
                Odeslat komentář
              </>
            )}
          </Button>
        </form>

        {/* Comments List */}
        <div className="space-y-4">
          {comments.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">
              Zatím žádné komentáře. Buďte první, kdo se podělí o své myšlenky!
            </p>
          ) : (
            comments.map((comment) => (
              <div key={comment.id} className="flex gap-3 p-4 bg-muted/50 rounded-lg">
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="text-xs">{getInitials(getDisplayName(comment.profiles))}</AvatarFallback>
                </Avatar>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{getDisplayName(comment.profiles)}</span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(comment.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-sm">{comment.content}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}
