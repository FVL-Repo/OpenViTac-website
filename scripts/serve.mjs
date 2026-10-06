import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { dirname, extname, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const port = Number(process.env.PORT || 4173);
const types = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".webp": "image/webp",
  ".woff2": "font/woff2",
  ".mp4": "video/mp4",
  ".webm": "video/webm",
  ".vtt": "text/vtt; charset=utf-8",
  ".pdf": "application/pdf",
};

createServer(async (request, response) => {
  try {
    const pathname = decodeURIComponent(
      new URL(request.url, "http://localhost").pathname,
    );
    const file = resolve(
      root,
      `.${pathname.endsWith("/") ? `${pathname}index.html` : pathname}`,
    );
    const relative = file.slice(root.length + 1);
    if (
      !file.startsWith(root + sep) ||
      relative.split(/[\\/]/).some((part) => part.startsWith(".")) ||
      !types[extname(file)]
    ) {
      response.writeHead(403);
      response.end("Forbidden");
      return;
    }
    const data = await readFile(file);
    const headers = {
      "Content-Type": types[extname(file)],
      "Cache-Control": "no-cache",
      "X-Content-Type-Options": "nosniff",
      "Accept-Ranges": "bytes",
    };
    const range = request.headers.range?.match(/^bytes=(\d+)-(\d*)$/);
    if (range) {
      const start = Number(range[1]);
      const end = Math.min(
        range[2] ? Number(range[2]) : data.length - 1,
        data.length - 1,
      );
      if (start > end || start >= data.length) {
        response.writeHead(416, { "Content-Range": `bytes */${data.length}` });
        response.end();
        return;
      }
      response.writeHead(206, {
        ...headers,
        "Content-Range": `bytes ${start}-${end}/${data.length}`,
        "Content-Length": end - start + 1,
      });
      response.end(
        request.method === "HEAD" ? undefined : data.subarray(start, end + 1),
      );
      return;
    }
    response.writeHead(200, { ...headers, "Content-Length": data.length });
    response.end(request.method === "HEAD" ? undefined : data);
  } catch {
    response.writeHead(404);
    response.end("Not found");
  }
}).listen(port, "127.0.0.1", () =>
  console.log(`OpenViTac preview: http://127.0.0.1:${port}`),
);
