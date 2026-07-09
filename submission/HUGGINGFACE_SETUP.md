# Publishing the model to Hugging Face (one-time)

The 1.93 GB GGUF can't live in git (GitHub's 100 MB limit). Hugging Face hosts it — this is both
the required Gate-1 delivery mechanism (`download_model.sh` fetches from here) and how the Dell
gets the file to benchmark. The model is not secret; a public HF repo is expected and safe.

## 1. Create a free HF account + token (2 min) — YOU do this
1. Sign up at https://huggingface.co/join
2. Create an access token: https://huggingface.co/settings/tokens → "New token" → type **Write** →
   copy it (looks like `hf_...`).

## 2. Upload (run on the Mac) — I can run this once you paste the token
```bash
cd ~/Desktop/Development/adtc-2026
pip install -q huggingface_hub hf_transfer
export HF_TOKEN=hf_xxx            # your Write token
export HF_HUB_ENABLE_HF_TRANSFER=1
python3 - <<'PY'
from huggingface_hub import HfApi
api = HfApi()
repo = "husseinalamutu/adtc-sme-copilot-gguf"       # created if missing
api.create_repo(repo, repo_type="model", private=False, exist_ok=True)
api.upload_file(
    path_or_fileobj="submission/model/adtc-sme-copilot-Q4_K_M.gguf",
    path_in_repo="adtc-sme-copilot-Q4_K_M.gguf",
    repo_id=repo, repo_type="model",
)
print("uploaded ->", f"https://huggingface.co/{repo}")
PY
```
`hf_transfer` chunks the upload (resumable), which matters on this flaky network — same reason it
worked for downloads. If it stalls, just re-run; it resumes.

> **Security:** the `HF_TOKEN` is a secret — it's only ever an env var here, never committed
> (`.env`/keys stay git-ignored). The uploaded GGUF itself is public and safe (it's the artifact
> the judges evaluate).

## 3. On the Dell — get the model with no USB, no login
```bash
git clone https://github.com/husseinalamutu/adtc-2026.git
cd adtc-2026
pip install -q huggingface_hub hf_transfer   # or: python -m pip ...
bash submission/download_model.sh            # pulls the GGUF into submission/model/
bash docker/run_local_emulation.sh           # real x86 TPS
```

If you pick a different HF repo name, update `HF_REPO` in `submission/download_model.sh` (and tell
me — I'll also mirror it into REPORT.md later).
