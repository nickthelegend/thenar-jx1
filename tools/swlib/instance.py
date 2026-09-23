"""Dedicated JX1 SolidWorks session management.

Another project (thenar-glasses) may be using a SolidWorks session on this machine. JX1 must never attach
to it, so this module NEVER calls GetActiveObject('SldWorks.Application'). Instead it launches its own
SLDWORKS.exe and binds to it through the Running Object Table moniker "SolidWorks_PID_<pid>".

A guard verifies after launch that GetActiveObject (what other tools use) still resolves to the
pre-existing session; if the new JX1 session hijacked that registration it is closed immediately.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

import pythoncom
import win32com.client as com
from win32com.client import gencache

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "tools" / ".sw_instance.json"
SW_EXE = Path(r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SLDWORKS.exe")
CLASS_MONIKER = "!{666AAEE2-7A21-40FC-B768-2078840A88C3}"
API_DIR = Path(r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS")


def _library(name):
    a = pythoncom.LoadTypeLib(str(API_DIR / (name + ".tlb"))).GetLibAttr()
    return gencache.EnsureModule(a[0], a[1], a[3], a[4])


SW = _library("sldworks")


def rot_entries():
    rot = pythoncom.GetRunningObjectTable()
    ctx = pythoncom.CreateBindCtx(0)
    out = []
    for m in rot.EnumRunning():
        try:
            out.append((m.GetDisplayName(ctx, None), m))
        except pythoncom.com_error:
            pass
    return rot, out


def pid_alive(pid: int) -> bool:
    try:
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout
        return str(pid) in out and "SLDWORKS" in out.upper()
    except Exception:
        return False


def bind_pid(pid: int):
    rot, entries = rot_entries()
    for name, mk in entries:
        if name.lower() == f"solidworks_pid_{pid}".lower():
            obj = rot.GetObject(mk)
            return SW.ISldWorks(obj.QueryInterface(pythoncom.IID_IDispatch))
    return None


def active_object_pid():
    """Process id of the session GetActiveObject resolves to (what other tools attach to). Read-only."""
    try:
        app = SW.ISldWorks(com.GetActiveObject("SldWorks.Application")._oleobj_)
        return app.GetProcessID()
    except pythoncom.com_error:
        return None


def launch(timeout_s=420, visible=True):
    baseline = active_object_pid()
    proc = subprocess.Popen([str(SW_EXE), "/r"])
    pid = proc.pid
    t0 = time.time()
    app = None
    while time.time() - t0 < timeout_s:
        time.sleep(2.0)
        app = bind_pid(pid)
        if app is not None:
            break
        if proc.poll() is not None:
            raise RuntimeError(f"SLDWORKS.exe exited early with code {proc.returncode}")
    if app is None:
        raise TimeoutError(f"SolidWorks_PID_{pid} never appeared in the ROT")
    # wait until the session is responsive
    for _ in range(120):
        try:
            app.RevisionNumber()
            break
        except pythoncom.com_error:
            time.sleep(1.0)
    guard_samples = []
    for _ in range(6):  # the class registration can lag the PID moniker; sample for ~10 s
        guard_samples.append(active_object_pid())
        if guard_samples[-1] == pid:
            break
        time.sleep(2.0)
    guard = guard_samples[-1]
    hijacked = baseline is not None and pid in guard_samples
    STATE.write_text(json.dumps({"pid": pid, "launched": time.strftime("%Y-%m-%d %H:%M:%S"),
                                 "active_object_pid_before": baseline, "active_object_pid_after": guard, "guard_samples": guard_samples,
                                 "hijacked": hijacked}, indent=2))
    if hijacked:
        try:
            app.ExitApp()
        finally:
            time.sleep(3)
            if pid_alive(pid):
                os.system(f"taskkill /PID {pid} /F >NUL 2>&1")
        raise RuntimeError("New session captured the shared GetActiveObject registration; closed it to protect the other session")
    try:
        app.Visible = visible
    except pythoncom.com_error:
        pass
    return app, pid


def get_app(launch_if_needed=True):
    """Return (app, pid) for the dedicated JX1 SolidWorks session."""
    if STATE.exists():
        st = json.loads(STATE.read_text())
        pid = st.get("pid")
        if pid and pid_alive(pid):
            app = bind_pid(pid)
            if app is not None:
                return app, pid
    if not launch_if_needed:
        raise RuntimeError("No JX1 SolidWorks session running")
    return launch()


if __name__ == "__main__":
    app, pid = get_app()
    print({"pid": pid, "process_id_reported": app.GetProcessID(), "revision": app.RevisionNumber(),
           "docs": app.GetDocumentCount(), "active_object_pid": active_object_pid()})
