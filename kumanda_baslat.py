import os
import subprocess

ana = r"C:\Users\hasan\Desktop\Kumanda"
node_klasor = os.path.join(ana, "node")
betik_dizin = os.path.dirname(os.path.abspath(__file__))

# 1) Eski 3000 sürecini öldür
subprocess.run(
    'for /f "tokens=5" %a in (\'netstat -ano ^| findstr :3000 ^| findstr LISTENING\') do taskkill /F /PID %a',
    shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)

# 2) Pencere küçültme + ortalama (PowerShell)
ps1_yolu = os.path.join(betik_dizin, "pencere_ayarla.ps1")
with open(ps1_yolu, "w", encoding="utf-8") as f:
    f.write(r'''Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class CW {
    [DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow();
    [DllImport("kernel32.dll")] public static extern IntPtr GetStdHandle(int n);
    [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int x, int y, int w, int hh, bool r);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    public struct RECT { public int Left, Top, Right, Bottom; }

    [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
    public struct CONSOLE_FONT_INFO_EX {
        public uint cbSize; public uint nFont;
        public short dwFontSizeX; public short dwFontSizeY;
        public int FontFamily; public int FontWeight;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string FaceName;
    }
    [DllImport("kernel32.dll")] public static extern bool SetCurrentConsoleFontEx(IntPtr h, bool m, ref CONSOLE_FONT_INFO_EX f);
    [DllImport("kernel32.dll")] public static extern bool GetCurrentConsoleFontEx(IntPtr h, bool m, ref CONSOLE_FONT_INFO_EX f);
}
"@
$hwnd = [CW]::GetConsoleWindow()
$hOut = [CW]::GetStdHandle(-11)

# --- Font'u küçült (Ctrl+tekerlek zoom-out) ---
$f = New-Object CW+CONSOLE_FONT_INFO_EX
$f.cbSize = [System.Runtime.InteropServices.Marshal]::SizeOf($f)
[CW]::GetCurrentConsoleFontEx($hOut, $false, [ref]$f) | Out-Null
$f.dwFontSizeY = [Math]::Max(10, $f.dwFontSizeY - 2)   # 2 piksel küçült
[CW]::SetCurrentConsoleFontEx($hOut, $false, [ref]$f) | Out-Null

Start-Sleep -Milliseconds 200

# --- Ortala ---
$r = New-Object CW+RECT
[CW]::GetWindowRect($hwnd, [ref]$r) | Out-Null
$w = $r.Right - $r.Left; $h = $r.Bottom - $r.Top
$s = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$x = [int](($s.Width - $w) / 2); $y = [int](($s.Height - $h) / 2)
[CW]::MoveWindow($hwnd, $x, $y, $w, $h, $true) | Out-Null
''')

# 3) Doğru klasörü bul
if os.path.isfile(os.path.join(node_klasor, "server.js")):
    hedef = ['cd /d "%USERPROFILE%\\Desktop"', 'cd Kumanda', 'cd node']
elif os.path.isfile(os.path.join(ana, "server.js")):
    hedef = ['cd /d "%USERPROFILE%\\Desktop"', 'cd Kumanda']
else:
    hedef = None

if hedef is None:
    satirlar = ['echo server.js bulunamadi!', 'pause']
else:
    satirlar = (
        ['title Kumanda Sunucusu']
        + ['@mode con: cols=68 lines=28 >nul']                                                # pencere boyutu
        + ['@powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0pencere_ayarla.ps1"']  # küçült + ortala
        + ['cls']
        + hedef
        + ['node server.js', 'pause']
    )

bat_yolu = os.path.join(betik_dizin, "kumanda_calistir.bat")
with open(bat_yolu, "w", encoding="utf-8") as f:
    f.write("\n".join(satirlar) + "\n")

os.startfile(bat_yolu)