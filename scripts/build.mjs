import { cp, mkdir, rm } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const output = resolve(root, "dist");
const files = [
  ".nojekyll",
  "app.js",
  "index.html",
  "googlea84be0f3728abaf3.html",
  "site-config.js",
  "styles.css",
];

await rm(output, { recursive: true, force: true });
await mkdir(output, { recursive: true });

await Promise.all(
  files.map((file) => cp(resolve(root, file), resolve(output, file))),
);
await cp(resolve(root, "assets"), resolve(output, "assets"), {
  recursive: true,
});

console.log(`Prepared GitHub Pages artifact in ${output}`);
