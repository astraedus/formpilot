/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "8003",
        pathname: "/uploads/**",
      },
    ],
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8003/api/:path*",
      },
      {
        source: "/uploads/:path*",
        destination: "http://localhost:8003/uploads/:path*",
      },
    ];
  },
};

export default nextConfig;
