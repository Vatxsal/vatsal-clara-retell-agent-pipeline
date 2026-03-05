import whisper
import os
import sys

def transcribe_audio(audio_path, output_path):
    print("Loading Whisper model...")
    model = whisper.load_model("base")

    print(f"Transcribing: {audio_path}")
    result = model.transcribe(audio_path)

    transcript = result["text"]

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(transcript)

    print(f"Transcript saved to: {output_path}")


def main():

    if len(sys.argv) < 3:
        print("Usage: python transcribe_audio.py <audio_file> <output_file>")
        return

    audio_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.exists(audio_file):
        print("Audio file not found")
        return

    transcribe_audio(audio_file, output_file)


if __name__ == "__main__":
    main()