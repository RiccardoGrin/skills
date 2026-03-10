# Troubleshooting

## yt-dlp Issues

### "Video unavailable" or "Private video"
- The video may be private, age-restricted, or region-locked
- Try adding `--cookies-from-browser chrome` to the yt-dlp command if the user has access in their browser
- Age-restricted videos may need authentication

### "Unable to extract video data"
- yt-dlp may be outdated — update with `pip install -U yt-dlp`
- YouTube frequently changes their API; yt-dlp releases patches regularly

### Download hangs or is very slow
- Try a different format: `yt-dlp -f "bestaudio[ext=m4a]"` instead of WAV conversion
- Check if a VPN or proxy is needed
- Try `--no-check-certificates` if there are SSL issues (last resort)

### "ffmpeg not found"
- ffmpeg must be installed separately and on PATH
- Windows: `winget install ffmpeg` or download from ffmpeg.org
- macOS: `brew install ffmpeg`
- Linux: `apt install ffmpeg` or `yum install ffmpeg`

## Whisper API Issues

### "File too large" (413 error)
- Whisper API has a 25MB limit per file
- The download script should auto-split, but if it didn't:
  ```bash
  ffmpeg -i input.wav -f segment -segment_time 600 -acodec pcm_s16le -ar 16000 -ac 1 chunk_%03d.wav
  ```
- Then transcribe each chunk separately

### Poor transcription quality
- Background music degrades quality — no fix via API, but note it in the summary
- Multiple speakers talking over each other reduces accuracy
- Non-English content: add `--language` flag if known (the script doesn't expose this yet; edit directly)
- Very quiet audio: normalize with ffmpeg before transcribing:
  ```bash
  ffmpeg -i input.wav -af "loudnorm" -ar 16000 -ac 1 normalized.wav
  ```

### Rate limiting (429 errors)
- Wait and retry — OpenAI rate limits vary by tier
- For long videos with many chunks, add delays between API calls
- Consider upgrading your OpenAI API tier

### Timeout errors
- Large files (close to 25MB) can take a while to upload and process
- Check your internet connection
- The API occasionally has outages — check status.openai.com

## Audio Format Issues

### "Codec not supported" errors
- Ensure ffmpeg is installed with common codec support
- Try re-encoding: `ffmpeg -i input.mp3 -acodec libmp3lame -ar 16000 -ac 1 output.mp3`

## General Tips

- **Cost awareness**: Whisper API costs ~$0.006/minute of audio. A 1-hour video costs ~$0.36
- **Caching**: Always check `transcriptions/<VIDEO_ID>_transcript.txt` before re-processing
- **Disk space**: Clean up mp3 files after transcription; they're no longer needed
- **Long videos**: Videos over 3 hours will produce very large transcripts; consider whether a summary of specific sections would be more useful
