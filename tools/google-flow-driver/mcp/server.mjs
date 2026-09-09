import fs from 'node:fs';
import path from 'node:path';

// Stdio safety: MCP JSON-RPC protocol requires stdout to only carry JSON.
// Redirect console.* to stderr and a local logfile so debug output never corrupts JSON-RPC stdout.
const logFile = path.resolve('C:/Users/Snipe/Downloads/Outreach Program/tools/google-flow-driver/runtime/flow-mcp.log');
try { fs.mkdirSync(path.dirname(logFile), { recursive: true }); } catch {}

function safeLog(prefix, ...args) {
  const line = `[${new Date().toISOString()}] [${prefix}] ` + args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' ') + '\n';
  process.stderr.write(line);
  try { fs.appendFileSync(logFile, line); } catch {}
}

console.log = (...args) => safeLog('LOG', ...args);
console.info = (...args) => safeLog('INFO', ...args);
console.warn = (...args) => safeLog('WARN', ...args);
console.error = (...args) => safeLog('ERROR', ...args);

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { FlowDagEngine } from '../src/dag-engine.mjs';
import { generateParallaxVideo } from '../src/parallax-runner.mjs';

const engine = new FlowDagEngine();

const server = new Server(
  { name: 'google-flow-driver', version: '2.0.0' },
  { capabilities: { tools: {} } }
);

