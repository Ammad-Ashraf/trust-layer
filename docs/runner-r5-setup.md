# R5 Part A: setting up `tlsubject` on Israr's laptop (by hand)

Why: Study B runs log in to Israr's Max account. If they share a login with the runner's own Claude session, the login can break partway through a run. A second Linux user, `tlsubject`, with its **own** login to the same account, avoids that (decisions 0010, 0018).

**Before you start, get Israr's OK for:**
- a second user account on his laptop;
- typing his `sudo` password;
- logging that user into **his** Claude Max account. Study B's 36 runs (Dec–Jan) count against his usage limits, alongside his own use.

Israr types the password and does the Claude login himself, or tells you to.

Use a terminal logged in as `israr`. Lines starting with `sudo` ask for Israr's password.

## 1. Bring Israr's checkout up to date

```bash
cd /home/israr/Documents/Ammad-Particle-Physics/trust-layer
git checkout main && git pull --ff-only
rm -rf external/collider-bench/agents/simple_ledger      # R2's hand copy; now comes from the fork
git submodule sync && git submodule update --init
git -C external/collider-bench log --oneline -1           # must show d8ac871
```

## 2. Create the user and let it run in the background

```bash
sudo useradd -m -s /bin/bash tlsubject
grep tlsubject /etc/subuid /etc/subgid                   # must print 2 lines (Podman needs them)
sudo loginctl enable-linger tlsubject
```

If the `grep` prints nothing: `sudo usermod --add-subuids 200000-265535 --add-subgids 200000-265535 tlsubject`.

## 3. Let the runner session act as `tlsubject` (and only that, never root)

```bash
echo 'israr ALL=(tlsubject) NOPASSWD: ALL' | sudo tee /etc/sudoers.d/tlsubject
sudo chmod 440 /etc/sudoers.d/tlsubject
sudo visudo -c                                           # must say "parsed OK"
```

## 4. Let `tlsubject` read the repo (read-only)

```bash
sudo apt install -y acl                                  # usually already installed
sudo setfacl -m u:tlsubject:x /home/israr /home/israr/Documents /home/israr/Documents/Ammad-Particle-Physics
sudo setfacl -R -m u:tlsubject:rX /home/israr/Documents/Ammad-Particle-Physics/trust-layer
```

## 5. Become `tlsubject` and set it up

```bash
sudo -iu tlsubject
export XDG_RUNTIME_DIR=/run/user/$(id -u)
git config --global --add safe.directory '*'
git config --global user.name "tlsubject"
git config --global user.email "tlsubject@localhost"
git clone --no-hardlinks --recurse-submodules /home/israr/Documents/Ammad-Particle-Physics/trust-layer ~/trust-layer
git -C ~/trust-layer/external/collider-bench log --oneline -1   # must show d8ac871
curl -fsSL https://claude.ai/install.sh | bash -s 2.1.326
exit
```

## 6. Download the benchmark image for `tlsubject`

Each Linux user keeps its own copy of the image (several GB), so this takes a while.

```bash
sudo -iu tlsubject
export XDG_RUNTIME_DIR=/run/user/$(id -u)
podman pull ghcr.io/dfaroughy/lhc-bench@sha256:8820ecd3b8cada3d37e5e16214bedc53b07cbc58ea83ef104f1795e3f9b3c01f
```

## 7. Log in to Claude as `tlsubject` (Israr does this)

Still in the `tlsubject` shell:

```bash
claude --version          # must say 2.1.326; if "not found", run `exit`, then `sudo -iu tlsubject` again
claude
```

- Pick any theme. When asked how to log in, choose the **Claude account with subscription** option.
- It prints a long URL. Open it in a browser where **Israr** is signed in to claude.ai, click **Authorize**, copy the code it shows, and paste it into the terminal.
- When you reach the prompt, type `/exit`. **Don't** add MCP servers, plugins, connectors or settings.

Then `exit` to go back to `israr`.

## 8. Hand over to the runner

Tell the runner's Claude session: **"Read `docs/runner-tasks.md` and do the open tasks."** It does R5 Part B (the login-clash test) and reports back in `report.md`.
