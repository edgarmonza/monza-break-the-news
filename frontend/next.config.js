/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['www.eltiempo.com', 'www.elespectador.com', 'www.semana.com'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