const TOOLS = [
  {
    name: 'create_flow_image',
    description: 'Generate a high-fidelity 2.5D still plate using Google Flow (Nano Banana Pro) via active Chrome CDP. BEST FOR: Background plates, character staging plates, cut-in objects, and editorial scenes for 2.5D parallax and Remotion compositing. Supports native character binding (e.g. references: ["Mike"]) and disk image references. Aspect ratio is configurable (9:16 or 16:9).',
    inputSchema: {
      type: 'object',
      properties: {
        prompt: {
          type: 'string',
          description: 'The image generation prompt description and style instructions.'
        },
        references: {
          type: 'array',
          items: { type: 'string' },
          description: 'Optional array of references (absolute file paths to images or project character names like "Mike").'
        },
        ratio: {
          type: 'string',
          enum: ['9:16', '16:9'],
          description: 'Aspect ratio: "9:16" for vertical or "16:9" for horizontal (defaults to "9:16").'
        },
        outputPath: {
          type: 'string',
          description: 'Absolute output file path where the resulting PNG image will be saved.'
        },
        projectUrl: {
          type: 'string',
          description: 'Optional specific Google Flow project URL to navigate to.'
        }
      },
      required: ['prompt', 'outputPath']
    }
  },
  {
    name: 'get_flow_project',
    description: 'Inspect the active Google Flow project canvas. Returns project title, canvas aspect ratio, registered character names (e.g. ["Mike"]), active model, and media assets.',
    inputSchema: {
      type: 'object',
      properties: {
        projectUrl: {
          type: 'string',
          description: 'Optional specific Google Flow project URL to inspect.'
        }
      }
    }
  },
  {
    name: 'create_flow_video',
    description: 'Generate a cinematic video using Google Flow via active Chrome CDP. BEST FOR: Cinematic character hooks, multi-shot narrative scenes, complex physical motion, and 3-reference visual fidelity. FORBIDDEN FOR: Readable financial charts, stat cards, statutory text, or data tables (diffusion hallucinates numbers and mushes text; use Remotion/SVG instead). Supports multi-reference conditioning, explicit or preserved aspect ratio (9:16 or 16:9), and optional FFmpeg reversal for pixel-exact ending-frame handoffs.',
    inputSchema: {
      type: 'object',
      properties: {
        prompt: {
          type: 'string',
          description: 'The video generation prompt description and style instructions.'
        },
        startFrame: {
          type: 'string',
          description: 'Start frame asset name or query in project library for continuous two-point interpolation.'
        },
        endFrame: {
          type: 'string',
          description: 'End frame asset name or query in project library for continuous two-point interpolation.'
        },
        character: {
          type: 'string',
          description: 'Character reference chip name (e.g. "HollowStickMike").'
        },
        references: {
          type: 'array',
          items: { type: 'string' },
          description: 'Optional array of absolute file paths to image references (up to 3).'
        },
        ratio: {
          type: 'string',
          enum: ['9:16', '16:9'],
          description: 'Aspect ratio. Omit or set to null to preserve existing project canvas ratio. Set to "9:16" for vertical or "16:9" for horizontal.'
        },
        duration: {
          type: 'number',
          enum: [4, 6, 8],
          description: 'Duration in seconds (e.g. 6). Defaults to project setting if omitted.'
        },
        resolution: {
          type: 'string',
          enum: ['720p', '1080p'],
          description: 'Resolution. Defaults to project setting if omitted.'
        },
        reverse: {
          type: 'boolean',
          description: 'If true, applies FFmpeg -vf reverse so the video motion ends on the primary reference frame.'
        },
        outputPath: {
          type: 'string',
          description: 'Optional output file path where the resulting MP4 video will be saved if synchronous render is used.'
        },
        projectUrl: {
          type: 'string',
          description: 'Optional specific Google Flow project URL to navigate to.'
        }
      },
      required: ['prompt']
    }
  },
  {
    name: 'get_flow_canvas',
    description: 'Inspect the real-time state of the Google Flow canvas and generation queue. Returns isGenerating (boolean), progress percentage (e.g. "45%"), composer state (pinned triggers and chips), and visible library assets (<200 tokens).',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  },
  {
    name: 'download_flow_video',
    description: 'Download the newest generated scene video from the Google Flow canvas to a target path and automatically extract verification frames via FFmpeg.',
    inputSchema: {
      type: 'object',
      properties: {
        outputPath: {
          type: 'string',
          description: 'Absolute output file path where the resulting MP4 video will be saved.'
        },
        extractFrames: {
          type: 'boolean',
          description: 'Whether to extract 1 fps verification frames to <outputPath>-frames directory (default: true).'
        }
      },
      required: ['outputPath']
    }
  },
  {
    name: 'create_flow_batch',
    description: 'Execute a sequential DAG batch of video scenes in Google Flow with optional shot-to-shot frame chaining (Shot 2 conditions on end frame of Shot 1).',
    inputSchema: {
      type: 'object',
      properties: {
        scenes: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              id: { type: 'string' },
            mode: { type: 'string', enum: ['video', 'image'], description: 'Always set. Default video.' },
            submode: { type: 'string', enum: ['ingredients', 'frames'] },
            model: { type: 'string', description: "Exact model label as Flow shows it, e.g. 'Omni 1.1 Flash'." },
            count: { type: 'number', enum: [1, 2, 3, 4], description: 'Outputs per generation; credits scale with it.' },
            maxCredits: { type: 'number', description: 'Refuse the scene if Flow quotes more than this.' },
              prompt: { type: 'string' },
              references: { type: 'array', items: { type: 'string' } },
              chain_from_previous: {
                type: 'boolean',
                description: 'If true, prepends the previous scene end-frame PNG to this scene references.'
              },
              ratio: { type: 'string', enum: ['9:16', '16:9'] },
              duration: { type: 'number', enum: [4, 6, 8] },
              reverse: { type: 'boolean' }
            },
            required: ['prompt']
          },
          description: 'Array of scene objects to generate sequentially.'
        },
        outputDir: {
          type: 'string',
          description: 'Absolute output directory where all scene videos and metadata will be saved.'
        },
        mode: { type: 'string', enum: ['video', 'image'], description: 'Batch default. Always set; default video. The driver reads the state back and refuses to submit on mismatch.' },
        submode: { type: 'string', enum: ['ingredients', 'frames'] },
        model: { type: 'string', description: "Batch default model label exactly as Flow shows it, e.g. 'Omni 1.1 Flash'." },
        count: { type: 'number', enum: [1, 2, 3, 4], description: 'Outputs per generation; credits scale with it.' },
        maxCredits: { type: 'number', description: 'Per-scene credit ceiling read from the "Generating will use N credits" line before submit.' },
        ratio: {
          type: 'string',
          enum: ['9:16', '16:9'],
          description: 'Default aspect ratio for all scenes if not specified per-scene.'
        },
        projectUrl: {
          type: 'string',
          description: 'Optional specific Google Flow project URL.'
        }
      },
      required: ['scenes', 'outputDir']
    }
  },
  {
    name: 'get_flow_status',
    description: 'Check connectivity to Chrome CDP on port 9222 and inspect open Google Flow tabs.',
    inputSchema: {
      type: 'object',
      properties: {
        projectUrl: {
          type: 'string',
          description: 'Optional Google Flow project URL to verify.'
        }
      }
    }
  },
  {
    name: 'create_comfy_parallax_video',
    description: 'Generate an instant, zero-hallucination 2.5D parallax video from a still image using local GPU (Depth Anything v2 + Depthflow) via ComfyUI. BEST FOR: Editorial illustrations, book plates, paper art, diagrams, floor plans, and architectural layouts needing genuine 3D camera depth without AI geometry drift. FORBIDDEN FOR: Organic fluid dynamics (flowing water/smoke; use LTX-Video) or character facial expressions (looks like stretchy rubber). Trajectories: dolly, zoom, circle, horizontal, vertical, orbital.',
    inputSchema: {
      type: 'object',
      properties: {
        imagePath: {
          type: 'string',
          description: 'Absolute file path to the source still image.'
        },
        motion: {
          type: 'string',
          enum: ['dolly', 'zoom', 'circle', 'horizontal', 'vertical', 'orbital'],
          description: 'Camera motion trajectory. Defaults to "dolly".'
        },
        frames: {
          type: 'number',
          description: 'Number of frames to render (default 30).'
        },
        fps: {
          type: 'number',
          description: 'Frames per second (default 30).'
        },
        strength: {
          type: 'number',
          description: 'Motion displacement strength (default 1.0).'
        },
        outputPath: {
          type: 'string',
          description: 'Absolute output file path where the resulting MP4 video will be saved.'
        }
      },
      required: ['imagePath', 'outputPath']
    }
  }
];

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: TOOLS,
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === 'create_comfy_parallax_video') {
      const result = await generateParallaxVideo({
        inputImagePath: args.imagePath,
        motion: args.motion || 'dolly',
        frames: args.frames || 30,
        fps: args.fps || 30,
        strength: args.strength || 1.0,
        outputVideoPath: args.outputPath
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    }

    if (name === 'create_flow_image') {
      const result = await engine.generateImage(args || {});
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    }

    if (name === 'get_flow_project') {
      const result = await engine.getProjectDetails(args?.projectUrl || null);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    }

    if (name === 'create_flow_video') {
      if (args.startFrame && args.endFrame) {
        const result = await engine.submitInterpolationVideo({
          startFrame: args.startFrame,
          endFrame: args.endFrame,
          character: args.character || 'HollowStickMike',
          prompt: args.prompt
        });
        return {
          content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
        };
      }
      const result = await engine.generateVideo(args || {});
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    }

    if (name === 'get_flow_canvas') {
      const result = await engine.getCanvasState();
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    }

    if (name === 'download_flow_video') {
      const result = await engine.downloadVideo({
        outputPath: args.outputPath,
        extractFrames: args.extractFrames !== false
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    }

    if (name === 'create_flow_batch') {
      const result = await engine.generateBatch(args || {});
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    }

    if (name === 'get_flow_status') {
      const endpoint = await engine.driver.getWsEndpoint();
      const browser = await engine.driver.connect();
      const contexts = browser.contexts();
      const pages = contexts.flatMap(c => c.pages()).map(p => p.url());
      const flowTabs = pages.filter(u => u.includes('labs.google/fx/tools/flow') || u.includes('flow.google.com'));
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            cdpEndpoint: endpoint,
            chromeConnected: true,
            totalTabs: pages.length,
            flowTabsOpen: flowTabs.length,
            flowTabs,
          }, null, 2)
        }]
      };
    }

    throw new Error(`Unknown tool: ${name}`);
  } catch (error) {
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          error: error.message || String(error),
          stack: error.stack,
        }, null, 2)
      }],
      isError: true
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
