#!/usr/bin/env bash
set -euo pipefail

out=src/voicebot/stt/proto
uv run python -m grpc_tools.protoc -I proto --python_out="$out" --pyi_out="$out" --grpc_python_out="$out" proto/recognition.proto
sed -i 's/^import recognition_pb2 as recognition__pb2/from voicebot.stt.proto import recognition_pb2 as recognition__pb2/' "$out/recognition_pb2_grpc.py"
