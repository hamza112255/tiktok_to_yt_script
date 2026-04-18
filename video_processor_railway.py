"""
Railway video processing module.
Supports watermarking, video splitting, and female detection using DeepFace.
"""

import json
import subprocess


def run_command_safe(cmd, timeout=None):
    """Run subprocess command with proper UTF-8 encoding."""
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
        self.skip_female = config['youtube_settings'].get('skip_female_videos', False)
        self.split_videos = config['youtube_settings'].get('split_long_videos', False)
        self.split_duration = config['youtube_settings'].get('split_duration_seconds', 30)
        self.min_segment_duration = config['youtube_settings'].get('min_segment_duration_seconds', 20)
        self.deepface_available = None

        print("-> Video processor initialized (Railway mode)")

    def _load_deepface(self):
        """Load DeepFace library for gender detection"""
        if self.deepface_available is None:
            try:
                from deepface import DeepFace
                self.DeepFace = DeepFace
                self.deepface_available = True
                print("✓ DeepFace loaded for gender detection")
            except ImportError:
                print("Warning: DeepFace not installed. Install with: pip install deepface")
                print("  Female detection will be disabled.")
                self.deepface_available = False
            except Exception as e:
                print(f"Warning: Could not load DeepFace: {e}")
                self.deepface_available = False
        
        return self.deepface_available

    def detect_female_in_video(self, video_path):
        """
        Detect if there's a female person in the video using DeepFace.
        Returns: (has_female: bool, confidence: float)
        """
        if not self.skip_female:
            return False, 0.0

        if not self._load_deepface():
            print("Warning: Female detection disabled (DeepFace not available)")
            return False, 0.0

        cap = None
        try:
            import cv2

            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                print("Warning: Could not open video for female detection")
                return False, 0.0

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))

            sample_interval = max(fps * 3, 90) if fps > 0 else 90
            if total_frames > 0:
                frames_to_check = min(8, max(1, total_frames // sample_interval))
            else:
                frames_to_check = 4

            female_detections = 0
            frames_checked = 0

            print(f"-> Analyzing video for female presence ({frames_to_check} frames)...")

            for i in range(frames_to_check):
                frame_pos = i * sample_interval
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()
                if not ret or frame is None:
                    break

                frames_checked += 1

                try:
                    # Analyze frame for gender using DeepFace
                    result = self.DeepFace.analyze(
                        frame,
                        actions=['gender'],
                        enforce_detection=False,
                        silent=True
                    )

                    # Check if any face is detected as female
                    if isinstance(result, list):
                        for face in result:
                            gender = face.get('dominant_gender', '').lower()
                            if gender == 'woman':
                                female_detections += 1
                                break
                    elif isinstance(result, dict):
                        gender = result.get('dominant_gender', '').lower()
                        if gender == 'woman':
                            female_detections += 1

                except Exception:
                    # Frame analysis failed (no face detected or other error)
                    continue

            if frames_checked == 0:
                return False, 0.0

            detection_rate = female_detections / frames_checked
            has_female = detection_rate > 0.3
            if has_female:
                print(f"Warning: Female detected in {detection_rate * 100:.1f}% of frames")
            else:
                print(f"✓ No female detected (checked {frames_checked} frames)")

            return has_female, detection_rate

        except Exception as e:
            print(f"Warning: Error in female detection: {e}")
            return False, 0.0
        finally:
            if cap is not None:
                try:
                    cap.release()
                except Exception:
                    pass

    def add_watermark_to_video(self, input_path, output_path):
        """Add watermark text to video using ffmpeg - centered, black text, no background."""
        if not self.add_watermark:
            return input_path

        try:
            print(f"-> Adding watermark: {self.watermark_text}")

            watermark_escaped = (
                self.watermark_text
                .replace("\\", "\\\\")
                .replace(":", "\\:")
                .replace("'", "\\'")
            )

            # Centered watermark with black text, no background
            # x=(w-text_w)/2 centers horizontally
            # y=(h-text_h)/2 centers vertically
            cmd = [
                'ffmpeg',
                '-i', str(input_path),
                '-vf',
                f"drawtext=text='{watermark_escaped}':fontsize=40:fontcolor=black:x=(w-text_w)/2:y=(h-text_h)/2",
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-c:a', 'copy',
                '-y',
                str(output_path)
            ]

            result = run_command_safe(cmd, timeout=300)

            if output_path.exists() and output_path.stat().st_size > 0:
                print("✓ Watermark added")
                return output_path

            if result.stderr:
                error_lines = result.stderr.strip().split('\n')
                relevant_error = '\n'.join(error_lines[-3:])
                print("Warning: Watermark failed:")
                print(f"  {relevant_error}")
            else:
                print("Warning: Watermark failed: Output file not created")
            print("  Using original video")
            return input_path

        except FileNotFoundError:
            print("Warning: ffmpeg not installed, skipping watermark")
            return input_path
        except Exception as e:
            print(f"Warning: Watermark error: {e}")
            return input_path

    def split_video_into_shorts(self, video_path):
        """
        Split video into segments based on split_duration.
        Upload all segments regardless of length.
        """
        if not self.split_videos:
            return [video_path]

        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'json',
                str(video_path)
            ]

            result = run_command_safe(cmd, timeout=30)
            if result.returncode != 0:
                print("Warning: Could not get video duration, skipping split")
                return [video_path]

            data = json.loads(result.stdout)
            duration = float(data['format']['duration'])

            # Split if video is longer than split_duration
            if duration <= self.split_duration:
                print(f"-> Video is {duration:.1f}s, no split needed")
                return [video_path]

            print(f"-> Splitting {duration:.1f}s video into {self.split_duration}s segments")

            # Calculate number of segments (always include remaining part)
            num_segments = int(duration / self.split_duration)
            remaining = duration % self.split_duration

            if remaining > 0:
                num_segments += 1
                print(f"  -> Will create {num_segments} parts (last part: {remaining:.1f}s)")

            output_files = []

            for i in range(num_segments):
                start_time = i * self.split_duration

                # For the last segment, use remaining duration
                if i == num_segments - 1 and remaining > 0:
                    segment_duration = remaining
                else:
                    segment_duration = self.split_duration

                output_path = video_path.parent / f"{video_path.stem}_part{i + 1}{video_path.suffix}"

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
                    print(f"  ✓ Created part {i + 1} ({segment_duration:.1f}s)")
                else:
                    print(f"  Warning: Failed to create part {i + 1}")

            if output_files:
                try:
                    video_path.unlink()
                    print(f"✓ Split into {len(output_files)} parts")
                except Exception:
                    pass
                return output_files

            return [video_path]

        except FileNotFoundError:
            print("Warning: ffmpeg/ffprobe not installed, skipping split")
            return [video_path]
        except Exception as e:
            print(f"Warning: Split error: {e}")
            return [video_path]

    def process_video(self, video_path):
        """
        Complete video processing pipeline:
        1. Split into shorts if needed
        2. For each segment: check for person presence and add watermark
        """
        print(f"\n-> Processing video: {video_path.name}")

        if self.split_videos:
            split_files = self.split_video_into_shorts(video_path)
        else:
            split_files = [video_path]

        final_files = []

        for segment in split_files:
            if self.skip_female:
                has_female, confidence = self.detect_female_in_video(segment)
                if has_female:
                    print(f"-> Skipping segment {segment.name}: person detected ({confidence * 100:.1f}%)")
                    try:
                        segment.unlink()
                    except Exception:
                        pass
                    continue

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

        if not final_files:
            print("Warning: All segments were skipped")
            return True, []

        return False, final_files
