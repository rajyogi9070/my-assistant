#!/usr/bin/env python3
"""
Build script for My Assistant
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a shell command"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    print(result.stdout)
    return result


def clean():
    """Clean build artifacts"""
    print("Cleaning build artifacts...")
    dirs_to_clean = ['build/dist', 'build/build', '__pycache__', 'dist']
    for d in dirs_to_clean:
        if Path(d).exists():
            shutil.rmtree(d)
    print("Clean complete")


def install_deps():
    """Install dependencies"""
    print("Installing dependencies...")
    run_command("pip install -e .[dev]")


def run_tests():
    """Run tests"""
    print("Running tests...")
    run_command("pytest tests/ -v")


def lint():
    """Run linters"""
    print("Running linters...")
    run_command("black src/ --check")
    run_command("ruff check src/")


def build_exe():
    """Build executable"""
    print("Building executable...")
    run_command("pyinstaller build/assistant.spec --clean --noconfirm")
    print("Build complete: dist/MyAssistant/")


def create_installer():
    """Create Windows installer"""
    print("Creating installer...")
    # Inno Setup compiler
    iscc_path = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if Path(iscc_path).exists():
        run_command(f'"{iscc_path}" installer/setup.iss')
    else:
        print("Warning: Inno Setup not found. Please install Inno Setup 6.")
        print("Download from: https://jrsoftware.org/isdl.php")


def create_portable():
    """Create portable zip"""
    print("Creating portable package...")
    import zipfile
    
    dist_dir = Path("dist/MyAssistant")
    if not dist_dir.exists():
        print("Error: Build not found. Run build_exe first.")
        return
    
    zip_path = Path("dist/MyAssistant-Portable.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in dist_dir.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(dist_dir)
                zf.write(file, arcname)
    
    print(f"Portable package created: {zip_path}")


def generate_checksums():
    """Generate SHA-256 checksums"""
    print("Generating checksums...")
    import hashlib
    
    dist_dir = Path("dist")
    if not dist_dir.exists():
        return
    
    checksums = []
    for file in dist_dir.glob('*'):
        if file.is_file() and not file.suffix == '.sha256':
            sha256 = hashlib.sha256(file.read_bytes()).hexdigest()
            checksums.append(f"{sha256}  {file.name}")
    
    checksum_file = dist_dir / "checksums.sha256"
    checksum_file.write_text('\n'.join(checksums))
    print(f"Checksums saved to {checksum_file}")


def main():
    """Main build process"""
    if len(sys.argv) < 2:
        print("Usage: python build.py [command]")
        print("Commands: clean, deps, test, lint, build, installer, portable, all")
        sys.exit(1)
    
    command = sys.argv[1]
    
    commands = {
        'clean': clean,
        'deps': install_deps,
        'test': run_tests,
        'lint': lint,
        'build': build_exe,
        'installer': create_installer,
        'portable': create_portable,
        'checksums': generate_checksums,
    }
    
    if command == 'all':
        clean()
        install_deps()
        run_tests()
        build_exe()
        create_installer()
        create_portable()
        generate_checksums()
    elif command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
