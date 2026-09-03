#!/usr/bin/env node
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { pathToFileURL } from 'node:url';
import { createQueue } from '../shared/queue.mjs';
import { MCP_TOOL_DEFINITIONS, makeToolHandlers } from './tools.mjs';

const SDK_ERROR_MESSAGE = 'Missing MCP SDK module';
const here = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(process.cwd());
const SDK_ROOT = path.join(projectRoot, '.codex', 'mcp-runtime', 'google-ai-mode-mcp', 'node_modules', '@modelcontextprotocol', 'sdk', 'dist', 'esm');

async function loadSdkModule(relativePath, packageFallback) {
  try {
    return await import(pathToFileURL(path.join(SDK_ROOT, relativePath)).href);
  } catch (error) {
    if (relativePath) {
      return import(packageFallback);
    }
    throw error;
  }
}

const sdkServer = await loadSdkModule(path.join('server', 'index.js'), '@modelcontextprotocol/sdk/server/index.js');
const sdkStdio = await loadSdkModule(path.join('server', 'stdio.js'), '@modelcontextprotocol/sdk/server/stdio.js');
const sdkTypes = await loadSdkModule('types.js', '@modelcontextprotocol/sdk/types.js');
if (!sdkServer?.Server || !sdkStdio?.StdioServerTransport || !sdkTypes?.CallToolRequestSchema) {
  throw new Error(SDK_ERROR_MESSAGE);
}

const { Server } = sdkServer;
const { StdioServerTransport } = sdkStdio;
const {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} = sdkTypes;

const runtimeRoot = path.join(projectRoot, '.codex', 'flow-runtime');
const queue = createQueue({ runtimeRoot, projectRoot });
const handlers = makeToolHandlers({ queue, projectRoot });

const server = new Server(
  { name: 'google-flow-driver-mcp', version: '1.0.0' },
  { capabilities: { tools: {} } },
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: MCP_TOOL_DEFINITIONS,
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const name = request.params?.name;
  const args = request.params?.arguments ?? {};
  const handler = handlers[name];

  if (!handler) {
    throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
  }

  try {
    const result = await handler(args);
    return {
      content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
    };
  } catch (error) {
    if (error instanceof McpError) {
      throw error;
    }
    const code = error?.code || 'google_flow_driver_error';
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          ok: false,
          provider: 'google_flow',
          code: String(code),
          error: error?.message || String(error),
        }, null, 2),
      }],
      isError: true,
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
