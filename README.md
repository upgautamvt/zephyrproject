# Setup
Connect Nordic development kit (i.e., nRF52840dk) to USB J2 and put the toggle to VDD (not USB). Then `lsusb` will show SEGGER.. device you install SEGGET JLink software (Link: https://www.segger.com/downloads/jlink/

```bash
sudo apt update
sudo apt upgrade
sudo apt install --no-install-recommends git cmake ninja-build gperf \
  ccache dfu-util device-tree-compiler wget \
  python3-dev python3-pip python3-setuptools python3-tk python3-wheel xz-utils file \
  make gcc gcc-multilib g++-multilib libsdl2-dev libmagic1
sudo apt install git gcc-arm-none-eabi make gcc-multilib libstdc++-arm-none-eabi-newlib openocd gdb-multiarch doxygen wget unzip python3-serial
```

Install west build management tool in python virtual env
```bash
sudo apt install python3-venv
python3 -m venv ~/zephyrproject/.venv
source ~/zephyrproject/.venv/bin/activate
pip install -U west
west init ~/zephyrproject
cd ~/zephyrproject
west update
west zephyr-export
west packages pip --install
(or, as alternative, we can even put everything in virtual env: pip install -r ~/zephyrproject/zephyr/scripts/requirements.txt)
west sdk install
```

Also install these tools
```bash
upgautamvt@pc32gb:~/Downloads/nRF52840dk$ ls
 JLink_Linux_V844a_x86_64.deb                          nRF52840_DK_User_Guide_20201203.pdf
 j-link-ob-sam3u128-v2-nordicsemi-170724.bin           nrf5x_atsam3u2c_if_mbed_v0221_11012017.bin
 nrf52840-development-kit---hardware-files-3_0_2.zip   nrf-udev_1.0.1-all.deb
'nRF52840 DK Peripheral UART demo.zip'
upgautamvt@pc32gb:~/Downloads/nRF52840dk$ sudo dpkg -i nrf-udev_1.0.1-all.deb 
Selecting previously unselected package nrf-udev.
(Reading database ... 467856 files and directories currently installed.)
Preparing to unpack nrf-udev_1.0.1-all.deb ...
Unpacking nrf-udev (1.0.1) ...
Setting up nrf-udev (1.0.1) ...
Reloading udev rules...
upgautamvt@pc32gb:~/Downloads/nRF52840dk$ sudo dpkg -i ./JLink_Linux_V844a_x86_64.deb 
(Reading database ... 467858 files and directories currently installed.)
Preparing to unpack ./JLink_Linux_V844a_x86_64.deb ...
Removing /opt/SEGGER/JLink ...
Unpacking jlink (8.44.1) over (8.44.1) ...
Setting up jlink (8.44.1) ...
Updating udev rules via udevadm...
OK
upgautamvt@pc32gb:~/Downloads/nRF52840dk$ 
```

Also, we need `nrfutil` in our `~/.local/bin` so configure it. We downloaded nrfutil here: https://www.nordicsemi.com/Products/Development-tools/nRF-Util, and pasted it in `~/.local/bin` directory.
```bash
echo 'export PATH=~/.local/bin:"$PATH"' >> ~/.bashrc
source ~/.bashrc
chmod +x ~/.local/bin/nrfutil
```

We install device plugin that allows to detect connected Nordic boards (e.g., ours nRF52840-DK) over USB. You can use `nrfutil device list` to list the connected devices. 

completion is for shell auto completion, so when combined with install bash, we installed shell auto completion for bash shell. 

```bash
nrfutil install device
nrfutil install completion
nrfutil completion install bash
```

If you get `nrfutil device list` this error as below, you need to install SEGGER's JLink software
```bash
(.venv) upgautamvt@pc32gb:~/zephyrproject$ nrfutil device list
WARNING: JLinkARM DLL not found. Devices that require J-Link will not be recognized correctly, and J-Link operations will not be available. Install SEGGER J-Link from https://www.segger.com/downloads/jlink/. Currently tested version: JLink_V8.18.

Supported devices found: 0
```
Then download the software from here (https://www.segger.com/downloads/jlink/) and install. Then run
```bash
(.venv) upgautamvt@pc32gb:~/zephyrproject$ nrfutil device list
Supported devices found: 0
```

This step is only necessary if you plan to build Zephyr without using west — i.e., with raw cmake or ninja commands.
After running west zephyr-export, you can do something like this in your app directory:

```bash
mkdir build && cd build
cmake -GNinja -DBOARD=qemu_x86 ..
ninja
```

Without this export, cmake might not find Zephyr, and you'd get an error like:

```bash
CMake Error at CMakeLists.txt:4 (find_package):
  By not providing "FindZephyr.cmake" in CMAKE_MODULE_PATH...
```

By default, sdk gets intalled in ~/zephyr-sdk-<version>/

Now, configure zephyr related environment variables. More here: https://docs.zephyrproject.org/latest/develop/env_vars.html

```bash
export ZEPHYR_TOOLCHAIN_VARIANT=zephyr
export ZEPHYR_SDK_INSTALL_DIR=/home/upgautamvt/zephyr-sdk-0.17.1
export ZEPHYR_BASE=/home/upgautamvt/zephyrproject/zephyr
```

Now, you can still stay on directory ~/zephyrproject/zephyr, and trigger the build or flash or do everything from that directory. Make sure you connect board before flashing. Sometimes, flash may not work because of udev not configured. 

```bash
cd ~/zephyrproject

# west build -p always -b <board_soc> zephyr/samples/basic/blinky
# west build -p always -b nrf52840_pca10056 -d build_hello  zephyr/samples/basic/blinky
west build -p always -b nrf52840dk/nrf52840 -d build_hello  zephyr/samples/basic/blinky

# or you can build sample helloword application in QEMU
# From the root of the zephyr repository
west build -p always -b qemu_x86 -d build_hello zephyr/samples/hello_world
west build -t run
```

Running app natively,
```bash
upgautamvt@pc32gb:~/zephyrproject$ west build -p always -b native_sim -d build_native_sim zephyr/samples/hello_world
upgautamvt@pc32gb:~/zephyrproject$ west build -t run
or just run zephyr.exe directly:
upgautamvt@pc32gb:~/zephyrproject$ ./build_native_sim/zephyr/zephyr.exe
upgautamvt@pc32gb:~/zephyrproject$ file ./build_native_sim/zephyr/zephyr.exe
./build_native_sim/zephyr/zephyr.exe: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lid
# Note. this is windows style .exe extension only. And they used keyword native_sim to build directly in Linux.
```

Setting Udev rules, 
Udev is a device manager for the Linux kernel and the udev daemon handles all user space events raised when a hardware device is added (or removed) from the system. We can add a rules file to grant access permission by non-root users to certain USB-connected devices.

Either download the OpenOCD rules file and copy it to the right location
```bash
wget -O 60-openocd.rules https://sf.net/p/openocd/code/ci/master/tree/contrib/60-openocd.rules?format=raw
sudo cp 60-openocd.rules /etc/udev/rules.d
```
or copy the rules file from the Zephyr SDK folder,
```bash
sudo cp ${ZEPHYR_SDK_INSTALL_DIR}/sysroots/x86_64-pokysdk-linux/usr/share/openocd/contrib/60-openocd.rules /etc/udev/rules.d
```
Now, reload udev daemon,
```bash
sudo udevadm control --reload
```
Unplug and plug in the USB connection to your board, and you should have permission to access the board hardware for flashing. There is no harm unless you corrupt the bootloader (which Zephyr doesn’t usually do unless you're specifically flashing a bootloader)

```bash
west flash -d build (or west flash -d build_hello) because build are build directories
```

Everything worked!

Flashing mean writing your compiled Zephyr application binary (zephyr.elf, zephyr.hex, etc.) into the board's internal flash memory so that it runs on boot.

Inside ~/zephyrproject, create files .gitignore, .gitmodules, and create_gitmodules.py

## .gitignore
```bash
.west/
.venv/
```

## create_gitmodules.py
I created this python script becasue this project contains so many git submodules inside (recursively nested), and I needed to scan and list all them in my root's .gitsubmodules. To get their corresponding remote url, I ran ` west list -f '{path}: {url}'`

```python
import os
import subprocess
import sys
from configparser import ConfigParser

def get_main_repo_root(start_path):
    """Find the root of the main Git repository."""
    current = os.path.abspath(start_path)
    while True:
        git_path = os.path.join(current, '.git')
        if os.path.exists(git_path):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            sys.exit(f"Error: No Git repository found in {start_path} or parents")
        current = parent

def is_git_repo(path):
    """Check if a directory is a Git repo (handles both dir and file .git)"""
    git_path = os.path.join(path, '.git')
    if not os.path.exists(git_path):
        return False
    
    if os.path.isdir(git_path):
        return True
    
    if os.path.isfile(git_path):
        try:
            with open(git_path, 'r') as f:
                return 'gitdir:' in f.read()
        except:
            return False
    
    return False

def get_git_url(path):
    """Get the remote URL for a Git repo"""
    try:
        url = subprocess.check_output(
            ['git', '-C', path, 'config', '--get', 'remote.origin.url'],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        return url if url else None
    except subprocess.CalledProcessError:
        return None

def get_west_urls(main_root):
    """Get URLs from west manifest"""
    try:
        west_cmd = os.path.join(os.environ.get('VIRTUAL_ENV', ''), 'bin', 'west') or 'west'
        output = subprocess.check_output(
            [west_cmd, 'list', '-f', '{path}:{url}'],
            cwd=main_root, text=True, stderr=subprocess.DEVNULL
        ).strip()
        return dict(line.split(':', 1) for line in output.splitlines() if ':' in line)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def find_submodules(main_root):
    """Find all submodule directories within the main repo."""
    west_urls = get_west_urls(main_root)
    main_dot_git = os.path.realpath(os.path.join(main_root, '.git'))
    submodules = []
    skipped = []
    
    for root, dirs, files in os.walk(main_root):
        if 'vendor' in dirs:
            dirs.remove('vendor')
        
        if not is_git_repo(root):
            continue
            
        git_path = os.path.realpath(os.path.join(root, '.git'))
        if git_path == main_dot_git:
            continue

        rel_path = os.path.relpath(root, main_root).replace('\\', '/')
        
        # Try west URL first, then git config
        url = west_urls.get(rel_path) if west_urls else None
        if not url:
            url = get_git_url(root)
        
        if url:
            submodules.append((rel_path, url))
        else:
            skipped.append(rel_path)
            
        dirs[:] = []
    
    if skipped:
        print("\nSkipped repositories (no remote URL found):")
        for path in skipped:
            print(f"  {path}")
    
    return submodules

def update_gitmodules(main_root, submodules):
    """Update or create the .gitmodules file."""
    gitmodules_path = os.path.join(main_root, '.gitmodules')
    config = ConfigParser()
    
    if os.path.exists(gitmodules_path):
        config.read(gitmodules_path)
    
    for path, url in submodules:
        section = f'submodule "{path}"'
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, 'path', path)
        config.set(section, 'url', url)
    
    with open(gitmodules_path, 'w') as f:
        config.write(f)

def main():
    start_path = os.getcwd()
    try:
        main_root = get_main_repo_root(start_path)
        print(f"Main repository: {main_root}")
        
        submodules = find_submodules(main_root)
        if not submodules:
            print("\nNo submodules found with remote URLs")
            return
            
        update_gitmodules(main_root, submodules)
        print("\nUpdated .gitmodules with:")
        for path, url in submodules:
            print(f"  {path}: {url}")
            
    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
```

And, now run `python ./create_gitmodules.py`. Done!
