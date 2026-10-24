#!/bin/bash
set -euo pipefail
cd /workspace/divalead
root=/workspace/divalead-setup
mkdir -p "$root" /workspace/.venvs
python3 -m venv /workspace/.venvs/divalead
PIP_CACHE_DIR="$root/pip-cache" /workspace/.venvs/divalead/bin/python -m pip install numpy==2.5.3 scipy==1.18.1 soundfile==0.14.0 cffi==2.1.1 pycparser==3.11 typing_extensions==4.16.0 matplotlib==3.11.2
/workspace/.venvs/divalead/bin/python -m pip check
if [ ! -x "$root/sysroot/usr/lib/wine/wineserver64" ]; then
  mkdir -p "$root/apt/lists/partial" "$root/apt/cache/archives/partial" "$root/sysroot"
  cat > "$root/apt/sources.list" <<'EOF'
deb https://deb.debian.org/debian trixie main
deb https://deb.debian.org/debian trixie-updates main
deb https://security.debian.org/debian-security trixie-security main
EOF
  apt_opts=(-o Debug::NoLocking=true -o Dir::Etc::sourcelist="$root/apt/sources.list" -o Dir::Etc::sourceparts=- -o Dir::State::lists="$root/apt/lists" -o Dir::Cache="$root/apt/cache" -o APT::Sandbox::User=agent)
  apt-get "${apt_opts[@]}" update
  apt-get "${apt_opts[@]}" --download-only --no-install-recommends -y install wine64 gcc-mingw-w64-x86-64-posix
  for package in "$root"/apt/cache/archives/*.deb; do dpkg-deb -x "$package" "$root/sysroot"; done
fi
ln -sfn wineserver64 "$root/sysroot/usr/lib/wine/wineserver"
ln -sfn . "$root/sysroot/usr/share/wine/wine"
cp "$root/sysroot/usr/x86_64-w64-mingw32/lib/zlib1.dll" "$root/sysroot/usr/lib/x86_64-linux-gnu/wine/x86_64-windows/"
mkdir -p "$root/bin" "$root/cache"
compiler="$root/sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix"
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/diva_vst2_host.exe" diva-lead/v8/analysis/diva_vst2_host.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host.exe" diva-lead/v8/analysis/fx_render_host.c -lm
mkdir -p "$root/wine2/drive_c/windows/system32"
cp "$root/sysroot/usr/x86_64-w64-mingw32/lib/zlib1.dll" "$root/wine2/drive_c/windows/system32/"
cd diva-lead/v8
sha256sum -c SHA256SUMS.txt
cd analysis
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python compare.py > "$root/measurements.current.json"

# Rebuild the v9 intermediate effect outside the checkout.
cd /workspace/divalead
"$compiler" -O2 -shared -static -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v9_WIP_x64.dll" diva-lead/v9-wip/analysis/lead_finish.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v9_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v9-wip\Diva_v9_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v9.wav' > "$root/rebuilt-v9.log" 2>&1
/workspace/.venvs/divalead/bin/python - <<'VERIFY'
import soundfile as sf
import numpy as np
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v9.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v9-wip/Diva_v9_FINAL_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
VERIFY
cd diva-lead/v9-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v9.current.json"

# Rebuild and check the later v10 WIP using its saved real Diva input.
cd /workspace/divalead
"$compiler" -O2 -shared -static -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v10_WIP_x64.dll" diva-lead/v10-wip/analysis/lead_finish.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v10_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v10-wip\Diva_v10_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v10.wav' > "$root/rebuilt-v10.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
import soundfile as sf
import numpy as np
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v10.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v10-wip/Diva_v10_FINAL_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
VERIFY
cd diva-lead/v10-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v10.current.json"

# Rebuild v11 WIP and verify the saved real-Diva fixture outside the checkout.
cd /workspace/divalead
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/diva_vst2_host_6s.exe" diva-lead/v11-wip/analysis/diva_vst2_host_6s.c -lm
"$compiler" -O2 -shared -static -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v11_WIP_x64.dll" diva-lead/v11-wip/analysis/lead_finish.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v11_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v11-wip\Diva_v11_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v11.wav' > "$root/rebuilt-v11.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
import soundfile as sf
import numpy as np
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v11.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v11-wip/Diva_v11_FINAL_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
VERIFY
cd diva-lead/v11-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v11.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/fir_design.py

# Rebuild the v12 stereo matrix WIP and verify its actual-Diva fixture.
cd /workspace/divalead
"$compiler" -O2 -shared -static -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v12_WIP_x64.dll" diva-lead/v12-wip/analysis/lead_finish.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v12_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v12-wip\Diva_v12_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v12.wav' > "$root/rebuilt-v12.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
import soundfile as sf
import numpy as np
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v12.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v12-wip/Diva_v12_FINAL_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
VERIFY
cd diva-lead/v12-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v12.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/fir_design.py

# Rebuild the v13 dynamic eight-path WIP and verify its actual-Diva fixture.
cd /workspace/divalead
"$compiler" -O2 -shared -static -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v13_WIP_x64.dll" diva-lead/v13-wip/analysis/lead_finish.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v13_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v13-wip\Diva_v13_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v13.wav' > "$root/rebuilt-v13.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
import soundfile as sf
import numpy as np
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v13.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v13-wip/Diva_v13_FINAL_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
VERIFY
cd diva-lead/v13-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v13.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/fir_design.py

# Rebuild the v14 dynamic eight-path WIP and verify its actual-Diva fixture.
cd /workspace/divalead
"$compiler" -O2 -shared -static -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v14_WIP_x64.dll" diva-lead/v14-wip/analysis/lead_finish.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v14_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v14-wip\Diva_v14_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v14.wav' > "$root/rebuilt-v14.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
import soundfile as sf
import numpy as np
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v14.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v14-wip/Diva_v14_FINAL_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
VERIFY
cd diva-lead/v14-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v14.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/fir_design.py

# Rebuild the v15 dynamic eight-path WIP and verify its actual-Diva fixture.
cd /workspace/divalead
"$compiler" -O2 -shared -static -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v15_WIP_x64.dll" diva-lead/v15-wip/analysis/lead_finish.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v15_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v15-wip\Diva_v15_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v15.wav' > "$root/rebuilt-v15.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
import soundfile as sf
import numpy as np
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v15.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v15-wip/Diva_v15_FINAL_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
VERIFY
cd diva-lead/v15-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v15.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/fir_design.py

# Rebuild v16 and verify its genuine-Diva fixture and input-driven EQ constants.
cd /workspace/divalead
"$compiler" -O2 -shared -static -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v16_WIP_x64.dll" diva-lead/v16-wip/analysis/lead_finish.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v16_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v16-wip\Diva_v16_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v16.wav' > "$root/rebuilt-v16.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
import soundfile as sf
import numpy as np
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v16.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v16-wip/Diva_v16_FINAL_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
VERIFY
cd diva-lead/v16-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v16.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/fir_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/dynamic_design.py


# Rebuild v17 and verify its genuine-Diva fixture and input-driven EQ constants.
cd /workspace/divalead
"$compiler" -O2 -shared -static -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v17_WIP_x64.dll" diva-lead/v17-wip/analysis/lead_finish.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v17_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v17-wip\Diva_v17_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v17.wav' > "$root/rebuilt-v17.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
import soundfile as sf
import numpy as np
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v17.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v17-wip/Diva_v17_FINAL_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
VERIFY
cd diva-lead/v17-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v17.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/fir_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/dynamic_design.py

# Rebuild v18 and verify its genuine-Diva fixture and input-driven EQ constants.
cd /workspace/divalead
"$compiler" -O2 -shared -static -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v18_WIP_x64.dll" diva-lead/v18-wip/analysis/lead_finish.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v18_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v18-wip\Diva_v18_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v18.wav' > "$root/rebuilt-v18.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
import soundfile as sf
import numpy as np
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v18.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v18-wip/Diva_v18_FINAL_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
VERIFY
cd diva-lead/v18-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v18.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/fir_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/dynamic_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/exciter_design.py

cd /workspace/divalead
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/diva_performance_host.exe" diva-lead/v18-wip/analysis/diva_vst2_host.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/diva_performance_host_6s.exe" diva-lead/v18-wip/analysis/diva_vst2_host_6s.c -lm

# Rebuild v19 and verify its genuine-Diva fixture and input-driven EQ constants.
cd /workspace/divalead
"$compiler" -O2 -shared -static -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v19_WIP_x64.dll" diva-lead/v19-wip/analysis/lead_finish.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v19_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v19-wip\Diva_v19_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v19.wav' > "$root/rebuilt-v19.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
import soundfile as sf
import numpy as np
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v19.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v19-wip/Diva_v19_FINAL_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
VERIFY
cd diva-lead/v19-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v19.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/fir_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/dynamic_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/exciter_design.py

# Rebuild v20 and verify its genuine-Diva fixture and input-driven EQ constants.
cd /workspace/divalead
"$compiler" -O2 -shared -static -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v20_WIP_x64.dll" diva-lead/v20-wip/analysis/lead_finish.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v20_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v20-wip\Diva_v20_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v20.wav' > "$root/rebuilt-v20.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
import soundfile as sf
import numpy as np
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v20.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v20-wip/Diva_v20_FINAL_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
VERIFY
cd diva-lead/v20-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v20.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/fir_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/dynamic_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/exciter_design.py

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/chorus_design.py


# Rebuild v21 WIP and verify its saved actual-Diva fixture and fixed recipes.
cd /workspace/divalead
"$compiler" -O2 -shared -static -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v21_WIP_x64.dll" diva-lead/v21-wip/analysis/lead_finish.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v21_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v21-wip\Diva_v21_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v21.wav' > "$root/rebuilt-v21.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
import soundfile as sf
import numpy as np
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v21.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v21-wip/Diva_v21_FINAL_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
VERIFY
cd diva-lead/v21-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v21.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/fir_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/dynamic_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/exciter_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/chorus_design.py

# Rebuild v22 WIP and verify its saved actual-Diva fixture and fixed recipes.
cd /workspace/divalead
"$compiler" -O2 -shared -static -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v22_WIP_x64.dll" diva-lead/v22-wip/analysis/lead_finish.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v22_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v22-wip\Diva_v22_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v22.wav' > "$root/rebuilt-v22.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
import soundfile as sf
import numpy as np
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v22.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v22-wip/Diva_v22_FINAL_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
VERIFY
cd diva-lead/v22-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v22.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/fir_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/dynamic_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/exciter_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/chorus_design.py

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/harmonic_color_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/harmonic_compare.py > "$root/harmonic-measurements.v22.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/harmonic_color_test.py > "$root/harmonic-color-test.v22.current.json"

# Rebuild v23 WIP and verify its saved actual-Diva fixture and fixed recipes.
cd /workspace/divalead
"$compiler" -O2 -shared -static -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v23_WIP_x64.dll" diva-lead/v23-wip/analysis/lead_finish.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v23_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v23-wip\Diva_v23_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v23.wav' > "$root/rebuilt-v23.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
import soundfile as sf
import numpy as np
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v23.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v23-wip/Diva_v23_FINAL_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
VERIFY
cd diva-lead/v23-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v23.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/fir_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/dynamic_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/exciter_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/chorus_design.py

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/harmonic_color_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/harmonic_compare.py > "$root/harmonic-measurements.v23.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/harmonic_color_test.py > "$root/harmonic-color-test.v23.current.json"


# Rebuild v24 WIP and verify its saved actual-Diva fixture and fixed recipes.
cd /workspace/divalead
"$compiler" -O2 -shared -static -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v24_WIP_x64.dll" diva-lead/v24-wip/analysis/lead_finish.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v24_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v24-wip\Diva_v24_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v24.wav' > "$root/rebuilt-v24.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
import soundfile as sf
import numpy as np
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v24.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v24-wip/Diva_v24_FINAL_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
VERIFY
cd diva-lead/v24-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v24.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/fir_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/dynamic_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/exciter_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/chorus_design.py

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/harmonic_color_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/harmonic_compare.py > "$root/harmonic-measurements.v24.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/harmonic_color_test.py > "$root/harmonic-color-test.v24.current.json"

# Rebuild v25 WIP and verify its saved actual-Diva fixture and fixed recipes.
cd /workspace/divalead
"$compiler" -O2 -shared -static -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v25_WIP_x64.dll" diva-lead/v25-wip/analysis/lead_finish.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v25_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v25-wip\Diva_v25_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v25.wav' > "$root/rebuilt-v25.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
import soundfile as sf
import numpy as np
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v25.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v25-wip/Diva_v25_FINAL_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
VERIFY
cd diva-lead/v25-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v25.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/fir_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/dynamic_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/exciter_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/chorus_design.py

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/harmonic_color_design.py
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/harmonic_compare.py > "$root/harmonic-measurements.v25.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/harmonic_color_test.py > "$root/harmonic-color-test.v25.current.json"


PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/return_damp_design.py

# Rebuild v26 WIP and verify the new causal spectral stage and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v26_WIP_x64.dll" diva-lead/v26-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v26.exe" diva-lead/v26-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v26.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v26_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v26-wip\Diva_v26_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v26.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v26.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v26.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v26-wip/Diva_v26_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v26.log').read_text()
VERIFY
cd diva-lead/v26-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v26.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v26.current.json"

# Rebuild v27 WIP and verify the new causal spectral stage and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v27_WIP_x64.dll" diva-lead/v27-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v27.exe" diva-lead/v27-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v27.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v27_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v27-wip\Diva_v27_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v27.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v27.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v27.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v27-wip/Diva_v27_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v27.log').read_text()
VERIFY
cd diva-lead/v27-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v27.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v27.current.json"

# Rebuild v28 WIP and verify the new causal spectral stage and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v28_WIP_x64.dll" diva-lead/v28-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v28.exe" diva-lead/v28-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v28.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v28_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v28-wip\Diva_v28_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v28.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v28.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v28.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v28-wip/Diva_v28_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v28.log').read_text()
VERIFY
cd diva-lead/v28-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v28.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v28.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v28.current.json"

# Rebuild v29 WIP and verify the new causal spectral stage and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v29_WIP_x64.dll" diva-lead/v29-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v29.exe" diva-lead/v29-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v29.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v29_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v29-wip\Diva_v29_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v29.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v29.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v29.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v29-wip/Diva_v29_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v29.log').read_text()
VERIFY
cd diva-lead/v29-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v29.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v29.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v29.current.json"

# Rebuild v30 WIP and verify the new causal spectral stage and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v30_WIP_x64.dll" diva-lead/v30-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v30.exe" diva-lead/v30-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v30.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v30_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v30-wip\Diva_v30_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v30.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v30.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v30.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v30-wip/Diva_v30_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v30.log').read_text()
VERIFY
cd diva-lead/v30-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v30.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v30.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v30.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v30.current.json"

# Rebuild v31 WIP and verify the new causal spectral stage and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v31_WIP_x64.dll" diva-lead/v31-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v31.exe" diva-lead/v31-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v31.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v31_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v31-wip\Diva_v31_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v31.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v31.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v31.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v31-wip/Diva_v31_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v31.log').read_text()
VERIFY
cd diva-lead/v31-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v31.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v31.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v31.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v31.current.json"

# Rebuild v32 WIP and verify the new causal spectral stage and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v32_WIP_x64.dll" diva-lead/v32-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v32.exe" diva-lead/v32-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v32.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v32_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v32-wip\Diva_v32_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v32.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v32.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v32.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v32-wip/Diva_v32_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v32.log').read_text()
VERIFY
cd diva-lead/v32-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v32.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v32.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v32.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v32.current.json"

# Rebuild v33 WIP and verify the new causal spectral stage and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v33_WIP_x64.dll" diva-lead/v33-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v33.exe" diva-lead/v33-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v33.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v33_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v33-wip\Diva_v33_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v33.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v33.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v33.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v33-wip/Diva_v33_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v33.log').read_text()
VERIFY
cd diva-lead/v33-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v33.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v33.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v33.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v33.current.json"

# Rebuild v34 WIP and verify the new causal spectral stage and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v34_WIP_x64.dll" diva-lead/v34-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v34.exe" diva-lead/v34-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v34.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v34_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v34-wip\Diva_v34_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v34.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v34.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v34.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v34-wip/Diva_v34_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v34.log').read_text()
VERIFY
cd diva-lead/v34-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v34.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v34.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v34.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v34.current.json"

# Rebuild v35 WIP and verify the new causal spectral stage and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v35_WIP_x64.dll" diva-lead/v35-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v35.exe" diva-lead/v35-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v35.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v35_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v35-wip\Diva_v35_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v35.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v35.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v35.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v35-wip/Diva_v35_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v35.log').read_text()
VERIFY
cd diva-lead/v35-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v35.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v35.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v35.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v35.current.json"

# Rebuild v36 WIP and verify the new causal spectral stage and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v36_WIP_x64.dll" diva-lead/v36-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v36.exe" diva-lead/v36-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v36.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v36_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v36-wip\Diva_v36_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v36.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v36.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v36.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v36-wip/Diva_v36_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v36.log').read_text()
VERIFY
cd diva-lead/v36-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v36.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v36.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v36.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v36.current.json"


# Rebuild v37 WIP and verify the quadratic live-key core stage and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v37_WIP_x64.dll" diva-lead/v37-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v37.exe" diva-lead/v37-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v37.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v37_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v37-wip\Diva_v37_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v37.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v37.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v37.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v37-wip/Diva_v37_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v37.log').read_text()
VERIFY
cd diva-lead/v37-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v37.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v37.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v37.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v37.current.json"


# Rebuild v38 WIP and verify the expanded54 harmonic-gain stage and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v38_WIP_x64.dll" diva-lead/v38-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v38.exe" diva-lead/v38-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v38.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v38_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v38-wip\Diva_v38_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v38.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v38.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v38.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v38-wip/Diva_v38_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v38.log').read_text()
VERIFY
cd diva-lead/v38-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v38.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v38.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v38.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v38.current.json"


# Rebuild v39 WIP and verify the upper frequency and pitch-response coefficients and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v39_WIP_x64.dll" diva-lead/v39-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v39.exe" diva-lead/v39-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v39.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v39_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v39-wip\Diva_v39_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v39.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v39.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v39.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v39-wip/Diva_v39_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v39.log').read_text()
VERIFY
cd diva-lead/v39-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v39.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v39.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v39.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v39.current.json"


# Rebuild v40 WIP and verify the upper harmonic coefficients on individual notes and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v40_WIP_x64.dll" diva-lead/v40-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v40.exe" diva-lead/v40-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v40.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v40_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v40-wip\Diva_v40_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v40.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v40.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v40.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v40-wip/Diva_v40_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v40.log').read_text()
VERIFY
cd diva-lead/v40-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v40.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v40.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v40.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v40.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_powers.py > "$root/stationary-v40.current.json"


# Rebuild v41 WIP and verify the extended78 harmonic-gain and upper coefficients and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v41_WIP_x64.dll" diva-lead/v41-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v41.exe" diva-lead/v41-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v41.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v41_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v41-wip\Diva_v41_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v41.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v41.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v41.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v41-wip/Diva_v41_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v41.log').read_text()
VERIFY
cd diva-lead/v41-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v41.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v41.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v41.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v41.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_powers.py > "$root/stationary-v41.current.json"


# Rebuild v42 WIP and verify the extended93 harmonic-gain and balanced lower coefficients and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v42_WIP_x64.dll" diva-lead/v42-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v42.exe" diva-lead/v42-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v42.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v42_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v42-wip\Diva_v42_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v42.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v42.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v42.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v42-wip/Diva_v42_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v42.log').read_text()
VERIFY
cd diva-lead/v42-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v42.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v42.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v42.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v42.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_powers.py > "$root/stationary-v42.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_low_powers.py > "$root/stationary-low-v42.current.json"


# Rebuild v43 WIP and verify the adaptive69target plusstatic352 coefficients and updatedSide bank and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v43_WIP_x64.dll" diva-lead/v43-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v43.exe" diva-lead/v43-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v43.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v43_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v43-wip\Diva_v43_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v43.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v43.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v43.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v43-wip/Diva_v43_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v43.log').read_text()
VERIFY
cd diva-lead/v43-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v43.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v43.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v43.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v43.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_powers.py > "$root/stationary-v43.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_low_powers.py > "$root/stationary-low-v43.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/test_adaptive_transitions.py > "$root/adaptive-transitions-v43.current.log"

# Rebuild v44 WIP and verify the four grouped adaptive strengths, shared response time and 421 coefficients and updatedSide bank and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v44_WIP_x64.dll" diva-lead/v44-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v44.exe" diva-lead/v44-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v44.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v44_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v44-wip\Diva_v44_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v44.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v44.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v44.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v44-wip/Diva_v44_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v44.log').read_text()
VERIFY
cd diva-lead/v44-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v44.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v44.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v44.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v44.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_powers.py > "$root/stationary-v44.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_low_powers.py > "$root/stationary-low-v44.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/test_adaptive_transitions.py > "$root/adaptive-transitions-v44.current.log"

cat > "$root/startup-check-v44.py" <<'DIVA_STARTUP_PY'
"""Actual Diva and Windows-effect startup readiness, with outputs outside the checkout."""
from pathlib import Path
import json,subprocess,sys
import numpy as np,soundfile as sf
sys.path.insert(0,'/workspace/divalead-work')
from v18performancelib import ROOT,REPO,WINE,ENV,winpath,render_performance

V=REPO/'diva-lead/v44-wip'
S=Path('/workspace/divalead-setup')
c=json.loads((V/'analysis/selected_candidate.json').read_text())
dump=S/'startup-v44-Diva-parameters.tsv'
dry=render_performance(c['settings'],'startup-v44-actual-Diva',preset=V/'Diva_Lead_v44_WIP.h2p',dump=dump)
np.testing.assert_array_equal(dry,sf.read(V/'Diva_v44_VIDEO_DIVA_ONLY.wav',dtype='float32')[0])
assert dump.read_bytes()==(V/'Diva_v44_DIVA_parameters.tsv').read_bytes()
out=S/'startup-v44-full-Windows.wav'
with (S/'startup-v44-full-Windows.log').open('w') as log:
    subprocess.run([WINE,str(S/'bin/fx_render_host_v44.exe'),winpath(S/'bin/Diva_Lead_Finish_v44_WIP_x64.dll'),winpath(ROOT/'startup-v44-actual-Diva.wav'),winpath(out),'512','1',str(c['effect_parameters'][40]),'0'],env=ENV,stdout=log,stderr=log,timeout=150,check=True)
actual,rate=sf.read(out,dtype='float32')
assert rate==48000 and actual.shape==(288000,2)
np.testing.assert_array_equal(actual,sf.read(V/'Diva_v44_VIDEO_WITH_PDC.wav',dtype='float32')[0])
assert 'latency=12416' in (S/'startup-v44-full-Windows.log').read_text()
assert np.isfinite(actual).all() and np.max(abs(actual))<1
reference=Path('/workspace/attachments/c7279e3d-5fcb-48c4-b77b-f93b2c677f27/Diva_original_lead_reference.wav')
if reference.exists():
    np.testing.assert_array_equal(sf.read(reference)[0],sf.read(V/'Diva_original_lead_reference.wav')[0])
print('STARTUP44_ACTUAL_DIVA_281PARAMETERS_AND_WINDOWS_WAV_BITEXACT_PDC_PASS')
DIVA_STARTUP_PY
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python "$root/startup-check-v44.py"

# Rebuild v45 WIP and verify the four grouped adaptive strengths, shared response time and 467 coefficients, quartic targets and refined common phase and updatedSide bank and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v45_WIP_x64.dll" diva-lead/v45-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v45.exe" diva-lead/v45-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v45.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v45_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v45-wip\Diva_v45_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v45.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v45.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v45.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v45-wip/Diva_v45_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v45.log').read_text()
VERIFY
cd diva-lead/v45-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v45.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v45.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v45.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v45.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_powers.py > "$root/stationary-v45.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_low_powers.py > "$root/stationary-low-v45.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/test_adaptive_transitions.py > "$root/adaptive-transitions-v45.current.log"

cat > "$root/startup-check-v45.py" <<'DIVA_STARTUP_PY'
"""Actual Diva and Windows-effect startup readiness, with outputs outside the checkout."""
from pathlib import Path
import json,subprocess,sys
import numpy as np,soundfile as sf
sys.path.insert(0,'/workspace/divalead-work')
from v18performancelib import ROOT,REPO,WINE,ENV,winpath,render_performance

V=REPO/'diva-lead/v45-wip'
S=Path('/workspace/divalead-setup')
c=json.loads((V/'analysis/selected_candidate.json').read_text())
dump=S/'startup-v45-Diva-parameters.tsv'
dry=render_performance(c['settings'],'startup-v45-actual-Diva',preset=V/'Diva_Lead_v45_WIP.h2p',dump=dump)
np.testing.assert_array_equal(dry,sf.read(V/'Diva_v45_VIDEO_DIVA_ONLY.wav',dtype='float32')[0])
assert dump.read_bytes()==(V/'Diva_v45_DIVA_parameters.tsv').read_bytes()
out=S/'startup-v45-full-Windows.wav'
with (S/'startup-v45-full-Windows.log').open('w') as log:
    subprocess.run([WINE,str(S/'bin/fx_render_host_v45.exe'),winpath(S/'bin/Diva_Lead_Finish_v45_WIP_x64.dll'),winpath(ROOT/'startup-v45-actual-Diva.wav'),winpath(out),'512','1',str(c['effect_parameters'][40]),'0'],env=ENV,stdout=log,stderr=log,timeout=150,check=True)
actual,rate=sf.read(out,dtype='float32')
assert rate==48000 and actual.shape==(288000,2)
np.testing.assert_array_equal(actual,sf.read(V/'Diva_v45_VIDEO_WITH_PDC.wav',dtype='float32')[0])
assert 'latency=12416' in (S/'startup-v45-full-Windows.log').read_text()
assert np.isfinite(actual).all() and np.max(abs(actual))<1
reference=Path('/workspace/attachments/c7279e3d-5fcb-48c4-b77b-f93b2c677f27/Diva_original_lead_reference.wav')
if reference.exists():
    np.testing.assert_array_equal(sf.read(reference)[0],sf.read(V/'Diva_original_lead_reference.wav')[0])
print('STARTUP44_ACTUAL_DIVA_281PARAMETERS_AND_WINDOWS_WAV_BITEXACT_PDC_PASS')
DIVA_STARTUP_PY
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python "$root/startup-check-v45.py"

# Rebuild v46 WIP and verify the four grouped adaptive strengths, shared response time and 587 coefficients, harmonic stereo targets and47 gain states and updatedSide bank and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v46_WIP_x64.dll" diva-lead/v46-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v46.exe" diva-lead/v46-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v46.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v46_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v46-wip\Diva_v46_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v46.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v46.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v46.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v46-wip/Diva_v46_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v46.log').read_text()
VERIFY
cd diva-lead/v46-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v46.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v46.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v46.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v46.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_powers.py > "$root/stationary-v46.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_low_powers.py > "$root/stationary-low-v46.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/test_adaptive_transitions.py > "$root/adaptive-transitions-v46.current.log"

cat > "$root/startup-check-v46.py" <<'DIVA_STARTUP_PY'
"""Actual Diva and Windows-effect startup readiness, with outputs outside the checkout."""
from pathlib import Path
import json,subprocess,sys
import numpy as np,soundfile as sf
sys.path.insert(0,'/workspace/divalead-work')
from v18performancelib import ROOT,REPO,WINE,ENV,winpath,render_performance

V=REPO/'diva-lead/v46-wip'
S=Path('/workspace/divalead-setup')
c=json.loads((V/'analysis/selected_candidate.json').read_text())
dump=S/'startup-v46-Diva-parameters.tsv'
dry=render_performance(c['settings'],'startup-v46-actual-Diva',preset=V/'Diva_Lead_v46_WIP.h2p',dump=dump)
np.testing.assert_array_equal(dry,sf.read(V/'Diva_v46_VIDEO_DIVA_ONLY.wav',dtype='float32')[0])
assert dump.read_bytes()==(V/'Diva_v46_DIVA_parameters.tsv').read_bytes()
out=S/'startup-v46-full-Windows.wav'
with (S/'startup-v46-full-Windows.log').open('w') as log:
    subprocess.run([WINE,str(S/'bin/fx_render_host_v46.exe'),winpath(S/'bin/Diva_Lead_Finish_v46_WIP_x64.dll'),winpath(ROOT/'startup-v46-actual-Diva.wav'),winpath(out),'512','1',str(c['effect_parameters'][40]),'0'],env=ENV,stdout=log,stderr=log,timeout=150,check=True)
actual,rate=sf.read(out,dtype='float32')
assert rate==48000 and actual.shape==(288000,2)
np.testing.assert_array_equal(actual,sf.read(V/'Diva_v46_VIDEO_WITH_PDC.wav',dtype='float32')[0])
assert 'latency=12416' in (S/'startup-v46-full-Windows.log').read_text()
assert np.isfinite(actual).all() and np.max(abs(actual))<1
reference=Path('/workspace/attachments/c7279e3d-5fcb-48c4-b77b-f93b2c677f27/Diva_original_lead_reference.wav')
if reference.exists():
    np.testing.assert_array_equal(sf.read(reference)[0],sf.read(V/'Diva_original_lead_reference.wav')[0])
print('STARTUP44_ACTUAL_DIVA_281PARAMETERS_AND_WINDOWS_WAV_BITEXACT_PDC_PASS')
DIVA_STARTUP_PY
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python "$root/startup-check-v46.py"

# Rebuild v47 WIP and verify the 23 independent harmonic strengths, shared response time and 587 coefficients, harmonic stereo targets and47 gain states and updatedSide bank and Tune2 source and12 phase values and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v47_WIP_x64.dll" diva-lead/v47-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v47.exe" diva-lead/v47-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v47.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v47_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v47-wip\Diva_v47_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v47.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v47.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v47.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v47-wip/Diva_v47_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v47.log').read_text()
VERIFY
cd diva-lead/v47-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v47.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v47.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v47.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v47.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_powers.py > "$root/stationary-v47.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_low_powers.py > "$root/stationary-low-v47.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/test_adaptive_transitions.py > "$root/adaptive-transitions-v47.current.log"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/test_group_activation.py > "$root/group-activation-v47.current.log"

cat > "$root/startup-check-v47.py" <<'DIVA_STARTUP_PY'
"""Actual Diva and Windows-effect startup readiness, with outputs outside the checkout."""
from pathlib import Path
import json,subprocess,sys
import numpy as np,soundfile as sf
sys.path.insert(0,'/workspace/divalead-work')
from v18performancelib import ROOT,REPO,WINE,ENV,winpath,render_performance

V=REPO/'diva-lead/v47-wip'
S=Path('/workspace/divalead-setup')
c=json.loads((V/'analysis/selected_candidate.json').read_text())
dump=S/'startup-v47-Diva-parameters.tsv'
dry=render_performance(c['settings'],'startup-v47-actual-Diva',preset=V/'Diva_Lead_v47_WIP.h2p',dump=dump)
np.testing.assert_array_equal(dry,sf.read(V/'Diva_v47_VIDEO_DIVA_ONLY.wav',dtype='float32')[0])
assert dump.read_bytes()==(V/'Diva_v47_DIVA_parameters.tsv').read_bytes()
out=S/'startup-v47-full-Windows.wav'
with (S/'startup-v47-full-Windows.log').open('w') as log:
    subprocess.run([WINE,str(S/'bin/fx_render_host_v47.exe'),winpath(S/'bin/Diva_Lead_Finish_v47_WIP_x64.dll'),winpath(ROOT/'startup-v47-actual-Diva.wav'),winpath(out),'512','1',str(c['effect_parameters'][40]),'0'],env=ENV,stdout=log,stderr=log,timeout=150,check=True)
actual,rate=sf.read(out,dtype='float32')
assert rate==48000 and actual.shape==(288000,2)
np.testing.assert_array_equal(actual,sf.read(V/'Diva_v47_VIDEO_WITH_PDC.wav',dtype='float32')[0])
assert 'latency=12416' in (S/'startup-v47-full-Windows.log').read_text()
assert np.isfinite(actual).all() and np.max(abs(actual))<1
reference=Path('/workspace/attachments/c7279e3d-5fcb-48c4-b77b-f93b2c677f27/Diva_original_lead_reference.wav')
if reference.exists():
    np.testing.assert_array_equal(sf.read(reference)[0],sf.read(V/'Diva_original_lead_reference.wav')[0])
print('STARTUP47_ACTUAL_DIVA_281PARAMETERS_AND_WINDOWS_WAV_BITEXACT_PDC_PASS')
DIVA_STARTUP_PY
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python "$root/startup-check-v47.py"

# Rebuild v48 WIP and verify the 23 independent harmonic strengths, shared response time and 608 coefficients, harmonic stereo targets and47 gain states and unchanged47source/pre-STFT plus21high-stereo coefficients and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v48_WIP_x64.dll" diva-lead/v48-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v48.exe" diva-lead/v48-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v48.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v48_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v48-wip\Diva_v48_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v48.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v48.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v48.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v48-wip/Diva_v48_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v48.log').read_text()
VERIFY
cd diva-lead/v48-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v48.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v48.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v48.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v48.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_powers.py > "$root/stationary-v48.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_low_powers.py > "$root/stationary-low-v48.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/test_adaptive_transitions.py > "$root/adaptive-transitions-v48.current.log"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/test_group_activation.py > "$root/group-activation-v48.current.log"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/stereo_profile.py > "$root/stereo-profile-v48.current.json"

cat > "$root/startup-check-v48.py" <<'DIVA_STARTUP_PY'
"""Actual Diva and Windows-effect startup readiness, with outputs outside the checkout."""
from pathlib import Path
import json,subprocess,sys
import numpy as np,soundfile as sf
sys.path.insert(0,'/workspace/divalead-work')
from v18performancelib import ROOT,REPO,WINE,ENV,winpath,render_performance

V=REPO/'diva-lead/v48-wip'
S=Path('/workspace/divalead-setup')
c=json.loads((V/'analysis/selected_candidate.json').read_text())
dump=S/'startup-v48-Diva-parameters.tsv'
dry=render_performance(c['settings'],'startup-v48-actual-Diva',preset=V/'Diva_Lead_v48_WIP.h2p',dump=dump)
np.testing.assert_array_equal(dry,sf.read(V/'Diva_v48_VIDEO_DIVA_ONLY.wav',dtype='float32')[0])
assert dump.read_bytes()==(V/'Diva_v48_DIVA_parameters.tsv').read_bytes()
out=S/'startup-v48-full-Windows.wav'
with (S/'startup-v48-full-Windows.log').open('w') as log:
    subprocess.run([WINE,str(S/'bin/fx_render_host_v48.exe'),winpath(S/'bin/Diva_Lead_Finish_v48_WIP_x64.dll'),winpath(ROOT/'startup-v48-actual-Diva.wav'),winpath(out),'512','1',str(c['effect_parameters'][40]),'0'],env=ENV,stdout=log,stderr=log,timeout=150,check=True)
actual,rate=sf.read(out,dtype='float32')
assert rate==48000 and actual.shape==(288000,2)
np.testing.assert_array_equal(actual,sf.read(V/'Diva_v48_VIDEO_WITH_PDC.wav',dtype='float32')[0])
assert 'latency=12416' in (S/'startup-v48-full-Windows.log').read_text()
assert np.isfinite(actual).all() and np.max(abs(actual))<1
reference=Path('/workspace/attachments/c7279e3d-5fcb-48c4-b77b-f93b2c677f27/Diva_original_lead_reference.wav')
if reference.exists():
    np.testing.assert_array_equal(sf.read(reference)[0],sf.read(V/'Diva_original_lead_reference.wav')[0])
print('STARTUP48_ACTUAL_DIVA_281PARAMETERS_AND_WINDOWS_WAV_BITEXACT_PDC_PASS')
DIVA_STARTUP_PY
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python "$root/startup-check-v48.py"

# Rebuild v49 WIP and verify the 23 independent harmonic strengths, shared response time and 632 coefficients, harmonic stereo targets and47 gain states and unchanged47source/pre-STFT plus21upper-stereo coefficients and24low/join values and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v49_WIP_x64.dll" diva-lead/v49-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v49.exe" diva-lead/v49-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v49.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v49_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v49-wip\Diva_v49_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v49.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v49.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v49.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v49-wip/Diva_v49_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v49.log').read_text()
VERIFY
cd diva-lead/v49-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v49.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v49.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v49.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v49.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_powers.py > "$root/stationary-v49.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_low_powers.py > "$root/stationary-low-v49.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/test_adaptive_transitions.py > "$root/adaptive-transitions-v49.current.log"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/test_group_activation.py > "$root/group-activation-v49.current.log"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/stereo_profile.py > "$root/stereo-profile-v49.current.json"

cat > "$root/startup-check-v49.py" <<'DIVA_STARTUP_PY'
"""Actual Diva and Windows-effect startup readiness, with outputs outside the checkout."""
from pathlib import Path
import json,subprocess,sys
import numpy as np,soundfile as sf
sys.path.insert(0,'/workspace/divalead-work')
from v18performancelib import ROOT,REPO,WINE,ENV,winpath,render_performance

V=REPO/'diva-lead/v49-wip'
S=Path('/workspace/divalead-setup')
c=json.loads((V/'analysis/selected_candidate.json').read_text())
dump=S/'startup-v49-Diva-parameters.tsv'
dry=render_performance(c['settings'],'startup-v49-actual-Diva',preset=V/'Diva_Lead_v49_WIP.h2p',dump=dump)
np.testing.assert_array_equal(dry,sf.read(V/'Diva_v49_VIDEO_DIVA_ONLY.wav',dtype='float32')[0])
assert dump.read_bytes()==(V/'Diva_v49_DIVA_parameters.tsv').read_bytes()
out=S/'startup-v49-full-Windows.wav'
with (S/'startup-v49-full-Windows.log').open('w') as log:
    subprocess.run([WINE,str(S/'bin/fx_render_host_v49.exe'),winpath(S/'bin/Diva_Lead_Finish_v49_WIP_x64.dll'),winpath(ROOT/'startup-v49-actual-Diva.wav'),winpath(out),'512','1',str(c['effect_parameters'][40]),'0'],env=ENV,stdout=log,stderr=log,timeout=150,check=True)
actual,rate=sf.read(out,dtype='float32')
assert rate==48000 and actual.shape==(288000,2)
np.testing.assert_array_equal(actual,sf.read(V/'Diva_v49_VIDEO_WITH_PDC.wav',dtype='float32')[0])
assert 'latency=12416' in (S/'startup-v49-full-Windows.log').read_text()
assert np.isfinite(actual).all() and np.max(abs(actual))<1
reference=Path('/workspace/attachments/c7279e3d-5fcb-48c4-b77b-f93b2c677f27/Diva_original_lead_reference.wav')
if reference.exists():
    np.testing.assert_array_equal(sf.read(reference)[0],sf.read(V/'Diva_original_lead_reference.wav')[0])
print('STARTUP49_ACTUAL_DIVA_281PARAMETERS_AND_WINDOWS_WAV_BITEXACT_PDC_PASS')
DIVA_STARTUP_PY
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python "$root/startup-check-v49.py"

# Rebuild v50 WIP and verify the 23 independent harmonic strengths, shared response time and 638 coefficients, harmonic stereo targets and47 gain states and unchanged49source/pre-STFT/stereo plus6phase-key curvatures and updatedexisting phase/strength values and reported PDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v50_WIP_x64.dll" diva-lead/v50-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v50.exe" diva-lead/v50-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v50.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v50_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v50-wip\Diva_v50_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v50.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v50.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v50.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v50-wip/Diva_v50_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v50.log').read_text()
VERIFY
cd diva-lead/v50-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v50.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v50.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v50.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v50.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_powers.py > "$root/stationary-v50.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_low_powers.py > "$root/stationary-low-v50.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/test_adaptive_transitions.py > "$root/adaptive-transitions-v50.current.log"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/test_group_activation.py > "$root/group-activation-v50.current.log"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/stereo_profile.py > "$root/stereo-profile-v50.current.json"

cat > "$root/startup-check-v50.py" <<'DIVA_STARTUP_PY'
"""Actual Diva and Windows-effect startup readiness, with outputs outside the checkout."""
from pathlib import Path
import json,subprocess,sys
import numpy as np,soundfile as sf
sys.path.insert(0,'/workspace/divalead-work')
from v18performancelib import ROOT,REPO,WINE,ENV,winpath,render_performance

V=REPO/'diva-lead/v50-wip'
S=Path('/workspace/divalead-setup')
c=json.loads((V/'analysis/selected_candidate.json').read_text())
dump=S/'startup-v50-Diva-parameters.tsv'
dry=render_performance(c['settings'],'startup-v50-actual-Diva',preset=V/'Diva_Lead_v50_WIP.h2p',dump=dump)
np.testing.assert_array_equal(dry,sf.read(V/'Diva_v50_VIDEO_DIVA_ONLY.wav',dtype='float32')[0])
assert dump.read_bytes()==(V/'Diva_v50_DIVA_parameters.tsv').read_bytes()
out=S/'startup-v50-full-Windows.wav'
with (S/'startup-v50-full-Windows.log').open('w') as log:
    subprocess.run([WINE,str(S/'bin/fx_render_host_v50.exe'),winpath(S/'bin/Diva_Lead_Finish_v50_WIP_x64.dll'),winpath(ROOT/'startup-v50-actual-Diva.wav'),winpath(out),'512','1',str(c['effect_parameters'][40]),'0'],env=ENV,stdout=log,stderr=log,timeout=150,check=True)
actual,rate=sf.read(out,dtype='float32')
assert rate==48000 and actual.shape==(288000,2)
np.testing.assert_array_equal(actual,sf.read(V/'Diva_v50_VIDEO_WITH_PDC.wav',dtype='float32')[0])
assert 'latency=12416' in (S/'startup-v50-full-Windows.log').read_text()
assert np.isfinite(actual).all() and np.max(abs(actual))<1
reference=Path('/workspace/attachments/c7279e3d-5fcb-48c4-b77b-f93b2c677f27/Diva_original_lead_reference.wav')
if reference.exists():
    np.testing.assert_array_equal(sf.read(reference)[0],sf.read(V/'Diva_original_lead_reference.wav')[0])
print('STARTUP50_ACTUAL_DIVA_281PARAMETERS_AND_WINDOWS_WAV_BITEXACT_PDC_PASS')
DIVA_STARTUP_PY
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python "$root/startup-check-v50.py"

#!/bin/bash
set -euo pipefail
root=/workspace/divalead-setup
compiler="$root/sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix"
# Rebuild55; verify source267/all281 unchanged54, refined638spectral values/47gainstates andPDC.
cd /workspace/divalead
"$compiler" -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o "$root/bin/Diva_Lead_Finish_v55_WIP_x64.dll" diva-lead/v55-wip/analysis/lead_finish.c -lm
"$compiler" -O2 -static -Wl,--no-insert-timestamp -o "$root/bin/fx_render_host_v55.exe" diva-lead/v55-wip/analysis/fx_render_host.c -lm
WINEDLLPATH="$root/sysroot/usr/lib/x86_64-linux-gnu/wine" WINEPREFIX="$root/wine2" WINEDEBUG=-all XDG_CACHE_HOME="$root/cache" "$root/sysroot/usr/lib/wine/wine64" "$root/bin/fx_render_host_v55.exe" 'Z:\workspace\divalead-setup\bin\Diva_Lead_Finish_v55_WIP_x64.dll' 'Z:\workspace\divalead\diva-lead\v55-wip\Diva_v55_VIDEO_DIVA_ONLY.wav' 'Z:\workspace\divalead-setup\rebuilt-v55.wav' 512 1 1.8525063970852007 0 > "$root/rebuilt-v55.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python - <<'VERIFY'
from pathlib import Path
import numpy as np
import soundfile as sf
actual,sr=sf.read('/workspace/divalead-setup/rebuilt-v55.wav',dtype='float32')
expected,_=sf.read('/workspace/divalead/diva-lead/v55-wip/Diva_v55_VIDEO_WITH_PDC.wav',dtype='float32')
assert sr==48000
np.testing.assert_array_equal(actual,expected)
assert 'latency=12416' in Path('/workspace/divalead-setup/rebuilt-v55.log').read_text()
VERIFY
cd diva-lead/v55-wip
sha256sum -c SHA256SUMS.txt
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/compare.py > "$root/measurements.v55.current.json"
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/verify_spectral.py --fixtures > "$root/spectral-v55.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_crest.py > "$root/crest-v55.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_energy_envelopes.py > "$root/energy-envelope-v55.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_powers.py > "$root/stationary-v55.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/measure_stationary_low_powers.py > "$root/stationary-low-v55.current.json"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/test_adaptive_transitions.py > "$root/adaptive-transitions-v55.current.log"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/test_group_activation.py > "$root/group-activation-v55.current.log"

PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python analysis/stereo_profile.py > "$root/stereo-profile-v55.current.json"

cat > "$root/startup-check-v55.py" <<'DIVA_STARTUP_PY'
"""Actual Diva and Windows-effect startup readiness, with outputs outside the checkout."""
from pathlib import Path
import json,subprocess,sys
import numpy as np,soundfile as sf
sys.path.insert(0,'/workspace/divalead-work')
from v18performancelib import ROOT,REPO,WINE,ENV,winpath,render_performance

V=REPO/'diva-lead/v55-wip'
S=Path('/workspace/divalead-setup')
c=json.loads((V/'analysis/selected_candidate.json').read_text())
dump=S/'startup-v55-Diva-parameters.tsv'
dry=render_performance(c['settings'],'startup-v55-actual-Diva',preset=V/'Diva_Lead_v55_WIP.h2p',dump=dump)
np.testing.assert_array_equal(dry,sf.read(V/'Diva_v55_VIDEO_DIVA_ONLY.wav',dtype='float32')[0])
assert dump.read_bytes()==(V/'Diva_v55_DIVA_parameters.tsv').read_bytes()
out=S/'startup-v55-full-Windows.wav'
with (S/'startup-v55-full-Windows.log').open('w') as log:
    subprocess.run([WINE,str(S/'bin/fx_render_host_v55.exe'),winpath(S/'bin/Diva_Lead_Finish_v55_WIP_x64.dll'),winpath(ROOT/'startup-v55-actual-Diva.wav'),winpath(out),'512','1',str(c['effect_parameters'][40]),'0'],env=ENV,stdout=log,stderr=log,timeout=150,check=True)
actual,rate=sf.read(out,dtype='float32')
assert rate==48000 and actual.shape==(288000,2)
np.testing.assert_array_equal(actual,sf.read(V/'Diva_v55_VIDEO_WITH_PDC.wav',dtype='float32')[0])
assert 'latency=12416' in (S/'startup-v55-full-Windows.log').read_text()
assert np.isfinite(actual).all() and np.max(abs(actual))<1
reference=Path('/workspace/attachments/c7279e3d-5fcb-48c4-b77b-f93b2c677f27/Diva_original_lead_reference.wav')
if reference.exists():
    np.testing.assert_array_equal(sf.read(reference)[0],sf.read(V/'Diva_original_lead_reference.wav')[0])
print('STARTUP55_ACTUAL_DIVA_281PARAMETERS_AND_WINDOWS_WAV_BITEXACT_PDC_PASS')
DIVA_STARTUP_PY
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/divalead/bin/python "$root/startup-check-v55.py"


# Official external VST3 runtime. Historical Finish checks above are readiness
# fixtures, not the current production effect chain. Existing setup is intact.
cd /workspace/divalead
zl_python=/workspace/.venvs/divalead/bin/python
zl_runtime=/tmp/divalead-local-1625/internet-plugins-runtime-1.4.1
zl_scripts=diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/external-plugins-20261023-02/scripts
if [ ! -x "$zl_runtime/vst3_effect_host.exe" ]; then
  if [ -e "$zl_runtime" ]; then
    echo 'Incomplete external ZL runtime exists; preserve it and choose a new destination.' >&2
    exit 1
  fi
  PYTHONDONTWRITEBYTECODE=1 "$zl_python" "$zl_scripts/setup_ZL_runtime.py" --destination "$zl_runtime"
fi
PYTHONPATH="$zl_runtime" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 "$zl_python" - <<'ZL_ACTUAL_CHECK'
from pathlib import Path
import hashlib,json,numpy as np
from win_vst3 import WinVST3,D
binary=D/'ZL Equalizer 2.vst3/Contents/x86_64-win/ZL Equalizer 2.vst3'
assert hashlib.sha256(binary.read_bytes()).hexdigest()=='3269c63a7b6c4a2cc38b249c3678efaf2759ea4a71a299020e3b67a96595028d'
public=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22')
state=public/'ZL-WIP23/verification/ZL_component.bin'
c=WinVST3('startup-ZL23-current-context-check')
try:
    c.load(state)
    impulse=np.zeros((32768,2),np.float32);impulse[4096]=[.1,.073]
    y,status=c.render(impulse);assert np.isfinite(y).all()and not np.any(y[:4096])
    assert c.latency()==0 and np.flatnonzero(np.max(abs(y),axis=1)>1e-9)[0]==4096
    c.save(D/'startup-component-resaved.bin')
    assert (D/'startup-component-resaved.bin').read_bytes()==state.read_bytes()
    receipt=dict(actual_official_VST3_execution=True,component_roundtrip_byte_exact=True,declared_PDC_frames=0,
                 impulse_added_delay_frames=0,not_a_FL_GUI_or_ASIO_test=True,reference_match_reached=False)
    (D/'STARTUP_ACTUAL_ZL_PROOF.json').write_text(json.dumps(receipt,indent=2)+'\n')
finally:c.close()
print('OFFICIAL_ZL23_ACTUAL_VST3_STATE_AND_ZERO_ADDED_BUFFER_PASS')
ZL_ACTUAL_CHECK


# Restore the verified current native base and actual Diva OscMix6.5 source.
# This delta was independently restored and byte/sample checked; it does not
# auto-start long matching jobs and does not claim a new FL GUI export.
/workspace/.venvs/divalead/bin/python -B \
  /workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/actual-Diva-OscMix6p5-fixed-independent48-confirmation/scripts/restore_verified_native_base_and_source.py \
  --archive /workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/rebased-native-bases/FL20_NATIVE_ZL_REBASED_06-verified-base.zip \
  --expected-sha256 e2be024a8ea59f051e4ff1b1043da67c2122ce8089e2e65499b25a042b1ede6c \
  --parent /tmp/divalead-local-1625 --restore-source \
  --receipt /workspace/divalead-setup/native_base06_startup_restore.json

# Install supported native saved-state/control metadata after legacy bootstrap.
# These exact scripts passed actual DLL regression; fingerprint defaults retain
# all old native base04 state hashes. Changed trials cannot load old presets.
native_current_scripts=/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/ZL23-validated-continuation/scripts
install -m 0644 "$native_current_scripts/fl20_curve.py" /tmp/divalead-local-1625/fl20_curve.py
install -m 0644 "$native_current_scripts/export_fl20_checkpoint.py" /tmp/divalead-local-1625/export_fl20_checkpoint.py
