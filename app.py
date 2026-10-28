import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from jass_design_resource_library.ui import main
if __name__ == "__main__":
    raise SystemExit(main())
