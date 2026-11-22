<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

![BC-250 SFTP Tools](../assets/sftp/bc250-sftp-tools.webp){ .app-logo }

# BC-250 SFTP Tools

SFTP Tools moves files between your computer and another one over SSH. It also manages the SSH server (`sshd`) of a
**BC-250** running **Bazzite**. It has two tabs:

- **SFTP Client:** your folders on the left, the server's on the right. You upload and download files and whole
  folders. It has a transfer queue, a speed limit and a choice of what to do when a file already exists.
- **Server Manager:** you connect to a Bazzite host and see whether `sshd` runs. You start or stop it, and edit
  `/etc/ssh/sshd_config`. You can also start or stop `sshd` on this computer, to make it the host.

The app is a client. Install it on the computer you connect **from**. The host you connect **to** only needs a
reachable `sshd`. It does not need the app.

The app does not change how the board runs. The Server Manager changes the SSH server of the host you connect to.
It asks before it saves. It starts or stops the SSH server of this computer only when you press its button.

## What it needs

- Python 3.10 or newer. The installer makes the app's own virtual environment with PyQt6 and
  [paramiko](https://www.paramiko.org/) in it. The suite's shared environment stays as it is.
- On the host you connect to: `sshd` running, and the firewall open for it. [Set up the host](#set-up-the-host)
  has the commands.
- On the host, an SSH server that signs with SHA-2. That is OpenSSH 7.2 from 2016 or newer, as on every current
  system. The app refuses an older server that only offers SHA-1 (`ssh-rsa`). It also refuses an RSA key that can
  only sign with SHA-1.
- Optional: `paplay`, for the beep when a transfer completes. Without it the app uses Qt's beep.

## Using it

1. Fill in the host, the port (22), your user name and either a password or the path of a private key. A key is
   the better choice. With a key, the password field holds the key's passphrase.
2. Press **Connect** in the window's header. The first time, the app shows the server's fingerprint and asks
   whether you trust it. Yes adds it to `~/.ssh/known_hosts`. No makes no connection.
3. Double-click folders to open them, or type a path. Select files or folders and press **Upload →** or
   **← Download**, or use the right-click menu. Ctrl-click and Shift-click select more than one. The right-click
   menu also deletes, after a question.
4. To upload, you can also drag files and folders onto the server's list. Drag them from the list on the left or
   from your file manager. They go to the server folder that is open. The app copies them and never moves them.
5. The lists under the folders show the queued, failed and successful transfers. When you close the app while
   transfers wait or run, it asks first, because closing cancels them.

The window's header shows three states:

- your own system
- the SFTP connection
- the state of `sshd` on the host that the Server Manager connects to

Beside them, **Connect** connects the SFTP Client, and disconnects it again. The password advice stands at the
right of the password field. As you type, it shows what is still missing. After the app logs an error, a red dot
appears at the right of the title. Click it to open the log.

**Profiles.** *Save profile* keeps the host, port, user name and key path under a name. The app never saves
passwords or key passphrases. The SFTP Client and the Server Manager each have their own list.

**Passwords.** The password rules are only advice. A good password has at least 8 characters, one capital, one
number and one special character. When a password without a key misses one of them, the app warns that the
password is unsafe. It connects all the same. An empty password is fine with a key.

### Server Manager

When you connect, the app asks `sshd` whether it is running or stopped. The button next to it starts or stops it.
*Load sshd_config* reads `/etc/ssh/sshd_config` into the editor. *Save sshd_config* does four things:

1. It checks the text with `sshd -t`.
2. It keeps the old file as `sshd_config.bak`.
3. It installs the new file.
4. It offers to restart `sshd`.

These steps need `sudo` without a password on the host (`sudo -n`). When the host asks for one, the app shows
the error and changes nothing.

**This computer as host.** Under the status, the Server Manager shows the state of `sshd` on the computer the app
runs on. **Start sshd here** or **Stop sshd here** stands next to it. Use it to make this computer the host that
another computer connects to.

- **Start** turns `sshd` on, so it also starts at boot. When firewalld runs and ssh is not open yet, Start opens
  the firewall for ssh. These are the commands of [Set up the host](#set-up-the-host).
- **Stop** stops `sshd` and keeps it from starting at boot. It leaves the firewall as it is.

Both ask for your password in the system's password dialog. When `openssh-server` is not installed, the app says
which command installs it. After that command, you restart the computer yourself.

## Set up the host

Do this once on the Bazzite host, in a terminal. You can also press **Start sshd here** in the app on the host
itself.

```sh
rpm -q openssh-server                       # if it is missing: sudo rpm-ostree install openssh-server, then reboot
sudo systemctl enable --now sshd
systemctl is-active sshd                    # prints "active"
sudo firewall-cmd --list-services           # ssh must be in the list
sudo firewall-cmd --permanent --add-service=ssh && sudo firewall-cmd --reload   # only when it is not
hostname -I                                 # the address to connect to
```

Use the address of the Ethernet or Wi-Fi connection that is in use, and your account name (`whoami`). Keep both
computers on a network you trust. Do not forward port 22 from your router to the internet.

A recent Fedora-based system can have password logins turned off. To turn them on, create a file for it and
restart `sshd`:

```sh
echo "PasswordAuthentication yes" | sudo tee /etc/ssh/sshd_config.d/10-enable-passwords.conf
sudo systemctl restart sshd
```

### Logging in with a key

On the computer you connect from:

```sh
ssh-keygen -t ed25519
ssh-copy-id yourusername@HOST_ADDRESS
```

Then give the key's path in the app (`~/.ssh/id_ed25519`). Or leave the field empty to use your SSH agent and the
default keys.

## On Windows

SFTP Tools for Windows is an app of its own. It reaches the board from a Windows computer. Its download, its
documentation and its releases are at [github.com/RobertoTorino/sftp-tool](https://github.com/RobertoTorino/sftp-tool).

## Settings

*Edit, Settings…* has these settings. The app saves them when you press Save.

| Setting | Default | What it does |
|---|---|---|
| Default local folder | home folder | The folder the left list starts in. |
| Connection timeout | 10 s | How long to wait for a connection (1 to 300). |
| TCP keep-alive | 15 s | How often to send a keep-alive on an idle connection (1 to 300). |
| Reconnect attempts, delay | 2, 5 s | Retries after a failed connection (0 to 10), and the pause between them (1 to 60). A host key you have not trusted is never retried. |
| Show hidden files | off | Lists names that start with a dot. |
| If file exists | Ask | Ask, overwrite or skip when the target exists. With more than one file, *Ask* offers to do the same for the others. |
| Speed limit | unlimited | Limit in KB/s per transfer. |
| File size format | Auto, 1 decimal, separator | Auto (1024-based), binary (KiB, MiB) or decimal (KB, MB). You also choose 0 to 3 decimals, and whether thousands get a separator. |
| Date format, time format | YYYY-MM-DD, HH:MM:SS | How the app shows modification times. |
| Beep when transfer completes | on | The desktop's *complete* sound. |
| Filter invalid Windows filename characters | on | A download replaces `< > : " \| ? *` in names with the replacement character (`_`), so you can copy the files to Windows later. |
| Enable SFTP compression | on | zlib compression on the connection. |
| Auto-clear successful transfers | on | Removes finished transfers from the list. |
| Preserve file modification times | on | Downloaded files get the remote modification time. |
| Log level, max log file size | INFO, 10 MB | What the app logs, and the size at which the log rotates. The app keeps three old logs. |

## Files

| What | Where |
|---|---|
| The app | `~/.local/share/bc250-sftp-tools/app` and its virtual environment `.../venv` |
| Settings | `~/.config/bc250-sftp-tools/settings.json`. Delete it to go back to the defaults. |
| Profiles | `~/.config/bc250-sftp-tools/profiles.json` (SFTP Client) and `server-profiles.json` (Server Manager). Only you can read them. |
| The log | `~/.local/share/bc250-sftp-tools/bc250-sftp-tools.log` |
| Trusted hosts | `~/.ssh/known_hosts`, never removed by the app |

## Uninstalling

Use the portal, or run `./install.sh --uninstall` from the app's folder. That removes the app and its
environment. It keeps your settings, profiles and log. `./install.sh --uninstall --purge` removes those too.
