// Post-build: copy non-TS files to dist/
const fs = require("fs");
const path = require("path");

const src = path.join(__dirname, "src");
const dist = path.join(__dirname, "dist");

function copyRecursive(srcDir, destDir, extensions) {
  if (!fs.existsSync(destDir)) fs.mkdirSync(destDir, { recursive: true });
  for (const entry of fs.readdirSync(srcDir, { withFileTypes: true })) {
    const srcPath = path.join(srcDir, entry.name);
    const destPath = path.join(destDir, entry.name);
    if (entry.isDirectory()) {
      copyRecursive(srcPath, destPath, extensions);
    } else if (extensions.some((ext) => entry.name.endsWith(ext))) {
      fs.copyFileSync(srcPath, destPath);
      console.log(`Copied: ${destPath}`);
    }
  }
}

// Copy HTML, CSS, JSON, PNG files
copyRecursive(src, dist, [".html", ".css", ".json", ".png"]);
console.log("Build complete!");
