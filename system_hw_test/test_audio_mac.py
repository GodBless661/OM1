import os
import osascript          # macOS AppleScript wrapper
import sounddevice as sd  # audio I/O
import soundfile as sf    # read/write audio files

# --------------------------- 1. Load the audio file ---------------------------
filename = "woof.wav"

try:
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"File not found: {filename}")

    # data: np.ndarray, samplerate: int
    data, samplerate = sf.read(filename, dtype="float32")
except FileNotFoundError as e:
    print(e)
    raise SystemExit(1)
except RuntimeError as e:  # soundfile internal error
    print(f"Error reading audio file: {e}")
    raise SystemExit(1)

# --------------------------- 2. Query available devices ---------------------------
try:
    devices = sd.query_devices()
    print("Available audio devices:")
    print(devices)
except Exception as e:
    print(f"Failed to query devices: {e}")
    raise SystemExit(1)

# --------------------------- 3. Set default output device ---------------------------
output_device_name = "External Headphones"   # change to your device name

try:
    # Find the device whose name exactly matches `output_device_name`
    output_idx = next(i for i, dev in enumerate(devices) if dev["name"] == output_device_name)
    # Set (input, output) tuple – we only care about output here
    sd.default.device = (None, output_idx)
    print(f"Default output device set to '{devices[output_idx]['name']}' (index {output_idx})")
except StopIteration:
    print(f"Output device \"{output_device_name}\" not found. Using system default.")
except Exception as e:
    print(f"Error setting output device: {e}")
    raise SystemExit(1)

# --------------------------- 4. Helper to run AppleScript ---------------------------
def run_osascript(cmd: str):
    """Execute AppleScript and raise on error."""
    result, rc = osascript.osascript(cmd)
    if rc != 0:
        raise RuntimeError(f"AppleScript error ({rc}): {result}")
    return result

# --------------------------- 5. Show current volume ---------------------------
try:
    vol_info = run_osascript("get volume settings")
    print("Current volume settings:", vol_info)
except Exception as e:
    print(f"Failed to get volume settings: {e}")

# --------------------------- 6. Set volume to maximum (0-100) ---------------------------
target_volume = 100   # integer between 0 and 100

try:
    run_osascript(f"set volume output volume {target_volume}")
    print(f"Volume set to {target_volume}%")
except Exception as e:
    print(f"Failed to set volume: {e}")

# --------------------------- 7. Unmute -----------------------------------
try:
    run_osascript("set volume without output muted")
    print("Unmuted")
except Exception as e:
    print(f"Failed to unmute: {e}")

# --------------------------- 8. Final verification -----------------------
try:
    print("Final volume state:", run_osascript("get volume settings"))
except Exception as e:
    print(f"Failed to verify final volume state: {e}")

# --------------------------- 9. Play the audio ---------------------------
try:
    sd.play(data, samplerate)   # start playback (non-blocking)
    sd.wait()                   # block until playback finishes
    print("Playback finished successfully")
except Exception as e:
    print(f"Error during playback: {e}")
finally:
    sd.stop()                   # clean up the device
