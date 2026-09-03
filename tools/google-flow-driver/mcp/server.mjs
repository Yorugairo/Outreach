import path from 'node:path';
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
    name: 'create_flow_video',
    description: 'Generate a cinematic video using Google Flow via active Chrome CDP. BEST FOR: Cinematic character hooks, multi-shot narrative scenes, complex physical motion, and 3-reference visual fidelity. FORBIDDEN FOR: Readable financial charts, stat cards, statutory text, or data tables (diffusion hallucinates numbers and mushes text; use Remotion/SVG instead). Supports multi-reference conditioning, explicit or preserved aspect ratio (9:16 or 16:9), and optional FFmpeg reversal for pixel-exact ending-frame handoffs.',
    inputSchema: {
      type: 'object',
      properties: {
        prompt: {
          type: 'string',
          description: 'The video generation prompt description and style instructions.'
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
          description: 'Absolute output file path where the resulting MP4 video will be saved.'
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

    if (name === 'create_flow_video') {

      const result = await engine.generateVideo(args || {});
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
      const flowTabs = pages.filter(u => u.includes('labs.google/fx/tools/flow'));
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
