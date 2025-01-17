#!/usr/bin/env python3
import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

def get_platform():
    if sys.platform.startswith('win'):
        return 'windows'
    elif sys.platform.startswith('linux'):
        return 'linux'
    else:
        raise SystemError('Unsupported platform')

def clean_build_dirs():
    """Clean build and dist directories"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    # Also clean spec files
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()

def build_portable():
    """Build portable version"""
    platform_name = get_platform()
    clean_build_dirs()
    
    # Build command with all options
    cmd = [
        'pyinstaller',
        '--clean',
        '--onefile',
        '--windowed',
        '--name=TinyTask',
        f'--icon=icon.svg',
        '--noconfirm',
        '--add-data=src/ui:ui',
        '--add-data=src/utils:utils',
        '--add-data=src/models:models',
        '--paths=src',
        'src/main.py'
    ]
    
    # Run PyInstaller
    subprocess.run(cmd, check=True)
    
    # Rename the output file based on platform
    source_file = 'dist/TinyTask'
    if platform_name == 'windows':
        source_file += '.exe'
        target_file = 'TinyTask-portable-windows.exe'
    else:
        target_file = 'TinyTask-portable-linux'
    
    # Remove target file if it exists
    if os.path.exists(target_file):
        if os.path.isdir(target_file):
            shutil.rmtree(target_file)
        else:
            os.remove(target_file)
    
    shutil.move(source_file, target_file)
    print(f"Created portable executable: {target_file}")
    
    # Make the Linux binary executable
    if platform_name == 'linux':
        os.chmod(target_file, 0o755)
    
    # Clean up build directories
    clean_build_dirs()

def create_windows_installer():
    """Create Windows installer using NSIS"""
    # First build the portable executable
    build_portable()
    
    # Create NSIS script
    nsis_script = '''
    !include "MUI2.nsh"
    !include "FileFunc.nsh"
    
    Name "TinyTask"
    OutFile "TinyTask-Setup.exe"
    InstallDir "$PROGRAMFILES\\TinyTask"
    RequestExecutionLevel admin
    
    !define MUI_ABORTWARNING
    !define MUI_ICON "icon.svg"
    !define MUI_UNICON "icon.svg"
    
    !insertmacro MUI_PAGE_WELCOME
    !insertmacro MUI_PAGE_DIRECTORY
    !insertmacro MUI_PAGE_INSTFILES
    !insertmacro MUI_PAGE_FINISH
    
    !insertmacro MUI_UNPAGE_WELCOME
    !insertmacro MUI_UNPAGE_CONFIRM
    !insertmacro MUI_UNPAGE_INSTFILES
    !insertmacro MUI_UNPAGE_FINISH
    
    !insertmacro MUI_LANGUAGE "English"
    
    Section "MainSection" SEC01
        SetOutPath "$INSTDIR"
        SetOverwrite on
        
        File "TinyTask-portable-windows.exe"
        Rename "$INSTDIR\\TinyTask-portable-windows.exe" "$INSTDIR\\TinyTask.exe"
        
        CreateDirectory "$SMPROGRAMS\\TinyTask"
        CreateShortCut "$SMPROGRAMS\\TinyTask\\TinyTask.lnk" "$INSTDIR\\TinyTask.exe"
        CreateShortCut "$DESKTOP\\TinyTask.lnk" "$INSTDIR\\TinyTask.exe"
        
        WriteUninstaller "$INSTDIR\\uninstall.exe"
        
        ; Write registry keys for uninstall
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\TinyTask" "DisplayName" "TinyTask"
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\TinyTask" "UninstallString" "$INSTDIR\\uninstall.exe"
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\TinyTask" "DisplayIcon" "$INSTDIR\\TinyTask.exe"
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\TinyTask" "Publisher" "Ali Eren Altındağ"
        
        ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
        IntFmt $0 "0x%08X" $0
        WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\TinyTask" "EstimatedSize" "$0"
    SectionEnd
    
    Section "Uninstall"
        Delete "$INSTDIR\\TinyTask.exe"
        Delete "$INSTDIR\\uninstall.exe"
        
        Delete "$SMPROGRAMS\\TinyTask\\TinyTask.lnk"
        Delete "$DESKTOP\\TinyTask.lnk"
        
        RMDir "$SMPROGRAMS\\TinyTask"
        RMDir "$INSTDIR"
        
        DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\TinyTask"
    SectionEnd
    '''
    
    with open('installer.nsi', 'w') as f:
        f.write(nsis_script)
    
    # Run NSIS compiler
    subprocess.run(['makensis', 'installer.nsi'], check=True)
    print("Created Windows installer: TinyTask-Setup.exe")

def create_linux_installer():
    """Create Linux .deb package"""
    # First build the portable executable
    build_portable()
    
    # Setup .deb package structure
    package_name = "tinytask"
    version = "1.0.0"
    arch = "amd64"
    maintainer = "Ali Eren Altındağ <alierenaltindaag@gmail.com>"
    
    # Create package directory structure
    package_root = f"{package_name}_{version}_{arch}"
    os.makedirs(f"{package_root}/DEBIAN", exist_ok=True)
    os.makedirs(f"{package_root}/usr/local/bin", exist_ok=True)
    os.makedirs(f"{package_root}/usr/share/applications", exist_ok=True)
    os.makedirs(f"{package_root}/usr/share/icons/hicolor/scalable/apps", exist_ok=True)
    
    # Create control file
    control_content = f'''Package: {package_name}
Version: {version}
Architecture: {arch}
Maintainer: {maintainer}
Description: TinyTask - Macro Recorder
 A lightweight macro recorder for mouse and keyboard actions.
 Records and plays back mouse movements, clicks, and keyboard inputs.
Priority: optional
Section: utils
'''
    
    with open(f"{package_root}/DEBIAN/control", 'w') as f:
        f.write(control_content)
    
    # Copy executable
    shutil.copy2("TinyTask-portable-linux", f"{package_root}/usr/local/bin/tinytask")
    os.chmod(f"{package_root}/usr/local/bin/tinytask", 0o755)
    
    # Copy icon
    shutil.copy2("icon.svg", f"{package_root}/usr/share/icons/hicolor/scalable/apps/tinytask.svg")
    
    # Create .desktop file
    desktop_content = '''[Desktop Entry]
Name=TinyTask
Comment=Record and play mouse and keyboard macros
Exec=/usr/local/bin/tinytask
Icon=tinytask
Terminal=false
Type=Application
Categories=Utility;
Keywords=macro;record;automation;
'''
    
    with open(f"{package_root}/usr/share/applications/tinytask.desktop", 'w') as f:
        f.write(desktop_content)
    
    # Build .deb package
    subprocess.run(['dpkg-deb', '--build', '--root-owner-group', package_root], check=True)
    print(f"Created Linux installer: {package_root}.deb")

def build_installer():
    """Build installer version"""
    platform_name = get_platform()
    
    if platform_name == 'windows':
        try:
            create_windows_installer()
        except subprocess.CalledProcessError:
            print("Error: NSIS is required to create Windows installer.")
            print("Please install NSIS (https://nsis.sourceforge.io/)")
            sys.exit(1)
    else:
        try:
            create_linux_installer()
        except subprocess.CalledProcessError:
            print("Error: dpkg-deb is required to create Linux installer.")
            print("Please install dpkg-deb (sudo apt-get install dpkg)")
            sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python build.py [portable|installer|all]")
        sys.exit(1)
    
    build_type = sys.argv[1].lower()
    
    if build_type == 'portable':
        build_portable()
    elif build_type == 'installer':
        build_installer()
    elif build_type == 'all':
        build_portable()
        build_installer()
    else:
        print("Invalid build type. Use: portable, installer, or all")
        sys.exit(1)

if __name__ == '__main__':
    main() 