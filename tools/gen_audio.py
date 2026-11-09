#!/usr/bin/env python3
import asyncio, hashlib, json, os, subprocess, sys, tempfile
import edge_tts

VOICE = os.environ.get('VOICE', 'de-DE-KatjaNeural')
OUT = os.path.join(os.path.dirname(__file__), '..', 'audio')
PAR = int(os.environ.get('PAR', '8'))
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else None

def name(t): return hashlib.sha1(t.encode('utf-8')).hexdigest()[:12] + '.mp3'

async def one(t, sem, stats):
    dst = os.path.join(OUT, name(t))
    if os.path.exists(dst): return
    async with sem:
        for attempt in range(5):
            try:
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f: tmp = f.name
                await edge_tts.Communicate(t, VOICE).save(tmp)
                p = await asyncio.create_subprocess_exec('ffmpeg', '-loglevel', 'error', '-y', '-i', tmp,
                        '-ac', '1', '-ar', '24000', '-b:a', '32k', dst + '.part.mp3')
                await p.wait(); os.remove(tmp)
                if p.returncode: raise RuntimeError('ffmpeg')
                os.replace(dst + '.part.mp3', dst)
                stats['ok'] += 1
                if stats['ok'] % 250 == 0: print(f"{stats['ok']} fertig", flush=True)
                return
            except Exception as e:
                await asyncio.sleep(2 * (attempt + 1))
        stats['err'] += 1; print('FEHLER:', t[:80], flush=True)

async def main():
    texts = json.load(open(os.path.join(OUT, 'texts.json'), encoding='utf-8'))
    todo = [t for t in texts if not os.path.exists(os.path.join(OUT, name(t)))]
    if LIMIT: todo = todo[:LIMIT]
    print(f'{len(texts)} Sätze, davon {len(todo)} noch offen', flush=True)
    sem, stats = asyncio.Semaphore(PAR), {'ok': 0, 'err': 0}
    await asyncio.gather(*(one(t, sem, stats) for t in todo))
    print(f"Fertig: {stats['ok']} neu, {stats['err']} Fehler", flush=True)

asyncio.run(main())
