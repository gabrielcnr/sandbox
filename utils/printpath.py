#!/usr/bin/env python
import os

for path in os.getenv("PATH").split(":"):
    print(path)

