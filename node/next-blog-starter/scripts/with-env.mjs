// Runs a Next.js command with the variables in an env file, such as
// `node scripts/with-env.mjs .env.prod build`.
//
// Next.js reads only the env files it knows by name, so this loads another one first.
// A variable already set wins over the file, and Next.js never replaces one that is set,
// so the file's values also win over Next.js's own .env.local.
//
// Not `node --env-file`: Next.js passes the flags it was started with on to its build
// workers through NODE_OPTIONS, where Node does not allow that one.
import { spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';

const [file, ...args] = process.argv.slice(2);
process.loadEnvFile(file);

const next = createRequire(import.meta.url).resolve('next/dist/bin/next');
const { status } = spawnSync(process.execPath, [next, ...args], { stdio: 'inherit' });
process.exit(status ?? 1);
