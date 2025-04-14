from app.models.gemini import Model as GeminiModel
import os
import yt_dlp
import re
import tempfile
import shutil

class Summarizer:
    """Summarizes a YouTube podcast"""

    def __init__(self):
        self.model = GeminiModel()
        self.temp_dir = tempfile.mkdtemp()  # Create a temporary directory


    def __del__(self):
        # Clean up the temporary directory when the object is destroyed
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename by replacing invalid characters."""
        return re.sub(r'[\/:*?"<>|]', '_', filename)  # Replace invalid characters with '_'


    def download_audio(self, url: str) -> str:
        """Download the highest quality audio stream from a YouTube URL and return the file path."""
        
        # # Use app directory-based path
        # app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # download_path = os.path.join(app_dir, 'data')

        # Extract video info first to modify the title
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
            except Exception as e:
                raise RuntimeError(f"Failed to fetch video info: {e}")

        title = self.sanitize_filename(info.get("title", "unknown").replace(" ", "_"))  # Replace spaces with underscores
        ext = "mp3"

        # # Construct the full output path
        # output_template = os.path.join(download_path, f"{title}.%(ext)s")
        # final_audio_path = os.path.join(download_path, f"{title}.{ext}")

        # Use temporary directory
        output_template = os.path.join(self.temp_dir, f"{title}.%(ext)s")
        final_audio_path = os.path.join(self.temp_dir, f"{title}.{ext}")

        ydl_opts = {
            'format': 'bestaudio/best',         # Choose the best audio format available
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',    # Convert audio to a specific format
                'preferredcodec': ext,          # You can change the codec to 'aac', 'ogg', 'wav', etc.
                'preferredquality': '192',      # Set the audio quality (e.g., 192kbps)
            }],
            'outtmpl': output_template,         # Output path and naming convention (or downloads/%(title)s.%(ext)s)
            'quiet': False,                     # Set to True for less output during download
        }
        
        # # Ensure the download path exists
        # os.makedirs(download_path, exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # info = ydl.extract_info(url, download=False)
            duration = info.get("duration", 0)
            if duration > 7200: # 2 hours in seconds
                raise ValueError(f"Video duration too long: {duration}")
            
            try:
                ydl.download([url])
            except Exception as e:
                raise RuntimeError(f"Download failed: {e}")
        
        # Return the final path of the downloaded audio file
        return final_audio_path
    

    def get_video_info(self, url: str) -> dict:
        """Get basic video information without downloading."""
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return {
                    "title": info.get("title", "Unknown"),
                    "channel": info.get("channel", "Unknown"),
                    "duration": info.get("duration", 0),
                    "description": info.get("description", "")
                }
            except Exception as e:
                raise RuntimeError(f"Failed to fetch video info: {e}")


    def get_summary(self, url: str) -> dict:
        """Download a YouTube video's audio and generate a summary."""
        try:
            # Get video info
            video_info = self.get_video_info(url)

            # Check duration
            if video_info["duration"] > 7200:  # 2 hours
                return {"error": "Video too long. Maximum duration is 2 hours."}

            # Download audio
            audio_path = self.download_audio(url)

            # Generate summary
            prompt = """
            Analyze this podcast audio and provide a comprehensive summary with the following structure:

            1. OVERVIEW: A concise 2-3 sentence summary of what the podcast is about, including the main topic and speakers if identifiable.

            2. KEY INSIGHTS: The 3-5 most valuable or interesting insights from the conversation. For each insight, provide 1 descriptive & meaningful sentence.

            3. HIGHLIGHTS: Brief mentions of any standout moments, quotes, or surprising information.

            4. RECOMMENDATION: A brief assessment of who might benefit from this podcast and whether it's worth listening to in full (consider factors like information density, unique perspectives, and entertainment value).

            Format the output with clear headings for each section and separate insights with line breaks.
            """

            summary = self.model.execute_prompt_from_audio(prompt, audio_path)

            # Clean up - delete the audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)

            return {
                "video_info": video_info,
                "summary": summary
            }

        except Exception as e:
            return {"error": str(e)}