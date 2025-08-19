"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent } from "@/components/ui/card"
import { Loader2, Upload, X, ImageIcon } from "lucide-react"
import { toast } from "@/hooks/use-toast"

interface Party {
  id: number
  name: string
  color: string
}

interface UploadFormProps {
  parties: Party[]
}

export default function UploadForm({ parties }: UploadFormProps) {
  const router = useRouter()
  const [isUploading, setIsUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    partyId: "",
    location: "",
    datePhotographed: "",
  })

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (file.type.startsWith("image/")) {
        setSelectedFile(file)
        const url = URL.createObjectURL(file)
        setPreviewUrl(url)
      } else {
        toast({
          title: "Invalid file type",
          description: "Please select an image file (JPG, PNG, etc.)",
          variant: "destructive",
        })
      }
    }
  }

  const handleRemoveFile = () => {
    setSelectedFile(null)
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
      setPreviewUrl(null)
    }
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()

    if (!selectedFile) {
      toast({
        title: "No image selected",
        description: "Please select an image to upload",
        variant: "destructive",
      })
      return
    }

    if (!formData.title.trim()) {
      toast({
        title: "Title required",
        description: "Please enter a title for the poster",
        variant: "destructive",
      })
      return
    }

    setIsUploading(true)

    try {
      // Upload image to Blob storage
      const uploadFormData = new FormData()
      uploadFormData.append("file", selectedFile)

      console.log("[v0] Starting image upload...")
      const uploadResponse = await fetch("/api/upload", {
        method: "POST",
        body: uploadFormData,
      })

      console.log("[v0] Upload response status:", uploadResponse.status)

      if (!uploadResponse.ok) {
        let errorMessage = "Failed to upload image"
        try {
          const errorData = await uploadResponse.json()
          errorMessage = errorData.error || errorMessage
        } catch {
          // Response is not JSON, use status text
          errorMessage = uploadResponse.statusText || errorMessage
        }
        throw new Error(errorMessage)
      }

      let uploadResult
      try {
        uploadResult = await uploadResponse.json()
        console.log("[v0] Upload result:", uploadResult)
      } catch (parseError) {
        console.error("[v0] Failed to parse upload response as JSON:", parseError)
        throw new Error("Invalid response from upload server")
      }

      const { url: imageUrl, filename } = uploadResult

      // Save poster metadata to database
      const posterData = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        imageUrl,
        filename,
        partyId: formData.partyId ? Number.parseInt(formData.partyId) : null,
        location: formData.location.trim() || null,
        datePhotographed: formData.datePhotographed || null,
      }

      console.log("[v0] Saving poster data:", posterData)
      const saveResponse = await fetch("/api/posters", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(posterData),
      })

      if (!saveResponse.ok) {
        let errorMessage = "Failed to save poster"
        try {
          const errorData = await saveResponse.json()
          errorMessage = errorData.error || errorMessage
        } catch {
          errorMessage = saveResponse.statusText || errorMessage
        }
        throw new Error(errorMessage)
      }

      const { poster } = await saveResponse.json()

      toast({
        title: "Poster uploaded successfully!",
        description: "Your poster has been shared with the community",
      })

      router.push(`/poster/${poster.id}`)
    } catch (error) {
      console.error("[v0] Upload error:", error)
      toast({
        title: "Upload failed",
        description:
          error instanceof Error ? error.message : "There was an error uploading your poster. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* File Upload */}
      <div className="space-y-4">
        <label className="block text-sm font-medium">Poster Image *</label>

        {!selectedFile ? (
          <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors">
            <input type="file" accept="image/*" onChange={handleFileSelect} className="hidden" id="file-upload" />
            <label htmlFor="file-upload" className="cursor-pointer">
              <ImageIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-lg font-medium mb-2">Click to upload an image</p>
              <p className="text-sm text-muted-foreground">PNG, JPG, GIF up to 10MB</p>
            </label>
          </div>
        ) : (
          <Card>
            <CardContent className="p-4">
              <div className="flex items-start gap-4">
                <div className="relative">
                  <img
                    src={previewUrl! || "/placeholder.svg"}
                    alt="Preview"
                    className="w-24 h-24 object-cover rounded-lg"
                  />
                </div>
                <div className="flex-1">
                  <p className="font-medium">{selectedFile.name}</p>
                  <p className="text-sm text-muted-foreground">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <Button type="button" variant="ghost" size="sm" onClick={handleRemoveFile}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Title */}
      <div className="space-y-2">
        <label htmlFor="title" className="block text-sm font-medium">
          Title *
        </label>
        <Input
          id="title"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          placeholder="Enter a descriptive title for the poster"
          required
        />
      </div>

      {/* Description */}
      <div className="space-y-2">
        <label htmlFor="description" className="block text-sm font-medium">
          Description
        </label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="Describe the poster, its message, or context (optional)"
          rows={3}
        />
      </div>

      {/* Political Party */}
      <div className="space-y-2">
        <label className="block text-sm font-medium">Political Party</label>
        <Select value={formData.partyId} onValueChange={(value) => setFormData({ ...formData, partyId: value })}>
          <SelectTrigger>
            <SelectValue placeholder="Select a political party (optional)" />
          </SelectTrigger>
          <SelectContent>
            {parties.map((party) => (
              <SelectItem key={party.id} value={party.id.toString()}>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: party.color }} />
                  {party.name}
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Location */}
      <div className="space-y-2">
        <label htmlFor="location" className="block text-sm font-medium">
          Location
        </label>
        <Input
          id="location"
          value={formData.location}
          onChange={(e) => setFormData({ ...formData, location: e.target.value })}
          placeholder="Where was this poster spotted? (optional)"
        />
      </div>

      {/* Date Photographed */}
      <div className="space-y-2">
        <label htmlFor="datePhotographed" className="block text-sm font-medium">
          Date Photographed
        </label>
        <Input
          id="datePhotographed"
          type="date"
          value={formData.datePhotographed}
          onChange={(e) => setFormData({ ...formData, datePhotographed: e.target.value })}
        />
      </div>

      {/* Submit Button */}
      <Button type="submit" disabled={isUploading} className="w-full" size="lg">
        {isUploading ? (
          <>
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            Uploading...
          </>
        ) : (
          <>
            <Upload className="mr-2 h-5 w-5" />
            Upload Poster
          </>
        )}
      </Button>
    </form>
  )
}
