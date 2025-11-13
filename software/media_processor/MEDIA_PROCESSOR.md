# LED Matrix Media Processor

## Project Overview

A Python-based desktop application that converts various media formats (images, videos, animated GIFs) into grayscale 8-bit bitmap frames suitable for display on a 28x20 pixel LED matrix.

To run in this repo, first `source ./venv/bin/activate` and then `./venv/bin/python -m media_processor.main --help` for help. 

**Target Display:** 28 rows × 20 columns = 560 pixels per frame

**Output Format:** Each frame as a separate grayscale bitmap image file (8-bit, 0-255 values). PNG by default, optional ASCII PGM for plain-text pixel data.

---

## Functionality Requirements

### Input Support
The application must handle the following file formats:
- **Static Images:** `.jpg`, `.jpeg`, `.png`, `.bmp`
- **Animated Images:** `.gif` (all frames)
- **Video Files:** `.mp4`, `.webm`, `.mov`, `.avi`, `.mkv`

### Processing Pipeline
For each input file:
1. **Load** - Detect and load media file (any supported format)
2. **Extract Frames** - Get individual frames (1 for images, N for videos/GIFs)
3. **User Transformations** (future enhancement)
   - Optional cropping to specific region
   - Optional scaling before final resize
4. **Resize** - Scale to exactly 20×28 pixels (width × height)
5. **Convert** - Grayscale conversion (8-bit, 0-255 range)
6. **Export** - Save each frame as separate bitmap file (PNG) or ASCII PGM text

### Output Structure (default)
```
media_processor/output/
├── <filename>/
│   ├── frame_0001.png / frame_0001.pgm
│   ├── frame_0002.png / frame_0002.pgm
│   ├── frame_0003.png / frame_0003.pgm
│   └── ...
└── metadata.json (frame count, fps, dimensions, format)
```

---

## Tech Stack

### Core Dependencies

**1. Pillow (PIL Fork) - v11.x**
- **Purpose:** Image manipulation and processing
- **Why:** Lightweight, pure Python, excellent format support
- **Usage:**
  - Image resizing with quality interpolation
  - Grayscale conversion
  - Cropping operations
  - Loading/saving image formats

**2. imageio - v2.x**
- **Purpose:** Video and animated GIF frame extraction
- **Why:** Clean API, handles multi-frame formats seamlessly
- **Usage:**
  - Read video files frame-by-frame
  - Extract GIF animation frames
  - Unified interface for single/multi-frame media

**3. imageio-ffmpeg - v0.x**
- **Purpose:** FFmpeg binary wrapper for video codec support
- **Why:** Automatically downloads FFmpeg, no system dependencies
- **Usage:**
  - Decodes .mp4, .webm, .mkv, .avi formats
  - Works as imageio plugin (transparent to our code)

**4. numpy - v2.x** (already installed)
- **Purpose:** Array operations
- **Why:** Fast pixel data manipulation, already in project
- **Usage:**
  - Pixel array representation
  - Efficient data type conversions
  - Array slicing for cropping

---

## Architecture Design

### Module Structure

```
software/
├── media_processor/
│   ├── __init__.py
│   ├── loader.py          # Load any media format
│   ├── processor.py       # Resize, grayscale conversion
│   ├── exporter.py        # Save frames to disk
│   └── utils.py           # Helper functions
│   └── output/            # Generated frames directory (default target)
├── tests/                 # Unit tests (future)
├── requirements.txt       # Dependencies
└── MEDIA_PROCESSOR.md     # This document
```

### Processing Pipeline Details

#### Step 1: Media Loading (`loader.py`)
```python
def load_media(filepath: str) -> list[np.ndarray]:
    """
    Load any supported media file and return list of frames.
    
    Returns:
        List of numpy arrays (H, W, C) where C is channels (RGB/RGBA)
        - Single image: list with 1 frame
        - Video/GIF: list with N frames
    """
```

**Implementation approach:**
- Try `imageio.get_reader()` first (multi-frame)
- Fall back to `imageio.imread()` (single frame)
- Return consistent format regardless of input type

#### Step 2: Frame Processing (`processor.py`)
```python
def process_frame(frame: np.ndarray, 
                  target_width: int = 20,
                  target_height: int = 28) -> np.ndarray:
    """
    Convert frame to grayscale 28x20 bitmap.
    
    Args:
        frame: Input frame as numpy array
        target_width: Output width (default 20)
        target_height: Output height (default 28)
    
    Returns:
        Grayscale numpy array (28, 20) dtype uint8
    """
```

**Processing steps:**
1. Convert numpy array to PIL Image: `Image.fromarray(frame)`
2. Resize to (20, 28): `img.resize((20, 28), Image.LANCZOS)`
   - Use LANCZOS for high-quality downsampling
3. Convert to grayscale: `img.convert('L')`
   - 'L' mode = 8-bit pixels (0-255)
4. Convert back to numpy: `np.array(img, dtype=np.uint8)`

#### Step 3: Export (`exporter.py`)
```python
def export_frames(frames: list[np.ndarray], 
                  output_dir: str,
                  base_name: str) -> dict:
    """
    Save frames as individual PNG files.
    
    Returns:
        Metadata dict with frame count, output paths, etc.
    """
```

**File naming convention:**
- Format: `frame_NNNN.png` (zero-padded to 4 digits)
- Example: `frame_0001.png`, `frame_0002.png`, ...
- Supports up to 9999 frames

---

## Implementation Details

### Key Design Decisions

**1. Why imageio over OpenCV?**
- Lighter dependency (~5MB vs ~90MB)
- Simpler API for our use case
- Automatic FFmpeg integration via plugin
- No compilation issues across platforms

