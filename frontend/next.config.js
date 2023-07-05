/**
 * @type {import('next').NextConfig}
 */
const nextConfig = {
  output: 'export',
  distDir: 'dist',
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
  webpack: (config, { isServer }) => {
    if (isServer) {
      config.node = {
        __dirname: true,
      };
    }

    return config;
  },
};

module.exports = nextConfig;
