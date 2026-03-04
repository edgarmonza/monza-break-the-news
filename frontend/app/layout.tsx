import type { Metadata, Viewport } from "next";
import { Inter, Syne } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
  weight: ["300", "400", "500", "600", "700"],
});

const syne = Syne({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-syne",
  weight: ["400", "500", "600", "700", "800"],
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export const metadata: Metadata = {
  title: "Plural — Noticias de Latinoamérica",
  description: "La plataforma donde los latinos encuentran toda la información. Noticias de diferentes fuentes, temas y países, todo en español.",
  keywords: ["noticias", "latinoamérica", "latino", "ia", "inteligencia artificial", "threads", "español"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className={`${inter.variable} ${syne.variable}`}>
      <body className="antialiased font-sans">
        {/* SVG noise filter for paper grain texture */}
        <svg className="absolute w-0 h-0" aria-hidden="true">
          <defs>
            <filter id="paper-grain" x="0%" y="0%" width="100%" height="100%">
              <feTurbulence
                type="fractalNoise"
                baseFrequency="0.65"
                numOctaves="6"
                stitchTiles="stitch"
                result="noise"
              />
              <feColorMatrix
                type="saturate"
                values="0"
                in="noise"
                result="gray-noise"
              />
            </filter>
          </defs>
        </svg>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
