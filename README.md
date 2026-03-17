# 👾 My Projects

A centralized portfolio repository containing various specialized tools and security utilities. 

> **Note**: This is a mono-repo. You can choose to clone the entire repository or use Git's **sparse-checkout** to download only a specific tool to save space and time.

---

## 🛠️ Project List

| # | Tool | Description | Status |
|---|------|-------------|--------|
| 1 | [🛡️ code-scanner](./code-scanner) | Supply Chain Security & Reachability Analysis | ✅ Stable |

---

## 📦 How to Clone (Optimized)

If you only want a specific tool (e.g., `code-scanner`) without downloading everything else:

```bash
# 1. Initialize a sparse clone
git clone --filter=blob:none --sparse https://github.com/VIKAS-KUMAR-10/My_Projects.git
cd My_Projects

# 2. Pull only the tool you need
git sparse-checkout set code-scanner
```

---

## 🔗 Author
**[VIKAS-KUMAR-10](https://github.com/VIKAS-KUMAR-10)**
