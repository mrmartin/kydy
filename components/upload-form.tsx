"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent } from "@/components/ui/card"
import { Loader2, Upload, X, ImageIcon, AlertCircle } from "lucide-react"
import { toast } from "@/hooks/use-toast"
import { validateImageFileClient } from "@/lib/file-validation"

interface Party {
  id: number
  name: string
  color_hex: string
}

interface UploadFormProps {
  parties: Party[]
}

export default function UploadForm({ parties }: UploadFormProps) {
  const router = useRouter()
  const [isUploading, setIsUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [validationError, setValidationError] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    partyId: "",
    location: "",
    datePhotographed: "",
  })

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    setValidationError(null)
    
    if (file) {
      // Client-side pre-validation with comprehensive checks
      const validationResult = validateImageFileClient(file)
      
      if (!validationResult.isValid) {
        setValidationError(validationResult.error || "Neplatný soubor")
        toast({
          title: "Neplatný soubor",
          description: validationResult.error,
          variant: "destructive",
        })
        // Clear the input
        event.target.value = ""
        return
      }

      setSelectedFile(file)
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
    }
  }

  const handleRemoveFile = () => {
    setSelectedFile(null)
    setValidationError(null)
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
      setPreviewUrl(null)
    }
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()

    if (!selectedFile) {
      toast({
        title: "Nebyl vybrán obrázek",
        description: "Prosím vyberte obrázek k nahrání",
        variant: "destructive",
      })
      return
    }

    if (!formData.title.trim()) {
      toast({
        title: "Titulek je povinný",
        description: "Prosím zadejte titulek plakátu",
        variant: "destructive",
      })
      return
    }

    setIsUploading(true)

    try {
      // Upload image with type specification for validation
      const uploadFormData = new FormData()
      uploadFormData.append("file", selectedFile)
      uploadFormData.append("type", "poster")

      console.log("[v0] Starting image upload...")
      const uploadResponse = await fetch("/api/upload", {
        method: "POST",
        body: uploadFormData,
      })

      console.log("[v0] Upload response status:", uploadResponse.status)

      if (!uploadResponse.ok) {
        let errorMessage = "Nahrání obrázku selhalo"
        try {
          const errorData = await uploadResponse.json()
          errorMessage = errorData.message || errorData.error || errorMessage
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
        throw new Error("Neplatná odpověď ze serveru")
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
        title: "Plakát byl úspěšně nahrán!",
        description: "Váš plakát byl sdílen s komunitou",
      })

      router.push(`/poster/${poster.id}`)
    } catch (error) {
      console.error("[v0] Upload error:", error)
      toast({
        title: "Nahrávání selhalo",
        description:
          error instanceof Error ? error.message : "Při nahrávání plakátu došlo k chybě. Zkuste to znovu.",
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
        <label className="block text-sm font-medium">
          Obrázek plakátu * 
          <span className="text-sm text-slate-500 font-normal ml-2">
            (JPG, PNG, GIF, WEBP, 50 KB - 10 MB)
          </span>
        </label>

        {!selectedFile ? (
          <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors">
            <input 
              type="file" 
              accept="image/jpeg,image/jpg,image/png,image/gif,image/webp" 
              onChange={handleFileSelect} 
              className="hidden" 
              id="file-upload" 
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-lg font-medium mb-2">Klikněte pro nahrání obrázku</p>
              <p className="text-sm text-muted-foreground">JPG, PNG, GIF, WEBP • 50 KB - 10 MB</p>
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
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-900 truncate">{selectedFile.name}</p>
                  <p className="text-sm text-slate-500">
                    {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                  {validationError && (
                    <div className="flex items-center gap-1 mt-1 text-red-600">
                      <AlertCircle className="w-4 h-4" />
                      <span className="text-xs">{validationError}</span>
                    </div>
                  )}
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
          Titulek *
        </label>
        <Input
          id="title"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          placeholder="Zadejte popisný titulek plakátu"
          required
        />
      </div>

      {/* Description */}
      <div className="space-y-2">
        <label htmlFor="description" className="block text-sm font-medium">
          Popis
        </label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="Popište plakát, jeho sdělení nebo kontext (volitelné)"
          rows={3}
        />
      </div>

      {/* Political Party */}
      <div className="space-y-2">
        <label className="block text-sm font-medium">Politická strana</label>
        <Select value={formData.partyId} onValueChange={(value) => setFormData({ ...formData, partyId: value })}>
          <SelectTrigger>
            <SelectValue placeholder="Vyberte politickou stranu (volitelné)" />
          </SelectTrigger>
          <SelectContent>
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
      </div>

      {/* Location */}
      <div className="space-y-2">
        <label htmlFor="location" className="block text-sm font-medium">
          Místo
        </label>
        <Input
          id="location"
          value={formData.location}
          onChange={(e) => setFormData({ ...formData, location: e.target.value })}
          placeholder="Kde byl tento plakát spatřen? (volitelné)"
        />
      </div>

      {/* Date Photographed */}
      <div className="space-y-2">
        <label htmlFor="datePhotographed" className="block text-sm font-medium">
          Datum vyfotografování
        </label>
        <Input
          id="datePhotographed"
          type="date"
          value={formData.datePhotographed}
          onChange={(e) => setFormData({ ...formData, datePhotographed: e.target.value })}
        />
      </div>

      {/* Submit Button */}
      <Button 
        type="submit" 
        disabled={isUploading || !selectedFile || !!validationError} 
        className="w-full" 
        size="lg"
      >
        {isUploading ? (
          <>
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            Nahrávám...
          </>
        ) : (
          <>
            <ImageIcon className="mr-2 h-5 w-5" />
            Nahrát plakát
          </>
        )}
      </Button>
    </form>
  )
}
