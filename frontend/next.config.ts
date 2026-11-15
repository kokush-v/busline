import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "busline-photos-original.s3.us-east-1.amazonaws.com",
      },
    ],
  },
};

export default nextConfig;
