# GraphPaper

PDF utilities for graph paper, dot grids, and calendar generation.

## Installing uv

[uv](https://docs.astral.sh/uv/) is a fast Python package and project manager.

### Mac

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or with Homebrew:

```bash
brew install uv
```

### Windows

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or with winget:

```powershell
winget install astral-sh.uv
```

## Setup

Clone the repo and let uv handle the Python version and dependencies:

```bash
git clone <repo-url>
cd graphpaper
uv sync
```

## Scripts

| Script | Description | Usage |
|---|---|---|
| `dot.py` | Generate dot grid paper (7.5mm spacing, gray dots) | `uv run dot.py` |
| `week_grid.py` | 8-week landscape planner grid starting from a given date | `uv run week_grid.py` |
| `trading_calendar.py` | NYSE trading calendar (11x17, with holidays marked) | `uv run trading_calendar.py` |
| `combine.py` | Merge multiple PDFs from the command line | `uv run combine.py file1.pdf file2.pdf ...` |
| `combine_drop.py` | GUI drag-and-drop PDF combiner | `uv run combine_drop.py` |
| `duplicate.py` | Duplicate every page in one or more PDFs | `uv run duplicate.py file.pdf` |
| `interleave.py` | Insert a dot grid page after each page of a PDF | `uv run interleave.py file.pdf` |
| `nopasswd.py` | Remove password protection from a PDF | `uv run nopasswd.py file.pdf` |

All scripts output PDFs to the current working directory.

## License

[MIT](LICENSE)
