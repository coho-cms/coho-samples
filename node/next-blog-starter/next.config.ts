import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  experimental: {
    // `npm install ../blog-content` links your content library into node_modules, and
    // Turbopack follows a link out of this folder only into a root it is given. If your
    // library is somewhere else, change the path; once it comes from a registry, remove this.
    turbopackAdditionalRoots: {
      contentLibrary: { path: '../blog-content' },
    },
  },
};

export default nextConfig;
