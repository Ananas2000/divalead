"""Capture only the visible foreground FL Studio window; no input or network."""

import argparse
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

from PIL import ImageGrab


WORKSPACE = Path(__file__).resolve().parent.parent
EXPECTED_PROCESS = "fl64.exe"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hwnd", type=int, required=True,
                        help="Exact FL window id returned by the Computer Use window list")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--wait-foreground", type=float, default=0,
                        help="Wait this many seconds for FL to regain foreground after approval")
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(WORKSPACE) or output.suffix.lower() != ".png":
        raise SystemExit("Output must be a PNG inside local-fl-matching")

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    dwmapi = ctypes.WinDLL("dwmapi", use_last_error=True)
    user32.SetProcessDpiAwarenessContext.argtypes = [ctypes.c_void_p]
    user32.SetProcessDpiAwarenessContext.restype = wintypes.BOOL
    user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    user32.IsWindow.argtypes = [wintypes.HWND]
    user32.IsWindow.restype = wintypes.BOOL
    user32.IsIconic.argtypes = [wintypes.HWND]
    user32.IsIconic.restype = wintypes.BOOL
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.GetWindowRect.restype = wintypes.BOOL
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD,
                                                  wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    dwmapi.DwmGetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD,
                                            ctypes.c_void_p, wintypes.DWORD]
    dwmapi.DwmGetWindowAttribute.restype = ctypes.c_long

    hwnd = wintypes.HWND(args.hwnd)
    if not user32.IsWindow(hwnd):
        raise SystemExit("Stale window id; select a fresh returned FL window")
    if user32.IsIconic(hwnd):
        raise SystemExit("FL Studio is minimized")
    deadline = time.monotonic() + max(0, min(args.wait_foreground, 30))
    while user32.GetForegroundWindow() != args.hwnd and time.monotonic() < deadline:
        time.sleep(0.1)
    if user32.GetForegroundWindow() != args.hwnd:
        raise SystemExit("FL Studio must be the foreground window")

    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    process = kernel32.OpenProcess(0x1000, False, pid.value)
    if not process:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        image_path = ctypes.create_unicode_buffer(32768)
        size = wintypes.DWORD(len(image_path))
        if not kernel32.QueryFullProcessImageNameW(process, 0, image_path, ctypes.byref(size)):
            raise ctypes.WinError(ctypes.get_last_error())
        if Path(image_path.value).name.lower() != EXPECTED_PROCESS:
            raise SystemExit("Refusing capture: selected window does not belong to FL64.exe")
    finally:
        kernel32.CloseHandle(process)

    rect = wintypes.RECT()
    result = dwmapi.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(rect), ctypes.sizeof(rect))
    if result != 0 and not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        raise ctypes.WinError(ctypes.get_last_error())
    bbox = (rect.left, rect.top, rect.right, rect.bottom)
    if rect.right <= rect.left or rect.bottom <= rect.top:
        raise SystemExit("Invalid window bounds")
    title = ctypes.create_unicode_buffer(1024)
    user32.GetWindowTextW(hwnd, title, len(title))
    if user32.GetForegroundWindow() != args.hwnd:
        raise SystemExit("Foreground changed before capture; no screenshot saved")
    screenshot = ImageGrab.grab(bbox=bbox, all_screens=True)
    if user32.GetForegroundWindow() != args.hwnd:
        raise SystemExit("Foreground changed during capture; no screenshot saved")
    output.parent.mkdir(parents=True, exist_ok=True)
    screenshot.save(output)
    metadata = {
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "backend": "Pillow ImageGrab / Windows GDI visible desktop crop",
        "hwnd": args.hwnd,
        "pid": pid.value,
        "process": EXPECTED_PROCESS,
        "title": title.value,
        "bbox": bbox,
        "size": screenshot.size,
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "image": str(output),
        "input_sent": False,
    }
    output.with_suffix(".json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
                                          encoding="utf-8")
    print(json.dumps(metadata, ensure_ascii=True))


if __name__ == "__main__":
    main()

