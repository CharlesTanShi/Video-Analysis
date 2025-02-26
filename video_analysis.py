import os
import glob
import moviepy.editor as mp
import google.generativeai as genai
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY. Set it as an environment variable.")

genai.configure(api_key=GEMINI_API_KEY)

INPUT_FOLDER = "input_videos"
OUTPUT_FOLDER = "output_videos"
RESULTS_FOLDER = "results"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

def convert_mov_to_mp4(input_path, output_path):
    """
    Converts .mov file to .mp4 using MoviePy.
    """
    try:
        print(f"Converting {input_path} to {output_path}...")
        clip = mp.VideoFileClip(input_path)
        clip.write_videofile(output_path, codec="libx264", fps=24)
        print(f"Conversion complete: {output_path}")
        return True
    except Exception as e:
        print(f"Error converting {input_path}: {e}")
        return False

def analyze_video(video_path):
    """
    Sends the .mp4 video file along with a text prompt to Google Gemini API for action classification.
    """
    print(f"Analyzing {video_path} with Gemini API...")

    model = genai.GenerativeModel("gemini-1.5-flash")

    try:
        with open(video_path, "rb") as video_file:
            video_data = video_file.read()

        response = model.generate_content([
            {"text": "Analyze the actions and objects in this video."},  # Required text prompt
            {"mime_type": "video/mp4", "data": video_data}  # Correct video format
        ])

        print("API Response:", response.text)

        if not response.text or response.text.strip() == "":
            print("⚠API did not return any text response. Skipping file save.")
            return

        result_file = os.path.join(RESULTS_FOLDER, os.path.basename(video_path) + ".txt")
        with open(result_file, "w") as f:
            f.write(response.text)

        print(f"Yayyy analysis complete. Results saved to {result_file}")

    except Exception as e:
        print(f"Error analyzing {video_path}: {e}")

if __name__ == "__main__":
    mov_files = glob.glob(os.path.join(INPUT_FOLDER, "*.mov"))

    if not mov_files:
        print("⚠No .mov files found in 'input_videos' folder.")
    else:
        for mov_file in mov_files:
            mp4_file = os.path.join(OUTPUT_FOLDER, os.path.basename(mov_file).replace(".mov", ".mp4"))
        
            # Convert MOV to MP4
            if convert_mov_to_mp4(mov_file, mp4_file):
                # Analyze the converted MP4 video
                analyze_video(mp4_file)
        
        print("✅ All videos processed successfully! Thank you for using my script!!!")
