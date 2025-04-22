"use client"
import React from "react"
import localFont from "next/font/local"
import "./globals.css"

const inter = localFont({ 
  src: './fonts/Inter.ttf',
  variable: '--font-inter'
})

export const metadata: Metadata = {
  title: "Financial Dashboard",
  description: "Track your investments, shares, and referrals",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
