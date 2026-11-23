<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

<span class="page-icon">:material-clipboard-list-outline:</span>

# Basic tests and additional requirements to streamline the Qt GUI version

### Start the GUI: 
Use this command when the requirements changed:
```bash
python3 -m venv python && python/bin/pip install -r requirements.txt && python/bin/python -m board_test  
```    
Use this command when they did not change:
```bash
python3 -m venv python && python/bin/python -m board_test  
```       

---

### Vulkan Memtest
Bazzite does not include memtest_vulkan, so download it on the BC-250 board.
Get the Linux x86_64 build from [https://github.com/GpuZelenograd/memtest_vulkan/releases](https://github.com/GpuZelenograd/memtest_vulkan/releases).
Extract it, then run this command:
```bash
chmod +x memtest_vulkan && mv memtest_vulkan ~/.local/bin/         
```

#### Example stress tests
```bash
sudo ./test-board.sh --only=41 --stress=120
sudo ./test-board.sh --only=18,19,22,35,41 --stress=30
```

### Stress test with max CU's
With the most CUs unlocked, run the stress test (41) with memtest_vulkan for at least 300s.
```bash
sudo ./test-board.sh --only=41 --stress=600
``` 
This run takes 10 minutes.
If it runs with no stall, 36 CUs are stable.
If your board can handle 40 CUs, the run confirms those instead.
It reports the following:
* Whether the clock holds.
* When the board is hot.
* How much power it draws.
* Whether the extra CUs produce VRAM errors.

---

### Measure your baseline
1. Install the tools with `rpm-ostree install stress-ng`, then restart.
2. Put the vkpeak binary from [https://github.com/nihui/vkpeak/releases](https://github.com/nihui/vkpeak/releases) in `~/.local/bin`.
3. `chmod +x vkpeak && mv vkpeak ~/.local/bin/`
4. Undo any CU unlock with a restart, so the board has 24 CUs. Close games and applications.
5. On the Performance page, check **Save as baseline (stock board only)** and run test 42.
6. It saves the benchmark results as `bench-baseline.json`.
7. Unlock your CU's and run test 42 again for the comparison.

---

### Game detection
The FPS reading needs MangoHud logging.
Set this once in `~/.config/MangoHud/MangoHud.conf`:
```
output_folder=~/mangohud-logs
autostart_log=1
log_interval=500
```
* Create that log folder, and make sure MangoHud is on for the game.
* MangoHud writes one log file per session, so delete old ones now and then.
* Without logging, you still get the game name and its CPU/GPU %.

#### Limits to check on the board
* It only works in Desktop Mode, because the GUI isn't visible in Game Mode.
* With fix-metrics on, the GPU % comes from the governor's patched GPU sensor file.
* To check the GPU %, compare the status bar's GPU % with MangoHud's while a game runs.
* The Hz in the status bar is for the screen the GUI window is on.

#### Here's how to check that the app can read mangohud:         
1. Start the game and check that the overlay appears. Right Shift + F12 shows or hides it.
2. Check that MangoHud writes a log while you play: `ls -lt ~/mangohud-logs | head -3`
3. The newest .csv file should grow. If no file appears, press Left Shift + F2 to start logging. You can also check that the config MangoHud actually uses holds autostart_log=1: `grep -E "output_folder|autostart_log" ~/.config/MangoHud/MangoHud.conf`
4. Open the app and check **Live** in the status bar. It should show the game title, its CPU and GPU share, and the FPS.
5. If the app shows no FPS while the overlay shows, output_folder probably points somewhere other than where the app looks.

---

### The buttons
* **Show graph** next to the stress settings (test 41) plots the latest stress CSV.
* It has panels for clocks, temperatures, GPU busy, GPU power, GPU memory, fan, GPU voltage and load average.
* A line above the panels lists the peaks.
* You can pick older stress runs from a list.
* **Show graph** on the Performance page (test 42) shows the benchmark history as bar charts per run.
* It has panels for the score against your stock baseline, GPU FP32, CPU multi- and single-thread, VRAM bandwidth and GPU clock.
* The labels on the bars look like "#2 40CU 12T", so CU and core unlocks sit side by side.

#### Show Logs
* A **Show graph** button appears whenever the selected file is a CSV.
* A CSV the app doesn't know gets one panel per number column.

#### Behavior
In the graph window:
* Drag to zoom in.
* Right-click to zoom out.
* Hover to see values.
* **Save as PNG…** saves all panels as one image.

---

### NVMe tests (10)

#### PCIe link: 
* The test shows the speed and width the link runs at, against what the drive and the slot support.
* It warns if the link is slower than both. The cause is often a poor contact.
* It notes when the slot is the limit.
* It shows the highest MB/s the link allows.

#### DRAM cache: 
* DRAM-less drives ask to borrow system RAM, a "host memory buffer".
* The kernel logs it when it grants that buffer.
* The test reads both.
* If neither shows up, the drive has its own DRAM.
* It warns if the drive asked for a buffer but never got one.

#### SMART health: 
* Critical warnings
* Media errors
* Spare blocks
* Wear %
* Data written
* Temperature against the drive's own limit
* Time spent throttling
* Unsafe shutdowns, where every hard lockup counts

### NVMe tests (43)
`disk speed (--disk-bench, or --disk-write=GiB)`
* Read is the default and writes nothing. It reads 4 GiB from the system disk and compares the result with the link's highest speed.
* With fio installed, it also measures random 4K reads.
* For Write, check **Disk speed test (43): also test writes** and set a size. Then the test does the following:
    * It writes a temporary file in `/var/tmp` 256 MiB at a time.
    * It logs the speed and drive temperature for each chunk, and deletes the file afterward.
    * Where the speed drops sharply, it reports that as the size of the fast SLC cache.
    * If the drive was hot at that moment, it reports throttling instead.
    * It checks for enough free space first.
    * It stops if the drive reaches its critical temperature.
    * It turns `btrfs` compression off for the file, so the result is real.
* **Show graph** plots write speed and temperature against GiB written.
* As safeguards, you confirm before it starts, and Run all never includes it.

The SMART, DRAM and random-read results on the board need tools.
Install them first with `rpm-ostree install nvme-cli fio`, then restart.

Then run the test with this flag:
```bash
sudo ./test-board.sh --only=10,43 --disk-write=16
```

---

### Internet speed test (test 44)
* It's opt-in with `--speedtest` and sits on the Network page.
* It uses Ookla's speedtest.
* If Ookla's tool isn't installed, it falls back to speedtest-cli.

It reports these results:
* Download and upload speed, idle latency and jitter.
* Latency while downloading and uploading.
* A rise of more than 100 ms is a warning, with a hint to turn on SQM in the router. Such a rise is bufferbloat.
* Packet loss above 1% is a warning.
* Which connection it uses, Ethernet or Wi-Fi, and its link speed.
* A 100 Mbit link warns about the cable.
* A download close to the link speed says the port is the limit.
* A note when a VPN is in the path.

It uses about 1 GB of data.
So it's never part of Run all, and it asks for confirmation first.
Each run goes into bc250-speedtest-history.csv.
**Show graph** compares all runs on these values:
* Speeds
* Idle versus loaded latency
* Jitter
* Packet loss

To try it on the board, download the `Linux x86_64 .tgz` from `speedtest.net/apps/cli`.
Put `speedtest` in `~/.local/bin`:
```bash
chmod +x speedtest && mv speedtest ~/.local/bin/  
```
Then run `--only=44 --speedtest`.

---

Do a CLI run with the benchmark and --speedtest.
It confirms that stress-ng, vkpeak and speedtest still give results when they run as your user.

```bash
sudo ./test-board.sh --bench --speedtest
```
