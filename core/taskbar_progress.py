# SubExtract Studio — Developed by NoYz
# Windows Taskbar Progress Bar Integration via ITaskbarList3 COM API

import sys
import ctypes
from ctypes import wintypes, c_void_p, c_ulonglong, c_int, Structure, byref, WINFUNCTYPE, cast, POINTER
import uuid

# Taskbar progress flags
TBPF_NOPROGRESS = 0x0
TBPF_INDETERMINATE = 0x1
TBPF_NORMAL = 0x2
TBPF_ERROR = 0x4
TBPF_PAUSED = 0x8

class TaskbarProgress:
    """Provides native Windows 10/11 taskbar progress bar indicators."""

    def __init__(self):
        self.available = False
        self._taskbar = None
        self._set_progress_val = None
        self._set_progress_state = None

        if sys.platform == "win32":
            self._init_com()

    def _init_com(self):
        try:
            class GUID(Structure):
                _fields_ = [
                    ('Data1', wintypes.DWORD),
                    ('Data2', wintypes.WORD),
                    ('Data3', wintypes.WORD),
                    ('Data4', wintypes.BYTE * 8)
                ]
                def __init__(self, guid_str):
                    super().__init__()
                    u = uuid.UUID(guid_str)
                    self.Data1 = u.time_low
                    self.Data2 = u.time_mid
                    self.Data3 = u.time_hi_version
                    for i, b in enumerate(u.bytes[8:]):
                        self.Data4[i] = b

            CLSID_TaskbarList = GUID('{56FDF344-FD6D-11D0-958A-006097C9A090}')
            IID_ITaskbarList3 = GUID('{EA1AFB91-9E28-4B86-90E9-9E9F8A5EEFAF}')

            ole32 = ctypes.oledll.ole32
            ole32.CoInitialize(None)

            taskbar = c_void_p()
            hr = ole32.CoCreateInstance(
                byref(CLSID_TaskbarList),
                None,
                1,  # CLSCTX_INPROC_SERVER
                byref(IID_ITaskbarList3),
                byref(taskbar)
            )

            if hr == 0 and taskbar.value:
                self._taskbar = taskbar
                vtbl = cast(taskbar, POINTER(POINTER(c_void_p))).contents

                SetProgressValueType = WINFUNCTYPE(ctypes.c_long, c_void_p, wintypes.HWND, c_ulonglong, c_ulonglong)
                self._set_progress_val = SetProgressValueType(vtbl[9])

                SetProgressStateType = WINFUNCTYPE(ctypes.c_long, c_void_p, wintypes.HWND, c_int)
                self._set_progress_state = SetProgressStateType(vtbl[10])

                self.available = True
        except Exception as e:
            self.available = False

    def set_value(self, hwnd, current, total=100):
        """Sets progress value on Windows taskbar icon."""
        if not self.available or not hwnd:
            return
        try:
            c_hwnd = wintypes.HWND(int(hwnd))
            if current > 0:
                self._set_progress_state(self._taskbar, c_hwnd, TBPF_NORMAL)
                self._set_progress_val(self._taskbar, c_hwnd, int(current), int(total))
            else:
                self._set_progress_state(self._taskbar, c_hwnd, TBPF_NOPROGRESS)
        except Exception:
            pass

    def set_state(self, hwnd, state_name="normal"):
        """Sets progress state (normal, error, paused, indeterminate, off)."""
        if not self.available or not hwnd:
            return
        try:
            c_hwnd = wintypes.HWND(int(hwnd))
            mapping = {
                "off": TBPF_NOPROGRESS,
                "normal": TBPF_NORMAL,
                "error": TBPF_ERROR,
                "paused": TBPF_PAUSED,
                "indeterminate": TBPF_INDETERMINATE
            }
            flag = mapping.get(state_name, TBPF_NORMAL)
            self._set_progress_state(self._taskbar, c_hwnd, flag)
        except Exception:
            pass

    def clear(self, hwnd):
        """Clears taskbar progress."""
        if not self.available or not hwnd:
            return
        try:
            c_hwnd = wintypes.HWND(int(hwnd))
            self._set_progress_state(self._taskbar, c_hwnd, TBPF_NOPROGRESS)
        except Exception:
            pass