**2. Why Pillow for processing?**
- Already handles format conversion well
- Better high-quality interpolation than basic numpy
- Familiar API
- No GPU/OpenCV overhead

**3. Why separate files instead of single binary?**
- Easy to preview individual frames
- Can process/debug specific frames
- Simple to implement
- Later can combine into binary format if needed

**4. Why PNG output?**
- Lossless (preserves exact pixel values)
- Good compression for simple grayscale
- Easy to preview visually
- Compatible with everything

**5. Why ASCII PGM option?**
- Plain-text representation of pixel values (readable in any editor)
- Still compatible with many image viewers
- Useful when transferring literal byte values to microcontroller firmware

### Resize Interpolation

**Options in Pillow:**
- `Image.NEAREST` - Fastest, blocky
- `Image.BILINEAR` - Fast, smooth
- `Image.BICUBIC` - Slower, high quality
- `Image.LANCZOS` - Slowest, highest quality (recommended)

**Recommendation:** Use `LANCZOS` for final output, `BILINEAR` for previews.

### Memory Considerations

For large videos:
- Process one frame at a time (don't load all into memory)
- Use generator/iterator pattern
- Clear frame data after processing

```python
# Good: Memory efficient
for frame in reader:
    processed = process_frame(frame)
    export_frame(processed)
    del frame  # Explicit cleanup

# Bad: Loads entire video
frames = list(reader)  # Could be GB of memory!
```

---

## Usage Examples

### Command Line Interface

```bash
# Process a single image
python main.py input.jpg

# Process a video
python main.py video.mp4

# Process an animated GIF
python main.py animation.gif

# Specify output directory
python main.py input.mp4 --output ./custom_output
```

### Expected Output

```
$ python main.py example.mp4

Loading: example.mp4
Format detected: mp4
Extracting frames... 150 frames found
Processing frames: [████████████████████] 100%
Exported to: output/example/
  - 150 frames (frame_0001.png to frame_0150.png)
  - metadata.json
Done! Total processing time: 3.2s
```

---

## Future Enhancements

### Phase 2: User Controls
- Interactive cropping UI (Tkinter or PyQt6)
- Preview window showing before/after
- Adjustable brightness/contrast
- Region of interest selection

### Phase 3: Dithering
- Floyd-Steinberg dithering for better grayscale
- Ordered dithering patterns
- Threshold adjustments

### Phase 4: Bluetooth Integration
- Connect to LED matrix controller
- Stream frames in real-time
- Frame rate control
- Live preview on LED display

### Phase 5: Format Optimization
- Binary frame format (smaller, faster)
- Run-length encoding for static regions
- Differential encoding between frames
- Pre-compressed animation bundles

---

## Testing Approach

### Test Media Files Needed
```
tests/media/
├── test_image.png          # Static image
├── test_photo.jpg          # JPEG photo
├── test_animation.gif      # Multi-frame GIF
├── test_video.mp4          # Short video (5-10s)
└── test_video.webm         # WebM format
```

### Test Cases
1. **Single image** → Should output 1 frame
2. **Animated GIF** → Should output N frames
3. **Video file** → Should output M frames
4. **Invalid file** → Should handle gracefully
5. **Verify dimensions** → All outputs are 28×20
6. **Verify grayscale** → All outputs are 8-bit (0-255)
7. **Verify format** → All outputs are valid PNG

---

## Development Workflow

### Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import PIL, imageio, numpy; print('All imports successful')"
```

### Incremental Implementation Order

1. **Step 1:** Basic image loading and resizing
   - Load single PNG/JPG
   - Resize to 28×20
   - Convert to grayscale
   - Save as PNG

2. **Step 2:** Multi-frame support
   - Load animated GIF
   - Extract all frames
   - Process each frame
   - Save numbered sequence

3. **Step 3:** Video support
   - Load MP4/WebM via imageio
   - Same processing pipeline
   - Handle longer sequences efficiently

4. **Step 4:** CLI interface
   - Argument parsing
   - Progress indicators
   - Error handling

5. **Step 5:** Polish
   - Metadata export
   - Directory organization
   - Documentation

---

## Technical Specifications

### Input Constraints
- **Max file size:** Limited by available RAM (recommend < 500MB)
- **Max frames:** Limited by disk space (1000 frames ≈ 2-3MB)
- **Supported codecs:** Whatever FFmpeg supports (H.264, VP8, VP9, etc.)

### Output Specifications
- **Frame dimensions:** Exactly 20×28 pixels (width × height)
- **Color depth:** 8-bit grayscale (0-255)
- **File format:** PNG (lossless, indexed grayscale)
- **Naming:** Zero-padded 4-digit numbering
- **Frame size:** ~300-500 bytes per frame (PNG compressed)

### Performance Targets
- **Image processing:** < 0.1s per frame
- **Video processing:** 30-50 FPS throughput
- **Memory usage:** < 200MB for processing

---

## Troubleshooting

### Common Issues

**"Could not find FFmpeg"**
- Solution: `imageio-ffmpeg` should auto-install
- Verify: `python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"`

**"File format not supported"**
- Check file extension
- Try converting with system FFmpeg first
- Verify file isn't corrupted

**"Out of memory" errors**
- Process frames one at a time (don't load all)
- Use generator pattern
- Reduce video length or resolution before processing

**Slow processing**
- Use `Image.BILINEAR` instead of `LANCZOS` for testing
- Process every Nth frame for long videos
- Consider pre-resizing video with FFmpeg

---

## References

- [Pillow Documentation](https://pillow.readthedocs.io/)
- [imageio Documentation](https://imageio.readthedocs.io/)
- [NumPy Documentation](https://numpy.org/doc/)
- LED Matrix Display: 28 rows × 20 columns (see `notes.md`)

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-13  
**Status:** Ready for implementation

