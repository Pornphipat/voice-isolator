import os
import numpy as np
from pydub import AudioSegment
import noisereduce as nr
from concurrent.futures import ThreadPoolExecutor
import math

def process_chunk(chunk_samples, sr, max_val):
    # Normalize
    samples_float = chunk_samples.astype(np.float32) / max_val
    # Reduce noise
    reduced = nr.reduce_noise(y=samples_float, sr=sr, stationary=True)
    return reduced

def process_audio(input_path, output_path):
    """
    Load an audio file, reduce background noise in parallel chunks, and save it.
    """
    print(f"Starting processing: {os.path.basename(input_path)}")
    
    # 1. Load audio file
    audio = AudioSegment.from_file(input_path)
    audio_mono = audio.set_channels(1)
    sr = audio_mono.frame_rate
    sample_width = audio_mono.sample_width
    max_val = float(2**(8 * sample_width - 1))
    
    # 2. Convert to numpy
    samples = np.array(audio_mono.get_array_of_samples())
    
    # 3. Parallel Chunk Processing (Option C)
    # Process in 30-second chunks
    chunk_size_samples = sr * 30 
    num_chunks = math.ceil(len(samples) / chunk_size_samples)
    
    print(f"File duration: {len(audio)/1000:.2f}s | Chunks: {num_chunks}")
    
    chunks = []
    for i in range(num_chunks):
        start = i * chunk_size_samples
        end = min((i + 1) * chunk_size_samples, len(samples))
        chunks.append(samples[start:end])
    
    processed_chunks = [None] * num_chunks
    
    # Use ThreadPoolExecutor for parallel processing
    # Adjust max_workers based on CPU cores (default is fine)
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_chunk, chunks[i], sr, max_val): i for i in range(num_chunks)}
        
        completed = 0
        for future in futures:
            idx = futures[future]
            processed_chunks[idx] = future.result()
            completed += 1
            # Option A: Progress indicator in terminal
            percent = (completed / num_chunks) * 100
            print(f"Progress: {percent:.1f}% ({completed}/{num_chunks} chunks)")

    # 4. Reassemble
    full_signal = np.concatenate(processed_chunks)
    
    # Convert back to original bit depth
    reduced_noise_int = (full_signal * max_val).astype(samples.dtype)
    
    processed_audio = AudioSegment(
        reduced_noise_int.tobytes(),
        frame_rate=sr,
        sample_width=sample_width,
        channels=1
    )
    
    # 5. Export
    ext = os.path.splitext(output_path)[1][1:].lower()
    export_format = "ipod" if ext in ['m4a', 'm4p'] else ext
    processed_audio.export(output_path, format=export_format)
    print(f"Successfully saved: {output_path}")

if __name__ == "__main__":
    # Simple test if run directly
    import sys
    if len(sys.argv) > 2:
        process_audio(sys.argv[1], sys.argv[2])
        print(f"Processed {sys.argv[1]} and saved to {sys.argv[2]}")
