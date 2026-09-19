# Alpha Stack — Free Tools for Influence + Content + Data

## Pamba's 82 Free Tools (verified monthly)

### Video/Content Production

| Tool | Stars | What | Cost |
|------|-------|------|------|
| **OpenCut** | 85k ★ | Open-source CapCut alternative, browser-based | Free |
| **yt-dlp** | 186k ★ | Download video/audio from any site | Free |
| **FFmpeg** | 63k ★ | Video processing backbone | Free |
| **whisperX** | 24k ★ | Transcription with word-level timestamps | Free |
| **faster-whisper** | 25k ★ | Whisper 4x faster | Free |
| **GPT-SoVITS** | 61k ★ | Clone voice from 1 minute of audio | Free |
| **F5-TTS** | 15k ★ | Zero-shot voice cloning from 10 seconds | Free |
| **Kokoro** | 8.5k ★ | 82M-param TTS, faster than real-time | Free |
| **Chatterbox** | 26k ★ | Open TTS with emotion control | Free |
| **AudioCraft** | 24k ★ | Meta's text-to-music + SFX | Free |
| **demucs** | 3.1k ★ | Stem separation (vocals, drums, bass) | Free |
| **Remotion** | 57k ★ | Make videos with React code | Free |
| **RIFE** | 5.6k ★ | AI frame interpolation (30fps → 120fps) | Free |
| **HandBrake** | 24k ★ | GUI video compressor | Free |
| **OBS Studio** | 75k ★ | Recording and streaming | Free |
| **Cap** | 21k ★ | Beautiful screen recordings | Free |

### Image/Photo

| Tool | Stars | What | Cost |
|------|-------|------|------|
| **remove-ai-watermarks** | 5k ★ | Strip Gemini/C2PA watermarks | Free |
| **IOPaint** | 23k ★ | AI object removal (brush over anything) | Free |
| **rembg** | 24k ★ | Background removal in one command | Free |
| **Upscayl** | 49k ★ | 4x image upscaling, desktop app | Free |
| **Real-ESRGAN** | 37k ★ | Upscaling model CLI | Free |
| **GFPGAN** | 38k ★ | Face restoration | Free |

### Text/Writing

| Tool | Stars | What | Cost |
|------|-------|------|------|
| **humanizer** | 37k ★ | Strip AI tells from writing | Free |
| **marker** | 39k ★ | PDF → clean Markdown | Free |
| **docling** | 65k ★ | IBM document parser | Free |
| **Harper** | 15k ★ | Offline grammar checker | Free |
| **surya** | 21k ★ | OCR that works on receipts/tables | Free |
| **PaddleOCR** | 88k ★ | Industrial OCR toolkit | Free |

### Local AI

| Tool | Stars | What | Cost |
|------|-------|------|------|
| **Ollama** | 179k ★ | Run LLMs locally, one command | Free |
| **llama.cpp** | 125k ★ | Inference engine for everything | Free |
| **ComfyUI** | 128k ★ | Node-graph for image/video models | Free |
| **Open WebUI** | 149k ★ | Self-hosted ChatGPT interface | Free |
| **vLLM** | 89k ★ | High-throughput model serving | Free |
| **Jan** | 44k ★ | Offline ChatGPT desktop app | Free |

### Web/Scraping/Agents

| Tool | Stars | What | Cost |
|------|-------|------|------|
| **browser-use** | 110k ★ | AI agent drives real browser | Free |
| **Firecrawl** | 170k ★ | Website → LLM-ready data | Free |
| **crawl4ai** | 79k ★ | Open-source crawler | Free |
| **Playwright** | 95k ★ | Browser automation | Free |
| **n8n** | 201k ★ | Visual workflow automation | Free |

### Building

| Tool | Stars | What | Cost |
|------|-------|------|------|
| **Claude Code** | 142k ★ | Agentic coding in terminal | Free tier |
| **aider** | 48k ★ | AI pair programming | Free |
| **OpenHands** | 85k ★ | Autonomous dev agent | Free |
| **Supabase** | 108k ★ | Postgres + auth + storage | Free tier |
| **shadcn/ui** | 122k ★ | React components | Free |
| **better-auth** | 30k ★ | Drop-in TypeScript auth | Free |

### Analytics

| Tool | Stars | What | Cost |
|------|-------|------|------|
| **PostHog** | 38k ★ | Analytics + session replay | Free tier |
| **Plausible** | 29k ★ | Privacy-first analytics | Free |

---

## GitHub: AI Influencer / Faceless / UGC

### Top repos

| Repo | Stars | What |
|------|-------|------|
| **AI-Influencer-Generator** | 299 ★ | Stable Diffusion + SadTalker lip-sync |
| **awesome-faceless** | 80+ tools | Curated list of faceless creation tools |
| **podcast-shorts-factory** | 89 ★ | 10 AI agents → podcast shorts |
| **Ytpipe** | — | Research → script → voice → render → upload |
| **faceless-ai-studio** | — | All-in-one with Amazon Nova |
| **ai-creator-academy** | — | Free curriculum for AI creator monetization |
| **Open-AI-UGC** | — | AI UGC video ads with realistic actors |
| **MoneyPrinterTurbo** | — | AI short video generator from topic |
| **VUZA** | — | Free AI video creator + Pinterest scraper |

### Key patterns from Pamba's data

- 42% of videos get under 1,000 views
- 1.7% of videos produce 61% of all reach
- Engagement rate inverts as views scale
- **Same power law rules content AND accounts**
- "Avatar lottery" — test 20 posts, cut cold creators, pour volume into winners
- "Retention improves first, distribution follows" — watch time > 50% → algorithm tests bigger audiences

---

## Integrated Stack for Datagarden

### Content Pipeline (all free)

```
DATA (Breadup/UKGraph/PPP)
    ↓
SCRIPT (humanizer + our data)
    ↓
VOICE (GPT-SoVITS or Kokoro or Edge-TTS)
    ↓
VISUALS (ComfyUI + our charts)
    ↓
EDIT (OpenCut or FFmpeg)
    ↓
CAPTIONS (whisperX)
    ↓
UPLOAD (YouTube API)
    ↓
ANALYTICS (PostHog or YouTube API)
```

### Key MCP servers found

| Server | What | Cost |
|--------|------|------|
| **Apify MCP** | 3000+ pre-built scrapers | Free tier |
| **Facebook Marketplace MCP** | Search FB Marketplace | Free |
| **Social Scraper MCP** | 98 social media tools | API-based |
| **Publora MCP** | 18 social media tools | API-based |
| **browser-use** | AI agent drives browser | Free |
| **Firecrawl** | Website → structured data | Free |

---

## What to build next

1. **Install Ollama + ComfyUI** — local AI for script/visual generation
2. **Set up GPT-SoVITS** — voice clone for consistent channel voice
3. **Use whisperX** — auto-caption all Shorts
4. **Use OpenCut** — edit videos in browser
5. **Use PostHog** — track what content performs
6. **Use n8n** — automate the daily content loop
