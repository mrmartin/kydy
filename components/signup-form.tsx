"use client"

import { useActionState } from "react"
import { useFormStatus } from "react-dom"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2, Vote } from "lucide-react"
import Link from "next/link"
import { signUp } from "@/lib/actions"

function SubmitButton() {
  const { pending } = useFormStatus()

  return (
    <Button type="submit" disabled={pending} className="w-full">
      {pending ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Vytvářím účet...
        </>
      ) : (
        "Vytvořit účet"
      )}
    </Button>
  )
}

export default function SignUpForm() {
  const [state, formAction] = useActionState(signUp, null)

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="text-center">
        <div className="flex justify-center mb-4">
          <Vote className="h-12 w-12 text-primary" />
        </div>
        <CardTitle className="text-2xl font-bold">Připojte se ke komunitě</CardTitle>
        <CardDescription>Vytvořte si účet pro sdílení a diskuzi o politických plakátech</CardDescription>
      </CardHeader>
      <CardContent>
        <form action={formAction} className="space-y-4">
          {state?.error && (
            <div className="bg-destructive/10 border border-destructive/50 text-destructive px-4 py-3 rounded">
              {state.error}
            </div>
          )}

          {state?.success && (
            <div className="bg-green-500/10 border border-green-500/50 text-green-700 px-4 py-3 rounded">
              {state.success}
            </div>
          )}

          <div className="space-y-2">
            <label htmlFor="fullName" className="block text-sm font-medium">
              Celé jméno
            </label>
            <Input id="fullName" name="fullName" type="text" placeholder="Vaše celé jméno" />
          </div>

          <div className="space-y-2">
            <label htmlFor="email" className="block text-sm font-medium">
              E-mail
            </label>
            <Input id="email" name="email" type="email" placeholder="vas@email.cz" required />
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="block text-sm font-medium">
              Heslo
            </label>
            <Input id="password" name="password" type="password" required />
          </div>

          <SubmitButton />

          <div className="text-center text-sm text-muted-foreground">
            Už máte účet?{" "}
            <Link href="/auth/login" className="text-primary hover:underline">
              Přihlaste se
            </Link>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
