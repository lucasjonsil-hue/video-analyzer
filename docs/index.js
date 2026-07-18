/**
 * DRAFT — scan-and-index script for the Inventory Viewer.
 * Written by Claude (chat), not yet tested against the real notes folder.
 * Claude Code: verify against actual note format/frontmatter and improve/replace as needed.
 *
 * Usage: node index.js
 * Output: index.json — { category: [ {title, filepath, date, creator, flagged} ] }
 */

const fs = require('fs');
const path = require('path');

// TODO: confirm this is the real notes directory
const NOTES_DIR = path.join(__dirname, 'notes');
const OUTPUT_FILE = path.join(__dirname, 'index.json');

function parseFrontmatter(content) {
  // Very simple frontmatter parser — expects:
  // ---
  // title: ...
  // date: ...
  // creator: ...
  // source: ...
  // flagged: true/false
  // ---
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  const meta = {};
  if (match) {
    match[1].split('\n').forEach(line => {
      const idx = line.indexOf(':');
      if (idx > -1) {
        const key = line.slice(0, idx).trim();
        const value = line.slice(idx + 1).trim();
        meta[key] = value;
      }
    });
  }
  return meta;
}

function scanNotes(dir) {
  const index = {};

  if (!fs.existsSync(dir)) {
    console.error(`Notes directory not found: ${dir}`);
    return index;
  }

  const categories = fs.readdirSync(dir, { withFileTypes: true })
    .filter(entry => entry.isDirectory())
    .map(entry => entry.name);

  for (const category of categories) {
    const categoryPath = path.join(dir, category);
    const files = fs.readdirSync(categoryPath)
      .filter(f => f.endsWith('.md'));

    index[category] = files.map(file => {
      const filepath = path.join(categoryPath, file);
      const content = fs.readFileSync(filepath, 'utf-8');
      const meta = parseFrontmatter(content);

      return {
        title: meta.title || file.replace('.md', ''),
        filepath: path.relative(dir, filepath),
        date: meta.date || null,
        creator: meta.creator || null,     // TODO: confirm field name once we check what Video Analyzer captures
        source: meta.source || null,       // original video/link URL
        flagged: meta.flagged === 'true',  // for the fact-check feature
      };
    });
  }

  return index;
}

const result = scanNotes(NOTES_DIR);
fs.writeFileSync(OUTPUT_FILE, JSON.stringify(result, null, 2));
console.log(`Indexed ${Object.keys(result).length} categories -> ${OUTPUT_FILE}`);
