# Driver Monitoring System

A basic DMS prototype that detects drowsiness by tracking eye closure using MediaPipe.

<img width="804" height="629" alt="Screenshot 2026-01-23 030746" src="https://github.com/user-attachments/assets/83d946c7-d6d6-4164-b248-eec8a1eb2f1c" />

## Setup

```bash
pip install -r requirements.txt
```

## Running

Just run:
```bash
python dms.py
```

## How it works

I'm using MediaPipe Face Mesh which gives 468 facial landmarks. From those, I extract the 6 key points around each eye and calculate the Eye Aspect Ratio (EAR).

<img width="767" height="641" alt="Screenshot 2026-01-23 030808" src="https://github.com/user-attachments/assets/6eecfef2-a6c1-4c4d-9d47-dc34e32aa9ea" />

**EAR formula:** `(vertical_dist1 + vertical_dist2) / (2 * horizontal_dist)`

When eyes are open, EAR is around 0.25-0.3. When closed, it drops below 0.2. I set the threshold at 0.21 after testing - 0.2 was triggering too often on normal blinks.

If EAR stays below threshold for 15 consecutive frames (~0.5 seconds), it triggers an alert.

## Performance

Tested on my laptop CPU (no GPU):
- **Latency:** 35-45ms per frame
- **FPS:** ~25-30
- Works in real-time

## What works

- Face detection is solid, handles different angles pretty well
- EAR metric reliably detects when eyes close
- Runs fine on CPU
- Works with my glasses on

## What doesn't work

**Sunglasses:** Complete failure. Can't see eyes = can't calculate EAR.

**Bad lighting:** Struggles in dark conditions. MediaPipe needs decent lighting to track landmarks accurately.

**Extreme head turns:** If you turn your head more than ~60 degrees, it loses the face. This is a problem because drivers do look at mirrors.

**Motion blur:** Fast head movements cause tracking issues. In a real car with bumps/vibrations this would be worse.

**Only detects drowsiness:** Doesn't detect other distractions like phone usage, looking at passengers, etc.

## What I'd improve

Given more time:

1. **PERCLOS metric** - Industry standard is "percentage of eye closure" over a 60-second window. More robust than just counting frames.

2. **Head pose estimation** - MediaPipe can do this. Would help detect when driver is looking away (at phone, passenger, etc).

3. **Per-person calibration** - The 0.21 threshold works for me but might need adjustment for different people. Could do a quick calibration at startup.

4. **Better temporal filtering** - Right now a single frame with low EAR increments the counter. Should probably use a sliding window or exponential smoothing to reduce false positives.

5. **IR camera support** - For night driving, would need to work with infrared cameras. Current RGB-based approach won't work in the dark.
