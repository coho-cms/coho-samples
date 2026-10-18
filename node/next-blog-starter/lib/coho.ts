import 'server-only';
import { configFromEnv } from '@coho-cms/delivery';
import { createCoho } from '@your-org/blog-content';

/**
 * The site's Coho client, for server components only.
 *
 * What it reads, and with which credential, comes from the environment, not the code:
 * with a preview token it reads dev or a branch, live; with a delivery key, released
 * content. Set them in .env.local.
 */
export const coho = createCoho(configFromEnv(process.env));

// The rest of the site imports the library through this file, so if yours has
// another name than @your-org/blog-content, this file is the only one to change.
export { isResolved } from '@your-org/blog-content';
export type { BlogPost, Tag, TeamMember } from '@your-org/blog-content';
