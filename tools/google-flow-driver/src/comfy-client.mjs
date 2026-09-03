import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { WebSocket } from 'ws';

export class ComfyClient {
  constructor(serverUrl = 'http://127.0.0.1:8188') {
    this.serverUrl = serverUrl;
    this.wsUrl = serverUrl.replace(/^http/, 'ws');
  }

  async isHealthy() {
    try {
      const resp = await fetch(`${this.serverUrl}/system_stats`);
      return resp.ok;
    } catch {
      return false;
    }
  }

  async queuePrompt(workflow, clientId = null) {
    const cid = clientId || crypto.randomUUID();
    const payload = {
      prompt: workflow,
      client_id: cid,
    };

    const resp = await fetch(`${this.serverUrl}/prompt`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!resp.ok) {
      const errorText = await resp.text();
      throw new Error(`ComfyUI prompt submission failed (${resp.status}): ${errorText}`);
    }

    const data = await resp.json();
    return { promptId: data.prompt_id, clientId: cid };
  }

  async waitForCompletion(promptId, clientId, timeoutMs = 180000) {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(`${this.wsUrl}/ws?clientId=${clientId}`);
      const timer = setTimeout(() => {
        ws.close();
        reject(new Error(`ComfyUI job ${promptId} timed out after ${timeoutMs}ms.`));
      }, timeoutMs);

      ws.on('message', async (data) => {
        try {
          const msg = JSON.parse(data.toString());
          if (msg.type === 'execution_error' && msg.data?.prompt_id === promptId) {
            clearTimeout(timer);
            ws.close();
            reject(new Error(`ComfyUI execution error: ${JSON.stringify(msg.data)}`));
          }

          if (msg.type === 'executing' && msg.data?.node === null && msg.data?.prompt_id === promptId) {
            clearTimeout(timer);
            ws.close();

            // Fetch history to get output filenames
            const historyResp = await fetch(`${this.serverUrl}/history/${promptId}`);
            const history = await historyResp.json();
            resolve(history[promptId] || {});
          }
        } catch {}
      });

      ws.on('error', (err) => {
        clearTimeout(timer);
        reject(err);
      });
    });
  }

  async downloadOutput(filename, subfolder = '', type = 'output', targetPath) {
    const url = `${this.serverUrl}/view?filename=${encodeURIComponent(filename)}&subfolder=${encodeURIComponent(subfolder)}&type=${encodeURIComponent(type)}`;
    const resp = await fetch(url);
    if (!resp.ok) {
      throw new Error(`Failed to download ComfyUI output ${filename}: ${resp.statusText}`);
    }

    const arrayBuf = await resp.arrayBuffer();
    fs.mkdirSync(path.dirname(targetPath), { recursive: true });
    fs.writeFileSync(targetPath, Buffer.from(arrayBuf));
    return targetPath;
  }
}
