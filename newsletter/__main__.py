"""Allow `python -m newsletter` execution."""
from newsletter.cli import main
import sys

sys.exit(main())
