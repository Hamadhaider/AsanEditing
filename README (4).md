# AsanEditing — AI Documentary Production Studio

A local-first starter application with a premium dark dashboard, a Gemini browser-session image workflow, expressive Edge TTS narration, scene cards/captions, and FFmpeg MP4 rendering.

## Important before using

- **Gemini image generation:** this version opens a visible Chromium browser using a persistent local profile. Sign into your own Google/Gemini account manually in that window. The app does not request or store your Google password. It then attempts to submit image prompts to Gemini and save the generated image from the page.
- This uses the access/limits of your Gemini account, but **does not promise unlimited generation**. Gemini can impose quotas, confirmations, or other limits. Browser UI automation is inherently fragile; if Google changes its page, image extraction may need updating. Never bypass CAPTCHAs, account checks, or usage restrictions.
- **Narration:** uses Edge TTS neural voices. It supports voice selection, slightly slower pacing and lower pitch. This is not a full acting/emotion model; expressive quality varies by voice and text. Edge TTS requires internet and is not a guaranteed commercial SLA. Check applicable terms before monetizing output.
- The target video duration is a production target; actual runtime follows generated narration length. It is not guaranteed to be exact.
- This is a local MVP, not a tested production-grade product. It does not include historical fact checking, licensed background music, subtitles in SRT, persistent database, exact crossfades, or a CapCut-like manual timeline editor.
- Keep the backend running throughout production. Job state is in memory and resets if the backend restarts.

## Requirements

- Python 3.10+
- Node.js 20+
- FFmpeg + FFprobe installed and on PATH
- Google account with access to Gemini image generation
- Internet connection

## Run on Windows

1. Install FFmpeg and ensure `ffmpeg -version` works in Command Prompt.
2. Open a terminal in `asanediting/backend` and run:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

3. Open a second terminal in `asanediting/frontend` and run:

```powershell
npm install
copy .env.local.example .env.local
npm run dev
```

4. Open http://localhost:3000.
5. Click **Connect Gemini**. A Chromium window opens. Sign into Gemini manually if requested, then return to the dashboard.
6. Paste a script (at least 80 characters), select duration/scenes/voice, and click **Generate my video**.

## Run on macOS/Linux

Install FFmpeg, then run `backend/run_mac_linux.sh` from the backend directory. In another terminal, install and run the frontend as above.

## How the Gemini browser profile works

The browser profile is stored in `backend/gemini-browser-profile/`. It preserves the local sign-in session. Do not share this folder; it may contain authenticated session data. If you need to sign out, do so inside the opened Gemini browser. Delete the profile folder only if you intentionally want to reset the local session.

## Architecture

- `frontend/`: Next.js + Framer Motion dashboard
- `backend/app/gemini_browser.py`: persistent browser session and Gemini UI automation
- `backend/app/story.py`: script-to-scene splitting and visual prompt creation
- `backend/app/narration.py`: Edge TTS narration
- `backend/app/render.py`: Pillow text overlays and FFmpeg animation/rendering
- `backend/app/worker.py`: staged production pipeline and progress updates

## Troubleshooting

- If Gemini asks you to sign in, finish sign-in manually in the opened browser.
- If generation stops at image extraction, inspect the Gemini browser tab. Gemini's UI or download behavior may have changed. The error will be shown in the dashboard.
- If FFmpeg is not found, install it and add its `bin` directory to PATH, then restart the backend terminal.
- If the browser fails to launch, run `playwright install chromium` again.
- Do not put Google passwords, cookies, or browser profile contents into source control.
