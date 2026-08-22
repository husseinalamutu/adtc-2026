# Running the SME Copilot on a Windows laptop

Written for the demo recording on a Dell Latitude 5420 (i7-1185G7, 8 GB), but it applies to
any Windows machine. **No `pip install` is needed** — the app and the finance engine use only
the Python standard library, including the spreadsheet reader.

Everything below runs offline once the two downloads are done.

---

## 0. What you need

| Requirement | Notes |
|---|---|
| **Python 3.10+** | `python --version`. If missing: python.org installer, tick **"Add python.exe to PATH"**. |
| **The repo** | `git clone`, or download the ZIP from GitHub. |
| **The model** (1.93 GB) | Downloaded once, then offline forever. |
| **llama.cpp for Windows** | Prebuilt binaries — no compiling. |

---

## 1. Get the code

```powershell
cd $HOME\Desktop
git clone https://github.com/husseinalamutu/adtc-2026
cd adtc-2026
```

No Git? Download `https://github.com/husseinalamutu/adtc-2026/archive/refs/heads/main.zip`,
unzip it, and `cd` into the folder.

## 2. Get the model

`submission/download_model.sh` is a bash script. On Windows, either run it in **Git Bash**, or
just download the file directly:

```powershell
mkdir -Force submission\model
curl.exe -L -o submission\model\alamz-tech-sme-copilot-Q4_K_M.gguf `
  "https://huggingface.co/HusseinAlamutu/alamz-tech-sme-copilot-gguf/resolve/main/alamz-tech-sme-copilot-Q4_K_M.gguf?download=true"
```

Check it landed at roughly 1.93 GB:

```powershell
(Get-Item submission\model\alamz-tech-sme-copilot-Q4_K_M.gguf).Length / 1GB
```

## 3. Get llama.cpp (prebuilt — do not compile)

From https://github.com/ggml-org/llama.cpp/releases download the latest
**`llama-bXXXX-bin-win-avx2-x64.zip`** and unzip it to `C:\llama\`.

> Use the **avx2** build, not the audit's SIMD-disabled build. The audit build exists to make
> the competition's speed comparison fair; it is ~8–10× slower and would make the demo crawl.
> For the video you want what a real user would actually run.
>
> If your machine has a working Vulkan driver, the **`-bin-win-vulkan-x64`** build can use the
> Iris Xe integrated GPU and may be considerably faster — worth trying, since "runs on
> integrated graphics" is exactly the hardware story this project is about.

## 4. Start the model server

In **terminal 1**, from the repo root:

```powershell
C:\llama\llama-server.exe -m submission\model\alamz-tech-sme-copilot-Q4_K_M.gguf --port 8080 -c 2048 -t 4
```

Wait for `server is listening`. Leave this window open.

## 5. Start the app

In **terminal 2**, from the repo root:

```powershell
python demo\app\server.py
```

You should see `ALAMZ TECH SME Copilot demo -> http://127.0.0.1:8090`.

## 6. Open it

Browse to **http://127.0.0.1:8090**. Then, before recording:

- **Unplug the network.** Everything keeps working — that is the whole claim.
- Drag in a **real spreadsheet** (`.xlsx` or `.csv`). Columns can be named anything sensible;
  date / description / amount / type / counterparty are matched automatically.
- Click through all five business questions once so nothing surprises you on camera.

---

## Verify it is genuinely working

```powershell
curl.exe -s -X POST http://127.0.0.1:8090/api/business -H "Content-Type: application/json" -d "{\"kind\":\"health\"}"
```

Returns JSON with a `verified` block (computed figures) and a `narrative` (the model's
explanation). If `narrative` is null, the app is fine but llama-server is not running — the
figures are still correct, because the engine computes them without the model.

## If something breaks

| Symptom | Cause | Fix |
|---|---|---|
| `python` not recognised | Not on PATH | Reinstall Python with "Add to PATH" ticked, or use `py` instead |
| `ModuleNotFoundError: finance` | Wrong working directory | Run from the **repo root**, not from `demo\app` |
| App works, `narrative` is null | llama-server not up | Check terminal 1 for `server is listening` |
| Narration takes 30 s+ | Wrong llama.cpp build | You have the SIMD-disabled build — use the **avx2** release |
| "No data loaded yet" | Nothing imported | Drag in a spreadsheet, or click *load the sample business* |

## Measuring this machine's real speed

```powershell
C:\llama\llama-bench.exe -m submission\model\alamz-tech-sme-copilot-Q4_K_M.gguf -p 512 -n 128 -t 4
```

Expect roughly **15–25 tok/s** with the avx2 build on a Tiger Lake i7. (The 2.75 tok/s figure
in the report is the *audit's* deliberately de-optimized build — a different measurement for a
different purpose.)
