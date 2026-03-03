import asyncio
import edge_tts

TEXT = """先ほどは弊社ブースまでお立ち寄りいただきありがとうございました。ご紹介させていただいたデザインシミュレーターワンディーについて詳しく知りたい場合は、お問合せフォームからデモのご依頼をいただければ、いつでも対応させていただきます。それではご検討よろしくお願いいたします。"""

OUTPUT_FILE = "web/assets/greeting.mp3"

async def generate():
    communicate = edge_tts.Communicate(
        TEXT,
        voice="ja-JP-NanamiNeural",
        rate="-3%",
        pitch="+15Hz",
    )
    
    # Collect word boundary events to find timing
    boundaries = []
    with open(OUTPUT_FILE, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                boundaries.append({
                    "text": chunk["text"],
                    "offset": chunk["offset"] / 10_000_000,  # convert to seconds
                    "duration": chunk["duration"] / 10_000_000,
                })
    
    print(f"Audio saved to {OUTPUT_FILE}")
    print(f"\n=== Word Boundaries ===")
    for b in boundaries:
        print(f"  {b['offset']:6.2f}s (+{b['duration']:.2f}s): {b['text']}")

asyncio.run(generate())
