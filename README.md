# Blueqat backend using qulacs
Unofficial release :)

Develop branch of blueqat is required.

## Usage

```py
from blueqat import Circuit()
import qulacs_blueqat_backend
qulacs_blueqat_backend.register_backend()

Circuit().h[0].run()
```
