import pkgutil
from pathlib import Path

for _, file, _ in pkgutil.iter_modules([str(Path(__file__).parent.absolute())]):
    __import__(file, globals(), level=1)
