"""One guarded pointer click inside a freshly observed FL Studio window."""
import argparse
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import time
import numpy as np
from PIL import Image, ImageGrab


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot', type=Path, required=True)
    p.add_argument('--x', type=int, required=True)
    p.add_argument('--y', type=int, required=True)
    p.add_argument('--button', choices=['left', 'right'], default='left')
    p.add_argument('--wait-foreground', type=float, default=25)
    p.add_argument('--diagnostic', action='store_true')
    a = p.parse_args()
    root = Path(__file__).resolve().parent.parent
    snapshot = a.snapshot.resolve()
    if not snapshot.is_relative_to(root):
        raise SystemExit('Snapshot must be inside the working folder')
    meta = json.loads(snapshot.read_text(encoding='utf-8'))
    age = (datetime.now(timezone.utc)-datetime.fromisoformat(meta['captured_utc'])).total_seconds()
    if age < 0 or age > 90 or meta['process'] != 'fl64.exe':
        raise SystemExit('A fresh FL snapshot is required (under 90 seconds)')
    image_path = Path(meta['image']).resolve()
    if not image_path.is_relative_to(root):
        raise SystemExit('Image outside working folder')
    if hashlib.sha256(image_path.read_bytes()).hexdigest() != meta['sha256']:
        raise SystemExit('Snapshot image changed')
    width, height = meta['size']
    if not (0 <= a.x < width and 0 <= a.y < height):
        raise SystemExit('Point outside snapshot')
    u = ctypes.WinDLL('user32', use_last_error=True)
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    d = ctypes.WinDLL('dwmapi', use_last_error=True)
    u.SetProcessDpiAwarenessContext.argtypes = [ctypes.c_void_p]
    u.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    u.GetForegroundWindow.restype = wintypes.HWND
    u.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    u.IsWindow.argtypes = [wintypes.HWND]
    u.WindowFromPoint.argtypes = [wintypes.POINT]
    u.WindowFromPoint.restype = wintypes.HWND
    u.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
    k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    k.OpenProcess.restype = wintypes.HANDLE
    k.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    k.CloseHandle.argtypes = [wintypes.HANDLE]
    d.DwmGetWindowAttribute.argtypes = [wintypes.HWND,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD]
    hwnd = meta['hwnd']
    if not u.IsWindow(hwnd):
        raise SystemExit('Stale FL handle')
    def pid_of(handle):
        value = wintypes.DWORD()
        u.GetWindowThreadProcessId(handle, ctypes.byref(value))
        return value.value
    pid = pid_of(hwnd)
    if pid != meta['pid']:
        raise SystemExit('FL process changed')
    handle = k.OpenProcess(0x1000, False, pid)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        name = ctypes.create_unicode_buffer(32768)
        size = wintypes.DWORD(len(name))
        if not k.QueryFullProcessImageNameW(handle,0,name,ctypes.byref(size)):
            raise ctypes.WinError(ctypes.get_last_error())
        if Path(name.value).name.lower() != 'fl64.exe':
            raise SystemExit('Target is not FL64.exe')
    finally:
        k.CloseHandle(handle)
    if a.diagnostic:
        adv = ctypes.WinDLL('advapi32', use_last_error=True)
        adv.OpenProcessToken.argtypes=[wintypes.HANDLE,wintypes.DWORD,ctypes.POINTER(wintypes.HANDLE)]
        adv.GetTokenInformation.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(wintypes.DWORD)]
        adv.GetSidSubAuthorityCount.argtypes=[ctypes.c_void_p]
        adv.GetSidSubAuthorityCount.restype=ctypes.POINTER(ctypes.c_ubyte)
        adv.GetSidSubAuthority.argtypes=[ctypes.c_void_p,wintypes.DWORD]
        adv.GetSidSubAuthority.restype=ctypes.POINTER(wintypes.DWORD)
        def integrity(process_id):
            ph=k.OpenProcess(0x1000,False,process_id)
            token=wintypes.HANDLE()
            try:
                if not adv.OpenProcessToken(ph,8,ctypes.byref(token)):
                    return {'error':ctypes.get_last_error()}
                length=wintypes.DWORD()
                adv.GetTokenInformation(token,25,None,0,ctypes.byref(length))
                data=ctypes.create_string_buffer(length.value)
                if not adv.GetTokenInformation(token,25,data,length.value,ctypes.byref(length)):
                    return {'error':ctypes.get_last_error()}
                sid=ctypes.cast(data,ctypes.POINTER(ctypes.c_void_p))[0]
                n=adv.GetSidSubAuthorityCount(sid)[0]
                return hex(adv.GetSidSubAuthority(sid,n-1)[0])
            finally:
                if token: k.CloseHandle(token)
                if ph: k.CloseHandle(ph)
        point=wintypes.POINT()
        u.GetCursorPos(ctypes.byref(point))
        print(json.dumps({'FL_integrity':integrity(pid),'python_integrity':integrity(os.getpid()),'cursor':[point.x,point.y],'input_sent':False}))
        return
    deadline = time.monotonic()+min(30,max(0,a.wait_foreground))
    while pid_of(u.GetForegroundWindow()) != pid and time.monotonic() < deadline:
        time.sleep(.1)
    if pid_of(u.GetForegroundWindow()) != pid:
        raise SystemExit('FL is not foreground')
    rect = wintypes.RECT()
    if d.DwmGetWindowAttribute(hwnd,9,ctypes.byref(rect),ctypes.sizeof(rect)) != 0:
        raise SystemExit('Cannot verify FL bounds')
    bounds = [rect.left,rect.top,rect.right,rect.bottom]
    if bounds != meta.get('window_bbox',meta['bbox']):
        raise SystemExit('FL window moved since snapshot')
    origin_x,origin_y = meta['bbox'][:2]
    x,y = origin_x+a.x,origin_y+a.y
    if pid_of(u.WindowFromPoint(wintypes.POINT(x,y))) != pid:
        raise SystemExit('Point is covered by a different application')
    r = 14
    crop = (max(0,a.x-r),max(0,a.y-r),min(width,a.x+r),min(height,a.y+r))
    expected = np.asarray(Image.open(image_path).convert('RGB').crop(crop)).astype(np.int16)
    live_box = (origin_x+crop[0],origin_y+crop[1],origin_x+crop[2],origin_y+crop[3])
    current = np.asarray(ImageGrab.grab(bbox=live_box,all_screens=True).convert('RGB')).astype(np.int16)
    error = float(np.abs(current-expected).mean())
    if error > 18:
        raise SystemExit('Observed target changed; take a fresh screenshot (pixel error '+str(error)+')')
    class MI(ctypes.Structure):
        _fields_=[('dx',wintypes.LONG),('dy',wintypes.LONG),('mouseData',wintypes.DWORD),('dwFlags',wintypes.DWORD),('time',wintypes.DWORD),('dwExtraInfo',ctypes.c_size_t)]
    class U(ctypes.Union):
        _fields_=[('mi',MI)]
    class INPUT(ctypes.Structure):
        _fields_=[('type',wintypes.DWORD),('u',U)]
    u.SendInput.argtypes=[wintypes.UINT,ctypes.POINTER(INPUT),ctypes.c_int]
    u.SendInput.restype=wintypes.UINT
    down,up=(2,4) if a.button=='left' else (8,16)
    if not u.SetCursorPos(x,y):
        raise ctypes.WinError(ctypes.get_last_error())
    if pid_of(u.GetForegroundWindow()) != pid or pid_of(u.WindowFromPoint(wintypes.POINT(x,y))) != pid:
        raise SystemExit('Target changed before click')
    events=(INPUT*2)()
    events[0].u.mi.dwFlags=down
    events[1].u.mi.dwFlags=up
    sent_down=u.SendInput(1,ctypes.byref(events[0]),ctypes.sizeof(INPUT))
    time.sleep(.08)
    sent_up=u.SendInput(1,ctypes.byref(events[1]),ctypes.sizeof(INPUT))
    if sent_down!=1 or sent_up!=1:
        raise SystemExit('Click outcome unknown: input counts '+str((sent_down,sent_up)))
    time.sleep(.25)
    print(json.dumps({'action':'click','button':a.button,'snapshot_point':[a.x,a.y],'screen_point':[x,y],'pid':pid,'pixel_error':error}))


if __name__=='__main__':
    main()
