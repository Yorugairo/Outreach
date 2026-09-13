---
name: install-permission
description: "Standing permission (2026-09-04) to install OpenCV or anything that improves performance, testing or animation capability - no need to ask; record what was installed and why"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-05T04:22:30.826Z
---

Operator, 2026-09-04: *"you have permission to install opencv or anything that helps improve
your performance, testing, or animation capabilities."*

**How to apply:** install into the working Python (`C:\Users\Snipe\AppData\Local\hermes\
hermes-agent\venv` - the `python` on PATH) or the driver's node_modules without asking; note
the package and the reason in the commit that uses it, and keep tests skipping cleanly where
the package is absent so the suite runs on a bare checkout. Installed under this permission:
`opencv-contrib-python-headless` (2026-09-04, for P40's saliency + optical-flow metrics).
Paid services are a different matter - see [local-whisper-no-paid-stt](local-whisper-no-paid-stt.md).
