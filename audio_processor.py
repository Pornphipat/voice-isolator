import os
import numpy as np
from pydub import AudioSegment
import noisereduce as nr
import io

def process_audio(input_path, output_path):
    """
    Load an audio file, reduce background noise, and save it to the output path.
    """
    # 1. Load audio file using pydub (handles various formats)
    audio = AudioSegment.from_file(input_path)
    
    # Convert to mono if it's stereo (noisereduce works best or requires specific handling for multi-channel)
    # For simplicity, we'll process as mono
    audio_mono = audio.set_channels(1)
    
    # 2. Convert pydub audio to numpy array
    # pydub stores data as raw bytes, so we need to convert based on sample_width
    samples = np.array(audio_mono.get_array_of_samples())
    
    # Normalize samples to float32 between -1 and 1
    # samples.itemsize gives bytes per sample (e.g., 2 for 16-bit)
    max_val = float(2**(8 * audio_mono.sample_width - 1))
    samples_float = samples.astype(np.float32) / max_val
    
    # 3. Perform noise reduction
    # stationary=True assumes the noise is constant throughout the clip
    reduced_noise = nr.reduce_noise(y=samples_float, sr=audio_mono.frame_rate, stationary=True)
    
    # 4. Convert back to pydub audio
    # Denormalize back to original bit depth
    reduced_noise_int = (reduced_noise * max_val).astype(samples.dtype)
    
    # Create new AudioSegment from the processed samples
    processed_audio = AudioSegment(
        reduced_noise_int.tobytes(),
        frame_rate=audio_mono.frame_rate,
        sample_width=audio_mono.sample_width,
        channels=1
    )
    
    # 5. Export the processed audio
    processed_audio.export(output_path, format=os.path.splitext(output_path)[1][1:])

if __name__ == "__main__":
    # Simple test if run directly
    import sys
    if len(sys.argv) > 2:
        process_audio(sys.argv[1], sys.argv[2])
        print(f"Processed {sys.argv[1]} and saved to {sys.argv[2]}")
