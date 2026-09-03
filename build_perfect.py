
from pathlib import Path
orig = Path(r'C:\Users\Snipe\.codex\worktrees\f10b\Outreach Program\content\video_engine\projects\systems-and-blowups\pilots\current-bubble-mechanism\edit\hyperframes-opening-v1\index.html').read_text(encoding='utf-8')
# Update asset paths to point to hyperframes_assets/
updated = orig.replace('assets/', 'hyperframes_assets/')
# Write to review
dest = Path('content/video_engine/review/hyperframes_v1_choreography_perfected.html')
dest.write_text(updated, encoding='utf-8')
print('SUCCESS_WRITTEN_ORIGINAL_CHOREOGRAPHY:', dest.resolve())
