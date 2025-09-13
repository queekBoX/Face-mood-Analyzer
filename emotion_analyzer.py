import os
import cv2
import numpy as np
from deepface import DeepFace
from PIL import Image
import json
from datetime import datetime
from retinaface import RetinaFace
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import time
import subprocess

logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    def __init__(self, photos_dir='photos', output_dir='output'):
        self.photos_dir = photos_dir
        self.output_dir = output_dir
        self.emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        self.results = []
        self.cache_dir = 'cache'
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize RetinaFace detector once
        self.detector = RetinaFace.build_model()
        
        # Initialize thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def analyze_photo(self, image_path):
        """Analyze emotions in a single photo"""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise Exception(f"Could not read image: {image_path}")
            
            # Analyze emotions using DeepFace
            result = DeepFace.analyze(
                img_path=image_path,
                actions=['emotion'],
                enforce_detection=False
            )
            
            # Extract the first face's emotions
            if isinstance(result, list):
                result = result[0]
            
            emotions = result['emotion']
            dominant_emotion = result['dominant_emotion']
            
            # Get image metadata
            img = Image.open(image_path)
            date_taken = None
            if hasattr(img, '_getexif') and img._getexif():
                exif = img._getexif()
                if exif:
                    date_taken = exif.get(36867)  # DateTimeOriginal tag
            
            return {
                'file_name': os.path.basename(image_path),
                'emotions': emotions,
                'dominant_emotion': dominant_emotion,
                'date_taken': date_taken,
                'confidence': emotions[dominant_emotion]
            }
            
        except Exception as e:
            print(f"Error analyzing {image_path}: {str(e)}")
            return None

    def analyze_all_photos(self):
        """Analyze all photos in the photos directory"""
        self.results = []
        
        # Get all image files
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
        image_files = [f for f in os.listdir(self.photos_dir) 
                      if f.lower().endswith(image_extensions)]
        
        # Sort files by name (assuming they might have timestamps)
        image_files.sort()
        
        for image_file in image_files:
            image_path = os.path.join(self.photos_dir, image_file)
            result = self.analyze_photo(image_path)
            if result:
                self.results.append(result)
        
        # Save results to JSON
        output_file = os.path.join(self.output_dir, 'emotion_analysis.json')
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        return self.results

    def get_emotion_timeline(self):
        """Get a timeline of emotions across all photos"""
        if not self.results:
            self.analyze_all_photos()
        
        timeline = []
        for result in self.results:
            timeline.append({
                'file_name': result['file_name'],
                'dominant_emotion': result['dominant_emotion'],
                'confidence': result['confidence'],
                'date_taken': result['date_taken']
            })
        
        return timeline

    def get_emotion_statistics(self):
        """Get statistics about emotions across all photos"""
        if not self.results:
            self.analyze_all_photos()
        
        emotion_counts = {emotion: 0 for emotion in self.emotions}
        total_photos = len(self.results)
        
        for result in self.results:
            emotion_counts[result['dominant_emotion']] += 1
        
        return {
            'total_photos': total_photos,
            'emotion_distribution': emotion_counts,
            'most_common_emotion': max(emotion_counts.items(), key=lambda x: x[1])[0]
        }

    @lru_cache(maxsize=32)
    def _detect_faces(self, image_path):
        """Cached face detection to avoid reprocessing the same image"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {}
            return RetinaFace.detect_faces(img, model=self.detector)
        except Exception as e:
            logger.error(f"Error detecting faces in {image_path}: {str(e)}")
            return {}

    def _process_single_photo(self, photo_path, reference_images, model_name, distance_metric, threshold, required_matches):
        """Process a single photo with face detection and recognition"""
        try:
            img = cv2.imread(photo_path)
            if img is None:
                return None

            faces = self._detect_faces(photo_path)
            if not isinstance(faces, dict):
                return None

            marked_img = img.copy()
            found_faces = False

            for face_idx, face_data in faces.items():
                facial_area = face_data['facial_area']
                x = int(facial_area[0])
                y = int(facial_area[1])
                w = int(facial_area[2] - x)
                h = int(facial_area[3] - y)
                
                # Ensure coordinates are within image bounds
                x = max(0, x)
                y = max(0, y)
                w = min(w, img.shape[1] - x)
                h = min(h, img.shape[0] - y)
                
                if w <= 0 or h <= 0:
                    continue
                
                detected_face_img = img[y:y+h, x:x+w]
                
                # Count successful matches with reference photos
                match_count = 0
                best_distance = float('inf')
                
                for ref_img in reference_images:
                    try:
                        result = DeepFace.verify(
                            img1_path=ref_img,
                            img2_path=detected_face_img,
                            model_name=model_name,
                            distance_metric=distance_metric,
                            enforce_detection=False
                        )
                        
                        if result['verified'] and result['distance'] <= threshold:
                            match_count += 1
                            best_distance = min(best_distance, result['distance'])
                            
                            if match_count >= required_matches:
                                break
                                
                    except Exception as e:
                        continue

                if match_count >= min(required_matches, len(reference_images)):
                    try:
                        emotion_result = DeepFace.analyze(
                            img_path=detected_face_img,
                            actions=['emotion'],
                            enforce_detection=False
                        )
                        dominant_emotion = emotion_result['dominant_emotion']
                        
                        # Add confidence score to the display
                        confidence_score = round((1 - best_distance) * 100, 1)
                        display_text = f"{dominant_emotion} ({confidence_score}%)"
                        
                        # Draw rectangle and text
                        rect_color = (0, 255, 0)
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        font_scale = 0.9
                        thickness = 2
                        
                        # Draw rectangle
                        cv2.rectangle(marked_img, (x, y), (x + w, y + h), rect_color, 2)
                        
                        # Calculate text size
                        (text_width, text_height), baseline = cv2.getTextSize(
                            display_text, font, font_scale, thickness
                        )
                        
                        # Position text
                        text_x = x + w + 10
                        text_y = y + h // 2 + text_height // 2
                        
                        # Draw white background for text
                        cv2.rectangle(
                            marked_img,
                            (text_x - 2, text_y - text_height - 2),
                            (text_x + text_width + 2, text_y + baseline + 2),
                            (255, 255, 255),
                            -1
                        )
                        
                        # Draw text
                        cv2.putText(
                            marked_img, display_text, (text_x, text_y),
                            font, font_scale, rect_color,
                            thickness, cv2.LINE_AA
                        )
                        
                        found_faces = True
                        
                    except Exception as e:
                        logger.error(f"Error analyzing emotion in {photo_path}: {str(e)}")
                        continue

            if found_faces:
                return marked_img
            return None

        except Exception as e:
            logger.error(f"Error processing {photo_path}: {str(e)}")
            return None

    def mark_reference_faces_in_photos(self, reference_dir='reference', photos_dir='photos', marked_dir='output/marked_photos', 
                                     model_name='ArcFace', distance_metric='cosine',
                                     threshold=0.68, required_matches=2):
        """
        Mark faces in photos that match the reference photos.
        Uses RetinaFace for detection and ArcFace for recognition.
        Requires multiple matches for higher accuracy.
        """
        os.makedirs(marked_dir, exist_ok=True)
        
        # Get reference images
        reference_images = [os.path.join(reference_dir, f) for f in os.listdir(reference_dir) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        if len(reference_images) == 0:
            raise ValueError("No reference images found!")

        # Get main photos
        photo_files = [f for f in os.listdir(photos_dir) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        marked_files = []

        # Process photos in smaller batches to avoid timeouts
        batch_size = 5
        for i in range(0, len(photo_files), batch_size):
            batch = photo_files[i:i + batch_size]
            futures = []
            
            for photo_file in batch:
                photo_path = os.path.join(photos_dir, photo_file)
                future = self.executor.submit(
                    self._process_single_photo,
                    photo_path,
                    reference_images,
                    model_name,
                    distance_metric,
                    threshold,
                    required_matches
                )
                futures.append((photo_file, future))
                logger.info(f"Started processing {photo_file}")

            # Collect results for this batch
            for photo_file, future in futures:
                try:
                    marked_img = future.result(timeout=300)  # 5-minute timeout per photo
                    if marked_img is not None:
                        marked_path = os.path.join(marked_dir, f"marked_{photo_file}")
                        cv2.imwrite(marked_path, marked_img)
                        marked_files.append(marked_path)
                        logger.info(f"Successfully processed {photo_file}")
                    else:
                        logger.info(f"No matching faces found in {photo_file}")
                except Exception as e:
                    logger.error(f"Error processing {photo_file}: {str(e)}")
                    continue

            # Small delay between batches to prevent overload
            time.sleep(1)

        return marked_files

    def create_video_from_photos(self, image_files, output_dir, fps=2):
        """Create a video from a list of photos with audio."""
        try:
            if not image_files:
                logger.error("No images provided for video creation")
                return False

            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            temp_video_path = os.path.join(output_dir, 'temp_video.mp4')
            output_path = os.path.join(output_dir, 'output_video.mp4')

            # Read first image to get dimensions
            first_image = cv2.imread(image_files[0])
            if first_image is None:
                logger.error(f"Could not read first image: {image_files[0]}")
                return False
            
            height, width = first_image.shape[:2]

            # Define the codec and create VideoWriter object
            # Use H264 codec for web compatibility
            if os.name == 'nt':  # Windows
                fourcc = cv2.VideoWriter_fourcc(*'H264')
            else:  # Linux/Mac
                fourcc = cv2.VideoWriter_fourcc(*'avc1')
            
            out = cv2.VideoWriter(
                temp_video_path,
                fourcc,
                fps,
                (width, height)
            )

            if not out.isOpened():
                logger.error("Failed to create video writer")
                return False

            try:
                # Write each image to video
                for image_file in image_files:
                    frame = cv2.imread(image_file)
                    if frame is not None:
                        # Hold each frame for desired duration (duplicate frames)
                        # 3 seconds per image for better viewing experience
                        for _ in range(int(fps * 3)):  # 3 seconds per image
                            out.write(frame)
                    else:
                        logger.warning(f"Could not read image: {image_file}")

                # Release the video writer
                out.release()
                
                # Generate audio and combine with video
                if os.path.exists(temp_video_path) and os.path.getsize(temp_video_path) > 0:
                    logger.info(f"Temporary video created successfully")
                    
                    # Add audio using moviepy
                    success = self._add_audio_to_video(temp_video_path, output_path, len(image_files))
                    
                    # Clean up temporary file
                    if os.path.exists(temp_video_path):
                        os.remove(temp_video_path)
                    
                    if success:
                        logger.info(f"Video with audio created successfully at {output_path}")
                        return True
                    else:
                        logger.error("Failed to add audio to video")
                        return False
                else:
                    logger.error("Temporary video file was not created or is empty")
                    return False

            finally:
                out.release()

        except Exception as e:
            logger.error(f"Error creating video: {str(e)}")
            return False

    def _add_audio_to_video(self, video_path, output_path, num_images):
        """Add generated audio to video using moviepy."""
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
            import numpy as np
            from scipy.io import wavfile
            
            # Load the video
            video = VideoFileClip(video_path)
            video_duration = video.duration
            
            # Generate simple background music based on emotions
            audio_path = self._generate_simple_audio(video_duration, output_path.replace('.mp4', '_audio.wav'))
            
            if audio_path and os.path.exists(audio_path):
                # Load the generated audio
                audio = AudioFileClip(audio_path)
                
                # Set audio to video
                final_video = video.set_audio(audio)
                
                # Write the final video
                final_video.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True,
                    verbose=False,
                    logger=None
                )
                
                # Clean up
                video.close()
                audio.close()
                final_video.close()
                
                # Remove temporary audio file
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                
                return True
            else:
                # If audio generation fails, just copy the video without audio
                logger.warning("Audio generation failed, creating video without audio")
                import shutil
                shutil.copy2(video_path, output_path)
                return True
                
        except Exception as e:
            logger.error(f"Error adding audio to video: {str(e)}")
            # Fallback: copy video without audio
            try:
                import shutil
                shutil.copy2(video_path, output_path)
                return True
            except:
                return False

    def _analyze_emotions_from_photos(self, image_files):
        """Analyze emotions from processed photos to determine audio style."""
        emotion_counts = {'happy': 0, 'sad': 0, 'angry': 0, 'fear': 0, 'surprise': 0, 'disgust': 0, 'neutral': 0}
        
        for image_file in image_files:
            try:
                # Try to extract emotion from filename or analyze the image
                filename = os.path.basename(image_file)
                if 'marked_' in filename:
                    # Try to read the image and analyze emotion
                    img = cv2.imread(image_file)
                    if img is not None:
                        try:
                            result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
                            if isinstance(result, list):
                                result = result[0]
                            dominant_emotion = result['dominant_emotion'].lower()
                            if dominant_emotion in emotion_counts:
                                emotion_counts[dominant_emotion] += 1
                        except:
                            emotion_counts['neutral'] += 1
            except Exception as e:
                logger.warning(f"Could not analyze emotion for {image_file}: {str(e)}")
                emotion_counts['neutral'] += 1
        
        # Find dominant emotion
        dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
        return dominant_emotion, emotion_counts

    def _generate_simple_audio(self, duration, output_path):
        """Generate emotion-based background audio with longer duration and variety."""
        try:
            import numpy as np
            from scipy.io import wavfile
            
            # Ensure minimum duration of 30 seconds for better audio experience
            min_duration = max(duration, 30.0)
            sample_rate = 44100
            samples = int(min_duration * sample_rate)
            
            # Analyze emotions from the current batch of photos
            marked_photos_folder = os.path.join('uploads', 'output', 'marked_photos')
            marked_files = []
            if os.path.exists(marked_photos_folder):
                marked_files = [os.path.join(marked_photos_folder, f) for f in os.listdir(marked_photos_folder) 
                               if f.endswith(('.png', '.jpg', '.jpeg'))]
            
            dominant_emotion = 'neutral'
            if marked_files:
                dominant_emotion, _ = self._analyze_emotions_from_photos(marked_files)
            
            logger.info(f"Generating {dominant_emotion} themed audio for {min_duration:.1f} seconds")
            
            # Generate time array
            t = np.linspace(0, min_duration, samples, False)
            
            # Emotion-based audio generation
            audio = self._generate_emotion_based_music(t, dominant_emotion, min_duration)
            
            # Apply fade in and fade out
            fade_samples = int(2.0 * sample_rate)  # 2 second fade
            if len(audio) > 2 * fade_samples:
                # Fade in
                fade_in = np.linspace(0, 1, fade_samples)
                audio[:fade_samples] *= fade_in
                # Fade out
                fade_out = np.linspace(1, 0, fade_samples)
                audio[-fade_samples:] *= fade_out
            
            # Normalize audio to prevent clipping
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                audio = audio / max_val * 0.8  # Leave some headroom
            
            # Convert to 16-bit integers
            audio_int = (audio * 32767).astype(np.int16)
            
            # Save as WAV file
            wavfile.write(output_path, sample_rate, audio_int)
            
            logger.info(f"Generated {dominant_emotion} themed audio file: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            return None

    def _generate_emotion_based_music(self, t, emotion, duration):
        """Generate cinematic movie-style music based on detected emotion."""
        import numpy as np
        
        logger.info(f"🎵 Composing {emotion.upper()} themed cinematic score...")
        
        # Movie-style emotion themes with cinematic progressions
        emotion_themes = {
            'happy': {
                'name': 'Joyful Celebration',
                'description': 'Uplifting orchestral theme with bright melodies',
                'key': 'C Major',
                'chord_progression': [261.63, 329.63, 392.00, 523.25],  # C-E-G-C (octave)
                'melody_notes': [523.25, 587.33, 659.25, 698.46, 783.99],  # C5-D5-E5-F5-G5
                'tempo': 120,  # BPM
                'style': 'orchestral_upbeat',
                'dynamics': 'forte'
            },
            'sad': {
                'name': 'Melancholic Reflection',
                'description': 'Emotional piano ballad with string accompaniment',
                'key': 'A Minor',
                'chord_progression': [220.00, 261.63, 293.66, 349.23],  # Am-C-D-F
                'melody_notes': [440.00, 493.88, 523.25, 587.33, 659.25],  # A4-B4-C5-D5-E5
                'tempo': 60,  # BPM
                'style': 'piano_ballad',
                'dynamics': 'piano'
            },
            'angry': {
                'name': 'Intense Confrontation',
                'description': 'Dramatic orchestral piece with powerful brass',
                'key': 'D Minor',
                'chord_progression': [146.83, 174.61, 220.00, 246.94],  # Dm-F-Am-Bb
                'melody_notes': [293.66, 329.63, 369.99, 415.30, 466.16],  # D4-E4-F#4-G#4-A#4
                'tempo': 140,  # BPM
                'style': 'orchestral_dramatic',
                'dynamics': 'fortissimo'
            },
            'fear': {
                'name': 'Suspenseful Mystery',
                'description': 'Eerie atmospheric soundscape with tension',
                'key': 'F# Minor',
                'chord_progression': [184.99, 220.00, 246.94, 293.66],  # F#m-Am-Bb-Dm
                'melody_notes': [369.99, 415.30, 466.16, 523.25, 587.33],  # F#4-G#4-A#4-C5-D5
                'tempo': 80,  # BPM
                'style': 'atmospheric_dark',
                'dynamics': 'pianissimo'
            },
            'surprise': {
                'name': 'Magical Discovery',
                'description': 'Whimsical orchestral piece with playful elements',
                'key': 'E Major',
                'chord_progression': [329.63, 415.30, 493.88, 659.25],  # E-G#-B-E
                'melody_notes': [659.25, 739.99, 830.61, 987.77, 1108.73],  # E5-F#5-G#5-B5-C#6
                'tempo': 110,  # BPM
                'style': 'orchestral_whimsical',
                'dynamics': 'mezzo_forte'
            },
            'disgust': {
                'name': 'Unsettling Dissonance',
                'description': 'Atonal composition with uncomfortable harmonies',
                'key': 'Atonal',
                'chord_progression': [196.00, 233.08, 277.18, 311.13],  # G-Bb-C#-Eb
                'melody_notes': [392.00, 466.16, 554.37, 622.25, 698.46],  # G4-A#4-C#5-Eb5-F5
                'tempo': 90,  # BPM
                'style': 'atonal_unsettling',
                'dynamics': 'mezzo_piano'
            },
            'neutral': {
                'name': 'Peaceful Ambience',
                'description': 'Calm ambient soundscape with gentle harmonies',
                'key': 'C Major',
                'chord_progression': [261.63, 329.63, 392.00, 523.25],  # C-E-G-C
                'melody_notes': [523.25, 587.33, 659.25, 698.46, 783.99],  # C5-D5-E5-F5-G5
                'tempo': 80,  # BPM
                'style': 'ambient_peaceful',
                'dynamics': 'mezzo_piano'
            }
        }
        
        theme = emotion_themes.get(emotion, emotion_themes['neutral'])
        logger.info(f"🎼 Creating '{theme['name']}' - {theme['description']}")
        
        # Generate cinematic composition
        audio = self._compose_cinematic_piece(t, theme, duration)
        
        return audio

    def _compose_cinematic_piece(self, t, theme, duration):
        """Compose a cinematic piece based on the emotion theme."""
        import numpy as np
        
        audio = np.zeros_like(t)
        sample_rate = 44100
        
        # Extract theme parameters
        chord_progression = theme['chord_progression']
        melody_notes = theme['melody_notes']
        tempo_bpm = theme['tempo']
        style = theme['style']
        
        # Calculate timing
        beat_duration = 60.0 / tempo_bpm  # seconds per beat
        measure_duration = beat_duration * 4  # 4/4 time signature
        
        # Create different layers based on style
        if style == 'orchestral_upbeat':
            audio += self._create_orchestral_layer(t, chord_progression, melody_notes, tempo_bpm, 'upbeat')
        elif style == 'piano_ballad':
            audio += self._create_piano_layer(t, chord_progression, melody_notes, tempo_bpm)
        elif style == 'orchestral_dramatic':
            audio += self._create_dramatic_layer(t, chord_progression, melody_notes, tempo_bpm)
        elif style == 'atmospheric_dark':
            audio += self._create_atmospheric_layer(t, chord_progression, melody_notes, tempo_bpm)
        elif style == 'orchestral_whimsical':
            audio += self._create_whimsical_layer(t, chord_progression, melody_notes, tempo_bpm)
        elif style == 'atonal_unsettling':
            audio += self._create_unsettling_layer(t, chord_progression, melody_notes, tempo_bpm)
        else:  # ambient_peaceful
            audio += self._create_ambient_layer(t, chord_progression, melody_notes, tempo_bpm)
        
        return audio

    def _create_orchestral_layer(self, t, chords, melody, tempo, mood='balanced'):
        """Create orchestral-style audio layer."""
        import numpy as np
        
        audio = np.zeros_like(t)
        beat_duration = 60.0 / tempo
        
        # String section (sustained chords)
        for i, chord_freq in enumerate(chords):
            chord_start = i * beat_duration * 2  # 2 beats per chord
            chord_mask = (t >= chord_start) & (t < chord_start + beat_duration * 2)
            
            # Create rich chord with overtones
            chord_wave = 0.3 * np.sin(2 * np.pi * chord_freq * t)  # Root
            chord_wave += 0.2 * np.sin(2 * np.pi * chord_freq * 1.25 * t)  # Major third
            chord_wave += 0.15 * np.sin(2 * np.pi * chord_freq * 1.5 * t)  # Perfect fifth
            chord_wave += 0.1 * np.sin(2 * np.pi * chord_freq * 2 * t)  # Octave
            
            # Apply envelope
            envelope = np.ones_like(t)
            if mood == 'upbeat':
                envelope *= (1 + 0.1 * np.sin(2 * np.pi * tempo / 60 * t))  # Rhythmic pulse
            
            audio += chord_wave * chord_mask * envelope
        
        # Melody line (woodwinds/brass)
        melody_rhythm = tempo / 60 * 2  # Melody plays twice as fast
        for i, note_freq in enumerate(melody):
            note_start = i * beat_duration / 2
            note_duration = beat_duration / 2
            note_mask = (t >= note_start) & (t < note_start + note_duration)
            
            # Create melody note with vibrato
            vibrato = 1 + 0.05 * np.sin(2 * np.pi * 6 * t)  # 6Hz vibrato
            melody_wave = 0.25 * np.sin(2 * np.pi * note_freq * t) * vibrato
            
            # Add harmonics for richness
            melody_wave += 0.1 * np.sin(2 * np.pi * note_freq * 2 * t)
            melody_wave += 0.05 * np.sin(2 * np.pi * note_freq * 3 * t)
            
            audio += melody_wave * note_mask
        
        return audio

    def _create_piano_layer(self, t, chords, melody, tempo):
        """Create piano ballad-style audio layer."""
        import numpy as np
        
        audio = np.zeros_like(t)
        beat_duration = 60.0 / tempo
        
        # Piano chords (arpeggiated)
        for i, chord_freq in enumerate(chords):
            chord_start = i * beat_duration * 4  # 4 beats per chord
            
            # Arpeggiated pattern
            arp_notes = [chord_freq, chord_freq * 1.25, chord_freq * 1.5, chord_freq * 2]
            for j, arp_freq in enumerate(arp_notes):
                note_start = chord_start + j * beat_duration
                note_mask = (t >= note_start) & (t < note_start + beat_duration * 2)
                
                # Piano-like attack and decay
                attack_time = 0.1
                decay_factor = np.exp(-(t - note_start) / (beat_duration * 0.8))
                envelope = np.where(note_mask, decay_factor, 0)
                
                piano_wave = 0.4 * np.sin(2 * np.pi * arp_freq * t)
                piano_wave += 0.2 * np.sin(2 * np.pi * arp_freq * 2 * t)  # Octave
                piano_wave += 0.1 * np.sin(2 * np.pi * arp_freq * 3 * t)  # Fifth
                
                audio += piano_wave * envelope
        
        # Melody (right hand)
        for i, note_freq in enumerate(melody):
            note_start = i * beat_duration
            note_duration = beat_duration * 1.5
            note_mask = (t >= note_start) & (t < note_start + note_duration)
            
            # Piano melody with expression
            decay_factor = np.exp(-(t - note_start) / note_duration)
            envelope = np.where(note_mask, decay_factor, 0)
            
            melody_wave = 0.3 * np.sin(2 * np.pi * note_freq * t)
            melody_wave += 0.15 * np.sin(2 * np.pi * note_freq * 2 * t)
            
            audio += melody_wave * envelope
        
        return audio

    def _create_dramatic_layer(self, t, chords, melody, tempo):
        """Create dramatic orchestral layer."""
        import numpy as np
        
        audio = np.zeros_like(t)
        beat_duration = 60.0 / tempo
        
        # Powerful brass chords
        for i, chord_freq in enumerate(chords):
            chord_start = i * beat_duration * 2
            chord_mask = (t >= chord_start) & (t < chord_start + beat_duration * 2)
            
            # Brass-like sound with rich harmonics
            brass_wave = 0.4 * np.sin(2 * np.pi * chord_freq * t)
            brass_wave += 0.3 * np.sin(2 * np.pi * chord_freq * 1.5 * t)
            brass_wave += 0.2 * np.sin(2 * np.pi * chord_freq * 2 * t)
            brass_wave += 0.1 * np.sin(2 * np.pi * chord_freq * 3 * t)
            
            # Add dramatic swells
            swell = 1 + 0.3 * np.sin(2 * np.pi * 0.5 * (t - chord_start))
            
            audio += brass_wave * chord_mask * swell
        
        # Dramatic melody with accents
        for i, note_freq in enumerate(melody):
            note_start = i * beat_duration / 2
            note_duration = beat_duration
            note_mask = (t >= note_start) & (t < note_start + note_duration)
            
            # Strong attack with sustain
            attack = np.where((t >= note_start) & (t < note_start + 0.1), 
                            (t - note_start) / 0.1, 1)
            envelope = np.where(note_mask, attack, 0)
            
            dramatic_wave = 0.35 * np.sin(2 * np.pi * note_freq * t)
            dramatic_wave += 0.2 * np.sin(2 * np.pi * note_freq * 1.5 * t)
            dramatic_wave += 0.15 * np.sin(2 * np.pi * note_freq * 2 * t)
            
            audio += dramatic_wave * envelope
        
        return audio

    def _create_atmospheric_layer(self, t, chords, melody, tempo):
        """Create dark atmospheric layer."""
        import numpy as np
        
        audio = np.zeros_like(t)
        
        # Dark ambient pads
        for chord_freq in chords:
            # Very low frequencies for ominous feeling
            low_freq = chord_freq / 4
            pad_wave = 0.2 * np.sin(2 * np.pi * low_freq * t)
            pad_wave += 0.15 * np.sin(2 * np.pi * low_freq * 1.5 * t)
            
            # Add tremolo for unease
            tremolo = 1 + 0.1 * np.sin(2 * np.pi * 4 * t)
            audio += pad_wave * tremolo
        
        # Sparse, eerie melody
        beat_duration = 60.0 / tempo
        for i, note_freq in enumerate(melody):
            if i % 3 == 0:  # Play only every third note for sparseness
                note_start = i * beat_duration * 2
                note_duration = beat_duration * 3
                note_mask = (t >= note_start) & (t < note_start + note_duration)
                
                # Eerie sound with slow attack
                attack_time = 1.0
                attack = np.where((t >= note_start) & (t < note_start + attack_time),
                                (t - note_start) / attack_time, 1)
                envelope = np.where(note_mask, attack, 0)
                
                eerie_wave = 0.15 * np.sin(2 * np.pi * note_freq * t)
                eerie_wave += 0.1 * np.sin(2 * np.pi * note_freq * 1.1 * t)  # Slight detuning
                
                audio += eerie_wave * envelope
        
        return audio

    def _create_whimsical_layer(self, t, chords, melody, tempo):
        """Create whimsical, playful layer."""
        import numpy as np
        
        audio = np.zeros_like(t)
        beat_duration = 60.0 / tempo
        
        # Light, bouncy accompaniment
        for i, chord_freq in enumerate(chords):
            chord_start = i * beat_duration * 2
            
            # Staccato chords
            for beat in range(4):
                note_start = chord_start + beat * beat_duration / 2
                note_duration = beat_duration / 4  # Short, staccato
                note_mask = (t >= note_start) & (t < note_start + note_duration)
                
                staccato_wave = 0.25 * np.sin(2 * np.pi * chord_freq * t)
                staccato_wave += 0.15 * np.sin(2 * np.pi * chord_freq * 2 * t)
                
                audio += staccato_wave * note_mask
        
        # Playful melody with ornaments
        for i, note_freq in enumerate(melody):
            note_start = i * beat_duration / 2
            note_duration = beat_duration / 2
            note_mask = (t >= note_start) & (t < note_start + note_duration)
            
            # Add grace notes and trills
            grace_freq = note_freq * 1.125  # Major second above
            grace_duration = beat_duration / 16
            grace_mask = (t >= note_start) & (t < note_start + grace_duration)
            
            # Main note
            playful_wave = 0.3 * np.sin(2 * np.pi * note_freq * t)
            # Grace note
            grace_wave = 0.2 * np.sin(2 * np.pi * grace_freq * t)
            
            audio += playful_wave * note_mask + grace_wave * grace_mask
        
        return audio

    def _create_unsettling_layer(self, t, chords, melody, tempo):
        """Create unsettling, dissonant layer."""
        import numpy as np
        
        audio = np.zeros_like(t)
        beat_duration = 60.0 / tempo
        
        # Dissonant clusters
        for i, chord_freq in enumerate(chords):
            chord_start = i * beat_duration * 3
            chord_mask = (t >= chord_start) & (t < chord_start + beat_duration * 3)
            
            # Create dissonant cluster
            cluster_wave = 0.2 * np.sin(2 * np.pi * chord_freq * t)
            cluster_wave += 0.2 * np.sin(2 * np.pi * chord_freq * 1.1 * t)  # Minor second
            cluster_wave += 0.15 * np.sin(2 * np.pi * chord_freq * 1.4 * t)  # Tritone
            cluster_wave += 0.1 * np.sin(2 * np.pi * chord_freq * 1.7 * t)  # Minor seventh
            
            # Add beating effect from close frequencies
            beating = 1 + 0.2 * np.sin(2 * np.pi * 2 * t)  # 2Hz beating
            
            audio += cluster_wave * chord_mask * beating
        
        # Uncomfortable melody intervals
        for i, note_freq in enumerate(melody):
            note_start = i * beat_duration
            note_duration = beat_duration * 1.5
            note_mask = (t >= note_start) & (t < note_start + note_duration)
            
            # Microtonal detuning for discomfort
            detune_factor = 1.03  # Slightly sharp
            unsettling_wave = 0.2 * np.sin(2 * np.pi * note_freq * detune_factor * t)
            unsettling_wave += 0.15 * np.sin(2 * np.pi * note_freq * 0.97 * t)  # Slightly flat
            
            audio += unsettling_wave * note_mask
        
        return audio

    def _create_ambient_layer(self, t, chords, melody, tempo):
        """Create peaceful ambient layer."""
        import numpy as np
        
        audio = np.zeros_like(t)
        
        # Gentle pad sounds
        for chord_freq in chords:
            pad_wave = 0.15 * np.sin(2 * np.pi * chord_freq * t)
            pad_wave += 0.1 * np.sin(2 * np.pi * chord_freq * 1.5 * t)
            pad_wave += 0.08 * np.sin(2 * np.pi * chord_freq * 2 * t)
            
            # Gentle breathing effect
            breath = 1 + 0.05 * np.sin(2 * np.pi * 0.2 * t)  # 0.2Hz breathing
            audio += pad_wave * breath
        
        # Soft melody
        beat_duration = 60.0 / tempo
        for i, note_freq in enumerate(melody):
            note_start = i * beat_duration * 2
            note_duration = beat_duration * 4
            note_mask = (t >= note_start) & (t < note_start + note_duration)
            
            # Soft attack and release
            attack_time = 2.0
            release_time = 2.0
            attack = np.where((t >= note_start) & (t < note_start + attack_time),
                            (t - note_start) / attack_time, 1)
            release = np.where((t >= note_start + note_duration - release_time) & (t < note_start + note_duration),
                             1 - (t - (note_start + note_duration - release_time)) / release_time, 1)
            envelope = np.where(note_mask, attack * release, 0)
            
            ambient_wave = 0.2 * np.sin(2 * np.pi * note_freq * t)
            ambient_wave += 0.1 * np.sin(2 * np.pi * note_freq * 2 * t)
            
            audio += ambient_wave * envelope
        
        return audio

    def generate_emotion_statistics(self, photo_paths):
        """Generate emotion statistics from the processed photos"""
        emotion_counts = {}
        total_photos = 0

        for photo_path in photo_paths:
            try:
                img = cv2.imread(photo_path)
                if img is None:
                    continue

                # Extract emotion from the text overlay
                # Assuming format: "EMOTION (XX%)"
                text = photo_path.split('_')[-1].split('.')[0]  # Get filename without extension
                if '(' in text:
                    emotion = text.split('(')[0].strip().lower()
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                    total_photos += 1
            except Exception as e:
                logger.error(f"Error processing {photo_path}: {str(e)}")
                continue

        return emotion_counts 