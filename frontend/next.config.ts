import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  images: {
    unoptimized: true,
  },
  // Ensure standalone output includes all necessary files
  outputFileTracingIncludes: {
    '/': ['./**/*'],
  },
};

export default nextConfig;
