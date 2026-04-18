"""
Video Processing Module
Handles watermarking, female detection, and video splitting
"""
import cv2
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess
import json
import sys

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
        # Fallback
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
        self.skip_female = config['youtube_settings'].get('skip_female_videos', False)
        self.split_videos = config['youtube_settings'].get('split_long_videos', False)
        self.split_duration = config['youtube_settings'].get('split_duration_seconds', 30)
        self.min_segment_duration = config['youtube_settings'].get('min_segment_duration_seconds', 20)
        
        # Initialize YOLO model for person detection (lazy loading)
        self.yolo_model = None
    
    def _load_yolo_model(self):
        """Load YOLO model for person detection"""
        if self.yolo_model is None:
            try:
                from ultralytics import YOLO
                print("→ Loading AI model for person detection...")
                self.yolo_model = YOLO('yolov8n.pt')  # Nano model (fastest, smallest)
                print("✓ AI model loaded")
            except Exception as e:
                print(f"⚠ Could not load AI model: {e}")
                self.yolo_model = False
        return self.yolo_model
    
    def detect_female_in_video(self, video_path):
        """
        Detect if there's a female person in the video
        Returns: (has_female: bool, confidence: float)
        """
        if not self.skip_female:
            return False, 0.0
        
        model = self._load_yolo_model()
        if not model:
            print("⚠ Female detection disabled (model not available)")
            return False, 0.0
        
        try:
            cap = cv2.VideoCapture(str(video_path))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            # Sample frames (check every 2 seconds)
            sample_interval = fps * 2 if fps > 0 else 30
            frames_to_check = min(10, total_frames // sample_interval)  # Check max 10 frames
            
            female_detections = 0
            frames_checked = 0
            
            for i in range(frames_to_check):
                frame_pos = i * sample_interval
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                frames_checked += 1
                
                # Run YOLO detection
                results = model(frame, verbose=False)
                
                # Check for person detections
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        
                        # Class 0 is 'person' in COCO dataset
                        if cls == 0 and conf > 0.5:
                            # Simple heuristic: if person detected, assume might be female
                            # For better accuracy, you'd need a gender classification model
                            female_detections += 1
                            break
            
            cap.release()
            
            # If we detect persons in more than 30% of sampled frames, flag it
            if frames_checked > 0:
                detection_rate = female_detections / frames_checked
                has_female = detection_rate > 0.3
                
                if has_female:
                    print(f"⚠ Person detected in {detection_rate*100:.1f}% of frames")
                
                return has_female, detection_rate
            
            return False, 0.0
            
        except Exception as e:
            print(f"⚠ Error in female detection: {e}")
            return False, 0.0
    
    def add_watermark_to_video(self, input_path, output_path):
        """
        Add watermark text to video using ffmpeg - centered, black text, no background
        """
        if not self.add_watermark:
            return input_path
        
        try:
            print(f"→ Adding watermark: {self.watermark_text}")
            
            # Escape the colon in Windows path for FFmpeg drawtext filter
            # C: becomes C\:
            font_file = "C\\:/Windows/Fonts/arial.ttf"
            
            # Centered watermark with black text, no background
            # x=(w-text_w)/2 centers horizontally
            # y=(h-text_h)/2 centers vertically
            cmd = [
                'ffmpeg',
                '-i', str(input_path),
                '-vf', 
                f"drawtext=fontfile={font_file}:text='{self.watermark_text}':fontsize=40:fontcolor=black:x=(w-text_w)/2:y=(h-text_h)/2",
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-c:a', 'copy',
                '-y',
                str(output_path)
            ]
            
            result = run_command_safe(cmd, timeout=300)
            
            # Check if output file was created successfully
            if output_path.exists() and output_path.stat().st_size > 0:
                print(f"✓ Watermark added")
                return output_path
            else:
                # Print last 3 lines of stderr for debugging
                if result.stderr:
                    error_lines = result.stderr.strip().split('\n')
                    relevant_error = '\n'.join(error_lines[-3:])
                    print(f"⚠ Watermark failed:")
                    print(f"  {relevant_error}")
                else:
                    print(f"⚠ Watermark failed: Output file not created")
                print(f"  Using original video")
                return input_path
                
        except FileNotFoundError:
            print("⚠ ffmpeg not installed, skipping watermark")
            return input_path
        except Exception as e:
            print(f"⚠ Watermark error: {e}")
            return input_path
    
    def split_video_into_shorts(self, video_path):
        """
        Split video into segments based on split_duration
        Upload all segments regardless of length
        Returns: list of output file paths
        """
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
            
            # Split if video is longer than split_duration
            if duration <= self.split_duration:
                print(f"→ Video is {duration:.1f}s, no split needed")
                return [video_path]
            
            print(f"→ Splitting {duration:.1f}s video into {self.split_duration}s segments")
            
            # Calculate number of segments (always include remaining part)
            num_segments = int(duration / self.split_duration)
            remaining = duration % self.split_duration
            
            if remaining > 0:
                num_segments += 1
                print(f"  → Will create {num_segments} parts (last part: {remaining:.1f}s)")
            
            output_files = []
            
            for i in range(num_segments):
                start_time = i * self.split_duration
                
                # For the last segment, use remaining duration
                if i == num_segments - 1 and remaining > 0:
                    segment_duration = remaining
                else:
                    segment_duration = self.split_duration
                
                # Create output filename
                stem = video_path.stem
                suffix = video_path.suffix
                output_path = video_path.parent / f"{stem}_part{i+1}{suffix}"
                
                # FFmpeg command to split (re-encode to preserve quality and effects)
                cmd = [
                    'ffmpeg',
                    '-i', str(video_path),
                    '-ss', str(start_time),
                    '-t', str(segment_duration),
                    '-c:v', 'libx264',  # Re-encode video
                    '-preset', 'fast',   # Fast encoding
                    '-crf', '23',        # Good quality
                    '-c:a', 'aac',       # Re-encode audio
                    '-b:a', '128k',      # Audio bitrate
                    '-y',
                    str(output_path)
                ]
                
                result = run_command_safe(cmd, timeout=120)
                
                if result.returncode == 0 and output_path.exists():
                    output_files.append(output_path)
                    print(f"  ✓ Created part {i+1} ({segment_duration:.1f}s)")
                else:
                    print(f"  ⚠ Failed to create part {i+1}")
            
            if output_files:
                # Delete original file after successful split
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
        Complete video processing pipeline:
        1. Split into shorts (if needed)
        2. For each segment: check for female and add watermark
        
        Returns: (should_skip: bool, processed_files: list)
        """
        print(f"\n→ Processing video: {video_path.name}")
        
        # Step 1: Split video first (if enabled)
        if self.split_videos:
            split_files = self.split_video_into_shorts(video_path)
        else:
            split_files = [video_path]
        
        # Step 2: Process each segment (female detection + watermark)
        final_files = []
        
        for segment in split_files:
            # Female detection on this segment
            if self.skip_female:
                has_female, confidence = self.detect_female_in_video(segment)
                if has_female:
                    print(f"✗ Skipping segment {segment.name}: Person detected (confidence: {confidence*100:.1f}%)")
                    # Delete this segment
                    try:
                        segment.unlink()
                    except Exception:
                        pass
                    continue  # Skip to next segment
            
            # Add watermark to this segment
            if self.add_watermark:
                watermarked_path = segment.parent / f"{segment.stem}_watermarked{segment.suffix}"
                processed_path = self.add_watermark_to_video(segment, watermarked_path)
                
                # If watermark was added, delete original segment
                if processed_path != segment and processed_path.exists():
                    try:
                        segment.unlink()
                        segment = processed_path
                    except Exception:
                        pass
            
            final_files.append(segment)
        
        # If all segments were skipped, return skip=True
        if not final_files:
            print("✗ All segments skipped")
            return True, []
        
        return False, final_files
