import ollama
from youtube_transcript_api import YouTubeTranscriptApi
import re

MODEL = "llama3.2:1b"

class YoutubeVideoID:
    def __init__(self, url):
        self.url = url
        self.video_id = self.extractVideoId(url)

    def extractVideoId(self, url):
        """
        Extracts the YouTube video ID from a given URL.
        Supports both regular and shortened URLs.
        """
        # Regular expression to match YouTube video URL and extract the video ID
        regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|\S*\?v=)|(?:youtu\.be\/))([a-zA-Z0-9_-]{11})"
        match = re.match(regex, url)
        
        if match:
            return match.group(1)
        else:
            raise ValueError("Invalid YouTube URL")

    def __str__(self):
        return f"Video ID: {self.video_id}"
    
video_url = "https://www.youtube.com/watch?v=Nl7aCUsWykg"

yt_video = YoutubeVideoID(video_url)
print(yt_video)

def get_transcript(video_id, language='en'):
    try:
        # Try to get the transcript in the desired language
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        # Join all the 'text' fields into a single string
        return " ".join([item['text'] for item in transcript])
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None
    
# Fetch transcript using the video ID
transcript_text = get_transcript(yt_video.video_id)
print(len(transcript_text))

def summarize_text(text):
    try:
        system_prompts = """
        You are a helpful assistant who provides concise and accurate summaries of text. Your task is to:
        
        - Capture the key points of the content.
        - Keep the summary brief and easy to understand.
        - Avoid summarizing overly lengthy texts or breaking them into excessively short summaries.
        - Use bullet points where appropriate to enhance clarity and structure.
        """

        messages = [
        {"role": "system", "content": system_prompts},
        {"role": "user", "content": f"Summarize the following text concisely: {text}"}]

        response = ollama.chat(model=MODEL, messages=messages)
        return response.get("message", {}).get("content", "No summary available")
        
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return None
    
def split_text(text, chunk_size=3000):
    """
    Splits large text into smaller chunks based on the given chunk size.
    Ensures that chunks end with a full stop where possible to maintain sentence integrity.
    
    :param text: str, the text to be split
    :param chunk_size: int, maximum size of each chunk (default 3000 characters)
    :return: list of str, where each str is a chunk of text
    """
    chunks = []
    while len(text) > chunk_size:
        # Find the last full stop within or at the chunk size
        split_point = text.rfind('.', 0, chunk_size + 1)  # +1 to include the period itself if it's at chunk_size
        if split_point == -1:  # No period found within the chunk size
            split_point = chunk_size
        
        # Append the chunk, ensuring we don't strip spaces that might be part of the sentence structure
        chunks.append(text[:split_point + 1] if split_point != chunk_size else text[:chunk_size])
        text = text[split_point + 1:] if split_point != chunk_size else text[chunk_size:]
    
    # Add the remaining text as the final chunk, only strip if there's content
    if text:
        chunks.append(text.strip())
    
    return chunks

transcript_chunks = split_text(transcript_text)

# Now you can summarize each chunk individually
summaries = []
for chunk in transcript_chunks:
    summary = summarize_text(chunk)
    summaries.append(summary)


# Combine the individual summaries into one
full_summary = " ".join(summaries)
print(full_summary)