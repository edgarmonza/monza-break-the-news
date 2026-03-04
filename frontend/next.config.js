/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { hostname: 'www.eltiempo.com' },
      { hostname: 'www.elespectador.com' },
      { hostname: 'www.semana.com' },
      { hostname: 'images.unsplash.com' },
    ],
  },
  turbopack: {
    root: __dirname,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
