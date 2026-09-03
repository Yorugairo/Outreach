#!/usr/bin/env node
/**
 * 2026 Agentic Harness Stamping & Replication Tool
 * 
 * Stamps the complete agentic engineering harness (skills, rules, subagents,
 * AST-grep structural gates, deterministic evals, and memory) onto any target repo.
 * 
 * Usage:
 *   node scripts/harness-stamp.mjs --target <path-to-repo> [--profile full|web|video|api] [--dry-run]
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SOURCE_ROOT = path.resolve(__dirname, '..');

const PROFILES = {
  full: {
    name: 'Full 2026 Agentic Stack',
    description: 'All 33 curated skills, full subagent library, AST-grep gates, and 5-journey evals bench.',
    skills: null // all
  },
  web: {
    name: 'Web & SaaS Stack',
    description: 'TypeScript, Next.js, Supabase, Design Engine, Content Engine, Deep Grilling, AST-grep.',
    skills: [
      'clean-code-guard', 'content-engine', 'council', 'design-engine', 'diagnosing-bugs',
      'e2e-testing', 'exa-search', 'grill-me', 'grilling', 'market-research', 'marketing-campaign',
      'motion-system', 'registry-core', 'research', 'seo-engine', 'social-distribution',
      'supabase', 'supabase-postgres-best-practices', 'taste', 'tavily-web', 'article-writing',
      'brand-discovery', 'brand-voice'
    ]
  },
  video: {
    name: 'Video Engine & Motion Graphics Stack',
    description: 'Remotion, Google Flow driver, VideoDB, Motion System, Evidence Motion, Taste, Deep Grilling.',
    skills: [
      'asset-claim-and-quarantine', 'blender-motion-state-inspection', 'clean-code-guard',
      'content-engine', 'council', 'design-engine', 'diagnosing-bugs', 'e2e-testing',
      'evidence-motion-engine', 'exa-search', 'fal-ai-media', 'frontend-slides', 'grill-me',
      'grilling', 'manim-video', 'marketing-campaign', 'motion-system', 'remotion-video-creation',
      'research', 'social-distribution', 'taste', 'tavily-web', 'ui-demo', 'video-editing',
      'video-engine', 'video-script-architect', 'videodb', 'brand-voice'
    ]
  },
  api: {
    name: 'Backend & API Stack',
    description: 'Clean Code, Supabase, Database optimization, E2E Testing, Deep Grilling, Subagent Research.',
    skills: [
      'clean-code-guard', 'council', 'diagnosing-bugs', 'e2e-testing', 'exa-search',
      'grill-me', 'grilling', 'market-research', 'research', 'supabase',
      'supabase-postgres-best-practices', 'tavily-web'
    ]
  }
};

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    target: null,
    profile: 'full',
    dryRun: false,
    help: false
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--target' || arg === '-t') {
      options.target = args[++i];
    } else if (arg === '--profile' || arg === '-p') {
      options.profile = args[++i] || 'full';
    } else if (arg === '--dry-run') {
      options.dryRun = true;
    } else if (arg === '--help' || arg === '-h') {
      options.help = true;
    }
  }

  return options;
}

function showHelp() {
  console.log(`
🏛️  2026 Agentic Harness Stamping Tool

Usage:
  node scripts/harness-stamp.mjs --target <path> [options]

Options:
  --target, -t <path>       Destination repository root (Required)
  --profile, -p <profile>   Profile to deploy: full | web | video | api (Default: full)
  --dry-run                 Preview actions without copying files
  --help, -h                Show this help message

Available Profiles:
  full   - All 33 skills, full subagent library, AST-grep gates, and evals suite.
  web    - Web, Next.js, Supabase, Design, Content, and SEO profile.
  video  - Remotion, Google Flow driver, VideoDB, Motion System, and Taste profile.
  api    - Minimal Backend, DB, Clean Code, and Subagent Research profile.
`);
}

function copyDirRecursive(src, dest, filterFn = null, isDryRun = false) {
  if (!fs.existsSync(src)) return 0;
  if (!isDryRun && !fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }

  let count = 0;
  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (filterFn && !filterFn(entry.name, srcPath, entry.isDirectory())) {
      continue;
    }

    if (entry.isDirectory()) {
      count += copyDirRecursive(srcPath, destPath, null, isDryRun);
    } else {
      if (!isDryRun) {
        fs.copyFileSync(srcPath, destPath);
      }
      count++;
    }
  }

  return count;
}

async function main() {
  const options = parseArgs();

  if (options.help || !options.target) {
    showHelp();
    process.exit(options.help ? 0 : 1);
  }

  const targetRoot = path.resolve(options.target);
  const profileKey = options.profile.toLowerCase();
  const profile = PROFILES[profileKey];

  if (!profile) {
    console.error(`❌ Error: Unknown profile "${options.profile}". Available: ${Object.keys(PROFILES).join(', ')}`);
    process.exit(1);
  }

  console.log(`\n=================================================================`);
  console.log(`🏛️  Stamping 2026 Agentic Harness`);
  console.log(`=================================================================`);
  console.log(`📍 Source:      ${SOURCE_ROOT}`);
  console.log(`🎯 Destination: ${targetRoot}`);
  console.log(`📦 Profile:     ${profile.name} (${profileKey})`);
  console.log(`🔍 Dry Run:     ${options.dryRun ? 'YES (No changes will be written)' : 'NO (Applying changes)'}`);
  console.log(`-----------------------------------------------------------------\n`);

  if (!options.dryRun && !fs.existsSync(targetRoot)) {
    fs.mkdirSync(targetRoot, { recursive: true });
  }

  // 1. Copy .agents/rules
  console.log(`[1/6] Stamping .agents/rules/...`);
  const rulesCount = copyDirRecursive(
    path.join(SOURCE_ROOT, '.agents/rules'),
    path.join(targetRoot, '.agents/rules'),
    null,
    options.dryRun
  );
  console.log(`      └─ Copied ${rulesCount} rule files.`);

  // 2. Copy .agents/agents (subagent definitions)
  console.log(`[2/6] Stamping .agents/agents/ (subagent library)...`);
  const agentsCount = copyDirRecursive(
    path.join(SOURCE_ROOT, '.agents/agents'),
    path.join(targetRoot, '.agents/agents'),
    null,
    options.dryRun
  );
  console.log(`      └─ Copied ${agentsCount} subagent definitions.`);

  // 3. Copy .agents/skills filtered by profile
  console.log(`[3/6] Stamping .agents/skills/ (profile: ${profileKey})...`);
  const skillsFilter = (name, fullPath, isDir) => {
    if (!profile.skills) return true; // full profile
    return profile.skills.includes(name);
  };

  const skillsCount = copyDirRecursive(
    path.join(SOURCE_ROOT, '.agents/skills'),
    path.join(targetRoot, '.agents/skills'),
    skillsFilter,
    options.dryRun
  );
  console.log(`      └─ Copied ${skillsCount} files across active skills.`);

  // 4. Copy sgconfig.yml and .ast-grep/rules/
  console.log(`[4/6] Stamping AST-Grep structural quality gates...`);
  if (!options.dryRun) {
    const sgConfigSrc = path.join(SOURCE_ROOT, 'sgconfig.yml');
    if (fs.existsSync(sgConfigSrc)) {
      fs.copyFileSync(sgConfigSrc, path.join(targetRoot, 'sgconfig.yml'));
    }
  }
  const astRulesCount = copyDirRecursive(
    path.join(SOURCE_ROOT, '.ast-grep/rules'),
    path.join(targetRoot, '.ast-grep/rules'),
    null,
    options.dryRun
  );
  console.log(`      └─ Copied sgconfig.yml and ${astRulesCount} AST-grep rules.`);

  // 5. Copy evals/ benchmark suite
  console.log(`[5/6] Stamping deterministic evals/ benchmark harness...`);
  const evalsCount = copyDirRecursive(
    path.join(SOURCE_ROOT, 'evals'),
    path.join(targetRoot, 'evals'),
    null,
    options.dryRun
  );
  console.log(`      └─ Copied ${evalsCount} eval harness files.`);

  // 6. Scaffold .claude/memory.md and package.json scripts
  console.log(`[6/6] Configuring project memory and package scripts...`);
  if (!options.dryRun) {
    // Scaffold .claude/memory.md if not exists
    const claudeDir = path.join(targetRoot, '.claude');
    if (!fs.existsSync(claudeDir)) fs.mkdirSync(claudeDir, { recursive: true });
    
    const memoryPath = path.join(claudeDir, 'memory.md');
    if (!fs.existsSync(memoryPath)) {
      const projectName = path.basename(targetRoot);
      const initialMemory = `# Project Memory & Architecture Invariants (${projectName})\n\n` +
        `This file preserves durable architectural decisions, operational conventions, and cross-harness contracts for agents working in this repository.\n\n` +
        `---\n\n` +
        `## 1. Project Boundaries & Stack\n` +
        `- **Project Name:** ${projectName}\n` +
        `- **Profile:** ${profile.name}\n\n` +
        `## 2. Multi-Agent Concurrency & Disk-as-Bus Standard\n` +
        `- **Single-Coordinator Writer:** Subagents are strictly read-only on shared state and write markdown findings to \`docs/research/runs/<topic_slug>/\`.\n` +
        `- **Zero Token Bloat:** Subagents return concise 3-bullet summaries over IPC.\n\n` +
        `## 3. Quality & Invariant Gates\n` +
        `- Run \`npm run lint:ast\` for Tree-sitter AST structural invariant verification.\n` +
        `- Run \`npm run test:evals\` to execute the deterministic 5-journey eval harness.\n`;
      fs.writeFileSync(memoryPath, initialMemory, 'utf8');
      console.log(`      └─ Generated .claude/memory.md`);
    }

    // Inject scripts into package.json if it exists
    const pkgPath = path.join(targetRoot, 'package.json');
    if (fs.existsSync(pkgPath)) {
      try {
        const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
        pkg.scripts = pkg.scripts || {};
        pkg.scripts['lint:ast'] = 'npx --package=@ast-grep/cli ast-grep scan';
        pkg.scripts['test:evals'] = 'npx tsx evals/harness-runner.ts';
        fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + '\n', 'utf8');
        console.log(`      └─ Injected "lint:ast" and "test:evals" into package.json`);
      } catch (err) {
        console.log(`      └─ Warning: Could not update package.json: ${err.message}`);
      }
    }
  }

  console.log(`\n=================================================================`);
  console.log(`✅ Stamping Complete! Harness is 100% active in destination.`);
  console.log(`=================================================================`);
  console.log(`Next Verification Step in ${targetRoot}:`);
  console.log(`  npx tsx evals/harness-runner.ts\n`);
}

main().catch(err => {
  console.error('Fatal error during stamping:', err);
  process.exit(1);
});
