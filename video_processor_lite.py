"""
Lightweight Video Processing Module for Railway
Only includes FFmpeg-based features (no OpenCV, no AI models)
"""
import subprocess
import json
from pathlib import Path

def run_command_safe(cmd, timeout=None):
    """Run subprocess command with proper UTF-8 encoding"""
    try:
        return subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='replace',
            timeout=timeout
        )
    except Exception:
        return subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            timeout=timeout
        )

class VideoProcessor:
    def __init__(self, config):
        self.config = config
        self.add_watermark = config['youtube_settings'].get('add_watermark', False)
        self.watermark_text = config['youtube_settings'].get('watermark_text', 'Lahori Twins')
        self.skip_female = False  # Disabled on Railway (requires AI models)
        self.split_videos = config['youtube_settings'].get('split_long_videos', False)
        self.split_duration = config['youtube_settings'].get('split_duration_seconds', 30)
        self.min_segment_duration = config['youtube_settings'].get('min_segment_duration_seconds', 20)
        
        print("→ Video processor initialized (lightweight mode - no AI features)")
    
    def detect_female_in_video(self, video_path):
        """Disabled on Railway - requires AI models"""
        return False, 0.0
    
    def add_watermark_to_video(self, input_path, output_path):
        """Add watermark text to video using ffmpeg"""
        if not self.add_watermark:
            return input_path
        
        try:
            print(f"→ Adding watermark: {self.watermark_text}")
            
            # Escape special characters for FFmpeg
            watermark_escaped = self.watermark_text.replace(":", "\\:")
            
            cmd = [
                'ffmpeg',
                '-i', str(input_path),
                '-vf', 
                f"drawtext=text='{watermark_escaped}':fontsize=40:fontcolor=white:x=10:y=10:shadowcolor=black:shadowx=2:shadowy=2",
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-c:a', 'copy',
                '-y',
                str(output_path)
            ]
            
            result = run_command_safe(cmd, timeout=300)
            
            if output_path.exists() and output_path.stat().st_size > 0:
                print(f"✓ Watermark added")
                return output_path
            else:
                print(f"⚠ Watermark failed, using original video")
                return input_path
                
        except FileNotFoundError:
            print("⚠ ffmpeg not installed, skipping watermark")
            return input_path
        except Exception as e:
            print(f"⚠ Watermark error: {e}")
            return input_path
    
    def split_video_into_shorts(self, video_path):
        """Split video into segments based on split_duration"""
        if not self.split_videos:
            return [video_path]
        
        try:
            # Get video duration
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'json',
                str(video_path)
            ]
            
            result = run_command_safe(cmd, timeout=30)
            
            if result.returncode != 0:
                print("⚠ Could not get video duration, skipping split")
                return [video_path]
            
            data = json.loads(result.stdout)
            duration = float(data['format']['duration'])
            
            min_duration_to_split = self.split_duration * 2
            if duration < min_duration_to_split:
                print(f"→ Video is {duration:.1f}s, no split needed")
                return [video_path]
            
            print(f"→ Splitting {duration:.1f}s video into {self.split_duration}s segments")
            
            num_segments = int(duration / self.split_duration)
            remaining = duration % self.split_duration
            
            if remaining > 0 and remaining < self.min_segment_duration:
                print(f"  → Last segment ({remaining:.1f}s) too short, will be discarded")
            elif remaining >= self.min_segment_duration:
                num_segments += 1
            
            output_files = []
            
            for i in range(num_segments):
                start_time = i * self.split_duration
                
                if i == num_segments - 1 and remaining > 0:
                    segment_duration = remaining
                    if segment_duration < self.min_segment_duration:
                        continue
                else:
                    segment_duration = self.split_duration
                
                stem = video_path.stem
                suffix = video_path.suffix
                output_path = video_path.parent / f"{stem}_part{i+1}{suffix}"
                
                cmd = [
                    'ffmpeg',
                    '-i', str(video_path),
                    '-ss', str(start_time),
                    '-t', str(segment_duration),
                    '-c:v', 'libx264',
                    '-preset', 'fast',
                    '-crf', '23',
                    '-c:a', 'aac',
                    '-b:a', '128k',
                    '-y',
                    str(output_path)
                ]
                
                result = run_command_safe(cmd, timeout=120)
                
                if result.returncode == 0 and output_path.exists():
                    output_files.append(output_path)
                    print(f"  ✓ Created part {i+1} ({segment_duration:.1f}s)")
            
            if output_files:
                try:
                    video_path.unlink()
                    print(f"✓ Split into {len(output_files)} parts")
                except Exception:
                    pass
                return output_files
            else:
                return [video_path]
                
        except FileNotFoundError:
            print("⚠ ffmpeg/ffprobe not installed, skipping split")
            return [video_path]
        except Exception as e:
            print(f"⚠ Split error: {e}")
            return [video_path]
    
    def process_video(self, video_path):
        """
        Lightweight video processing:
        1. Split into shorts (if enabled)
        2. Add watermark (if enabled)
        
        Returns: (should_skip: bool, processed_files: list)
        """
        print(f"\n→ Processing video: {video_path.name}")
        
        # Step 1: Split video first (if enabled)
        if self.split_videos:
            split_files = self.split_video_into_shorts(video_path)
        else:
            split_files = [video_path]
        
        # Step 2: Add watermark to each segment
        final_files = []
        
        for segment in split_files:
            if self.add_watermark:
                watermarked_path = segment.parent / f"{segment.stem}_watermarked{segment.suffix}"
                processed_path = self.add_watermark_to_video(segment, watermarked_path)
                
                if processed_path != segment and processed_path.exists():
                    try:
                        segment.unlink()
                        segment = processed_path
                    except Exception:
                        pass
            
            final_files.append(segment)
        
        return False, final_files
