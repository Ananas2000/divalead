"""Fetch Xvfb from the authenticated Debian package index; use only in /tmp."""
from pathlib import Path
import hashlib, json, lzma, subprocess, urllib.request

W = Path(__file__).resolve().parent
def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()

release_bytes = fetch('https://deb.debian.org/debian/dists/trixie/InRelease')
(W/'debian-InRelease').write_bytes(release_bytes)
gpg_home = W/'gpg-home'
gpg_home.mkdir(exist_ok=True, mode=0o700)
command = ['gpg', '--batch', '--homedir', str(gpg_home), '--no-default-keyring',
           '--keyring', '/usr/share/keyrings/debian-archive-keyring.gpg',
           '--verify', str(W/'debian-InRelease')]
result = subprocess.run(command, capture_output=True, text=True, check=True)
(W/'debian-release-signature-verification.log').write_text(result.stdout+result.stderr)
lines = release_bytes.decode().split('SHA256:\n',1)[1].split('\n\n',1)[0].splitlines()
expected, size, rel = next(line.split() for line in lines
                          if line.strip().endswith('main/binary-amd64/Packages.xz'))
packages = fetch('https://deb.debian.org/debian/dists/trixie/'+rel)
assert len(packages) == int(size) and hashlib.sha256(packages).hexdigest() == expected
entry = next(e for e in lzma.decompress(packages).decode().split('\n\n')
             if e.startswith('Package: xvfb\n'))
info = dict(line.split(': ',1) for line in entry.splitlines()
            if ': ' in line and not line.startswith(' '))
deb = fetch('https://deb.debian.org/debian/'+info['Filename'])
actual = hashlib.sha256(deb).hexdigest()
assert actual == info['SHA256'] and len(deb) == int(info['Size'])
(W/'xvfb-verified.deb').write_bytes(deb)
report = dict(release_signature_exit=result.returncode, verification_command=command,
              Packages_xz_signed_SHA256=expected, package_version=info['Version'],
              package_filename=info['Filename'], deb_SHA256=actual, verified=True)
(W/'xvfb-package-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report), flush=True)
