"use client"

import { useState } from "react"
import Image from "next/image"
import { Dialog, DialogContent, DialogTrigger, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Maximize2, X } from "lucide-react"
import * as VisuallyHidden from "@radix-ui/react-visually-hidden"

interface FullscreenPosterModalProps {
  imageUrl: string
  title: string
  children?: React.ReactNode
  triggerClassName?: string
}

export default function FullscreenPosterModal({ 
  imageUrl, 
  title, 
  children,
  triggerClassName 
}: FullscreenPosterModalProps) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {children || (
          <Button 
            variant="secondary" 
            size="sm" 
            className={triggerClassName}
          >
            <Maximize2 className="h-4 w-4 mr-2" />
            Celá obrazovka
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-[95vw] max-h-[95vh] p-0 bg-black border-none">
        <VisuallyHidden.Root>
          <DialogTitle>Zobrazení plakátu: {title}</DialogTitle>
        </VisuallyHidden.Root>
        <div className="relative w-full h-[95vh] flex items-center justify-center">
          {/* Close button */}
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-4 right-4 z-50 bg-black/50 hover:bg-black/70 text-white"
            onClick={() => setIsOpen(false)}
          >
            <X className="h-6 w-6" />
            <span className="sr-only">Zavřít</span>
          </Button>
          
          {/* Image */}
          <div className="relative w-full h-full">
            <Image
              src={imageUrl || "/placeholder.svg"}
              alt={title}
              fill
              className="object-contain"
              priority
              sizes="95vw"
            />
          </div>
          
          {/* Title overlay */}
          <div className="absolute bottom-4 left-4 right-4 bg-black/50 text-white p-4 rounded-lg">
            <h3 className="text-lg font-semibold truncate">{title}</h3>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
