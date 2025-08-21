"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Camera, Save, ArrowLeft, AlertCircle } from "lucide-react"
import { useRouter } from "next/navigation"
import { toast } from "@/hooks/use-toast"
import { validateImageFileClient } from "@/lib/file-validation"

interface Profile {
  id: string
  full_name: string | null
  email: string | null
  avatar_url: string | null
  admin: boolean
}

interface EditProfileFormProps {
  profile: Profile
}

export default function EditProfileForm({ profile }: EditProfileFormProps) {
  const router = useRouter()
  const [fullName, setFullName] = useState(profile.full_name || "")
  const [avatarFile, setAvatarFile] = useState<File | null>(null)
  const [avatarPreview, setAvatarPreview] = useState(profile.avatar_url || "")
  const [validationError, setValidationError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    setValidationError(null)
    
    if (file) {
      // Client-side pre-validation
      const validationResult = validateImageFileClient(file)
      
      if (!validationResult.isValid) {
        setValidationError(validationResult.error || "Neplatný soubor")
        toast({
          title: "Neplatný soubor",
          description: validationResult.error,
          variant: "destructive",
        })
        // Clear the input
        e.target.value = ""
        return
      }

      setAvatarFile(file)
      const reader = new FileReader()
      reader.onload = (e) => {
        setAvatarPreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      let avatarUrl = profile.avatar_url

      // Upload new avatar if selected
      if (avatarFile) {
        const formData = new FormData()
        formData.append("file", avatarFile)
        formData.append("type", "avatar")

        const uploadResponse = await fetch("/api/upload", {
          method: "POST",
          body: formData,
        })

        if (!uploadResponse.ok) {
          const errorData = await uploadResponse.json()
          throw new Error(errorData.message || errorData.error || "Nahrání avataru selhalo")
        }

        const uploadResult = await uploadResponse.json()
        avatarUrl = uploadResult.url
      }

      // Update profile
      const response = await fetch("/api/profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          full_name: fullName,
          avatar_url: avatarUrl,
        }),
      })

      if (!response.ok) {
        throw new Error("Aktualizace profilu selhala")
      }

      toast({
        title: "Profil aktualizován",
        description: "Váš profil byl úspěšně aktualizován",
      })

      router.push("/dashboard")
      router.refresh()
    } catch (error) {
      console.error("Error updating profile:", error)
      toast({
        title: "Chyba při aktualizaci",
        description: error instanceof Error ? error.message : "Aktualizace profilu selhala. Zkuste to prosím znovu.",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Avatar Section */}
      <div className="flex flex-col items-center space-y-4">
        <div className="relative">
          <Avatar className="w-24 h-24">
            <AvatarImage src={avatarPreview || "/placeholder.svg"} alt="Profile picture" />
            <AvatarFallback className="text-lg">{fullName ? fullName.charAt(0).toUpperCase() : "U"}</AvatarFallback>
          </Avatar>
          <label
            htmlFor="avatar-upload"
            className="absolute bottom-0 right-0 bg-blue-600 text-white p-2 rounded-full cursor-pointer hover:bg-blue-700 transition-colors"
          >
            <Camera className="w-4 h-4" />
          </label>
          <input 
            id="avatar-upload" 
            type="file" 
            accept="image/jpeg,image/jpg,image/png,image/gif,image/webp" 
            onChange={handleAvatarChange} 
            className="hidden" 
          />
        </div>
        <div className="text-center">
          <p className="text-sm text-slate-600">Klikněte na ikonu fotoaparátu pro změnu profilového obrázku</p>
          <p className="text-xs text-slate-500">JPG, PNG, GIF, WEBP • 50 KB - 10 MB</p>
          {validationError && (
            <div className="flex items-center justify-center gap-1 mt-2 text-red-600">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm">{validationError}</span>
            </div>
          )}
        </div>
      </div>

      {/* Full Name */}
      <div className="space-y-2">
        <Label htmlFor="fullName">Celé jméno</Label>
        <Input
          id="fullName"
          type="text"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          placeholder="Zadejte vaše celé jméno"
          required
        />
      </div>

      {/* Email (read-only) */}
      <div className="space-y-2">
        <Label htmlFor="email">E-mail</Label>
        <Input id="email" type="email" value={profile.email || ""} disabled className="bg-slate-50" />
        <p className="text-sm text-slate-500">E-mail nelze změnit</p>
      </div>

      {/* Admin Badge */}
      {profile.admin && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
          <p className="text-amber-800 font-medium">🛡️ Účet administrátora</p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-4 pt-4">
        <Button type="button" variant="outline" onClick={() => router.back()} className="flex-1">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Zrušit
        </Button>
        <Button 
          type="submit" 
          disabled={isLoading || !!validationError} 
          className="flex-1 bg-blue-600 hover:bg-blue-700"
        >
          <Save className="w-4 h-4 mr-2" />
          {isLoading ? "Ukládám..." : "Uložit změny"}
        </Button>
      </div>
    </form>
  )
}
