#!/usr/bin/env python3
from pathlib import Path
import base64
import gzip

payload_path = Path(__file__).with_name("build_phase3_5.py.gz.b64")
source = gzip.decompress(base64.b64decode(payload_path.read_text(encoding="ascii"))).decode("utf-8")
namespace = {"__name__": "__main__", "__file__": __file__}
exec(compile(source, __file__ + "<payload>", "exec"), namespace, namespace)
