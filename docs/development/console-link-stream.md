<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

<span class="page-icon">:material-video-wireless-outline:</span>

# PS Remote Play: the stream's threads

This page shows how BC-250 PS Remote Play keeps picture, sound and controller in step during a stream. It explains
why Python's global interpreter lock (the GIL) matters for that, and how you measure it. For the app itself, see its
[chapter in the wiki](../apps/consoles.md).

## The threads

| Thread | Language | What it does |
|---|---|---|
| Receiver | Rust (native core) | Receives the stream's packets, checks and decrypts them, and rebuilds frames with FEC. It also acknowledges the packets and sends the congestion reports. |
| Feedback | Rust (native core) | Sends the controller state at least every 200 ms, and the button history. |
| Stream | Python | Takes frames and sound from the receiver (`next_event`) and decodes them with the native core and FFmpeg. It hands the newest picture to the window and the sound to the sound buffer. |
| Window (GUI) | Python + Qt | Draws the picture. It uploads it as a texture and turns Y'CbCr into RGB in a shader. It also feeds the sound output, because Qt's `QAudioSink` pulls from the sound buffer in this thread. |
| Controller | Python | Reads the controllers through SDL3 every 4 ms and hands the state to the feedback thread. |
| Control | Python | Answers the session's heartbeats. |
| Statistics | Python | Writes the statistics file, once a second. |

## The GIL

Only one thread runs Python code at a time. That is the thread that holds the GIL. A call into the native core keeps
the GIL unless the core lets go of it (`py.detach` in PyO3). While the call keeps it, every other Python thread
waits.

Decoding a 1080p H.264 frame in software takes about 5 ms on the BC-250. At 60 frames per second that is about
300 ms of every second. While the decoder kept the GIL, three things went wrong:

- The window could not draw or feed the sound output. The output's buffer holds only 30 ms. When it ran empty, the
  sound stuttered.
- The window drew pictures late and unevenly. The picture lagged and stuttered.
- The controller thread's reads waited. The controller felt slow.

The native core now lets go of the GIL in the video decoder, the picture copy (`image()`) and the sound decoder.
They work on their own data and touch no Python object meanwhile. The test ran on a BC-250 with a PS4 Pro at
1080p and 60 frames per second. The game was Lumines Remastered, started from the Steam shortcut, full screen, on a
network cable. The stutter in sound and picture went away, and the controller felt more responsive.

The rule for the native core is that a slow call lets go of the GIL. A slow call is any call that can take more
than a fraction of a millisecond. Slow calls include:

- decoding
- copying a picture
- waiting for a packet
- a network handshake

`next_event` and `connect` let go of it already.

## Lost packets

When a frame loses a few of its packets, the receiver (Rust, `video.rs`) rebuilds it from the console's spare FEC
packets. Sometimes a frame loses too many packets, or never arrives. Then two things keep the decoder from drawing
garbage. Both come from chiaki-ng, the program the protocol code is ported from:

- `bitstream.rs` reads each frame's first slice header. It tells whether the frame is a key frame, and which earlier
  frame it refers to.
- The receiver keeps the last 16 frames it handed out.

The receiver does not hand out a frame whose reference is not among those 16. For HEVC, it may point the frame at
an older reference instead. After a frame that FEC could not rebuild, the receiver asks the console for a key frame
(IDRREQUEST). It skips the frames until the key frame comes. When none has come after 60 frames, it asks again. The
receiver also tells the console about every missing frame (CORRUPTFRAME). The console may answer by referring to an
older frame.

You can try this on a network that loses nothing. The direct start takes a hidden option that drops a share of the
video packets on arrival: `bc250-console-link --stream "<console>" --simulate-loss 5` (percent). The terminal shows
the log as it happens. The statistics file has the recovery per second.

## Measuring it

Each stream writes a statistics file, one line per second, in `~/.local/state/bc250-console-link/streams/`. The code
is in `stream_stats.py`. The app's [chapter in the wiki](../apps/consoles.md#when-it-does-not-work) explains the
file for users. Look for these fields:

| Field | Healthy | What a bad value points to |
|---|---|---|
| `in … longest gap` | about 17 ms at 60 fps | Frames arrive in bursts. The cause is the network or the console. |
| `recovery` | all 0 | These count frames FEC could not rebuild, key frames asked for, frames skipped until one came, and frames without their reference. Nonzero values mean the network loses packets (Wi-Fi, a busy link). The receiver handles a few now and then. Many point to the network. |
| `decode avg / max` | well under the frame time, 16.7 ms at 60 fps | The decoder is too slow for the resolution. Try a lower resolution, a hardware decoder (VA-API), or decoder threads. |
| `shown / skipped` | shown close to the frames in, few skipped | The window draws slower than the frames come. |
| `age avg / max` | a few ms | This is the time from decoder to drawing. A high value means the window is busy. |
| `window late max` | a few ms | Something blocks the GUI thread. It can be a native call that keeps the GIL, or a slow paint. |
| `sound buffer / gaps` | buffer 10 to 40 ms, gaps 0 | A gap means the window did not feed the sound output in time. See the window's fields. |
| `controller … longest gap` | about 4 to 6 ms | Something blocks the controller thread. |
| `cpu … busiest core / threads` | the busiest core well below 100% | One thread is at its limit. More cores do not help a single thread. |
| `disk wait / swapped` | 0 | The board is short of memory and swaps. A slow drive makes it worse. |

The same holds on other hardware. A device with a hardware video decoder (VA-API) decodes cheaply. Copying the
picture out still costs time. A larger picture costs more everywhere. Compare a file from each device. The fields
above show which part falls behind.
