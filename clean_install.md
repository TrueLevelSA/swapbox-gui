# Install process for RPi4

## Download and install Raspbian
- Use a Class10 SD card (16Gb at least)
- Download Raspbian Buster Desktop  
  `wget https://downloads.raspberrypi.org/raspbian_latest`  
  Current version: 2019-07-10
- Install Raspbian
  [https://www.raspberrypi.org/documentation/installation/installing-images/README.md](https://www.raspberrypi.org/documentation/installation/installing-images/README.md)
- Enable SSH or attach a keyboard and a monitor to your Pi

## Basic config
- In `sudo raspi-config` do
  - Expand filesystem
  - Enable Pi Camera
  - Allocate 512Mb for the GPU
- Update system
  - `sudo apt update && sudo apt upgrade -y && sudo apt dist-upgrade -y`
  - `sudo rpi-update`
  - `sudo reboot`
- Remove Menu Bar:
  - In `/etc/xdg/lxsession/LXDE-pi/autostart`:
    - Comment `@lxpanel` line 
- Disable screensaver:
  - In `/etc/lightdm/lightdm.conf`:
    - Add `xserver-command=X -s 0 -dpms` under `[Seat::*]`

## App Install

### Requirements
- Python3
- Pipenv  
  `pip3 install --upgrade pip && pip3 install pipenv --user`
- Some libs:
```bash
sudo apt install build-essential cmake pkg-config \
      zbar-tools \
      python3-numpy python3-scipy python3-matplotlib python3-pandas python3-nose \
      default-jdk ant \
      bison \
      qt4-dev-tools libqt4-dev libqtcore4 libqtgui4 \
      v4l-utils \
      libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
sudo apt install \
      libgtkglext1-dev
sudo apt install \
      libsdl2-dev
sudo apt-get install python-gtk2-dev
sudo apt install libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
```
- uv4l:
```bash
curl http://www.linux-projects.org/listing/uv4l_repo/lrkey.asc | sudo apt-key add -

echo "deb [trusted=yes] http://www.linux-projects.org/listing/uv4l_repo/raspbian/stretch stretch main" | sudo tee -a /etc/apt/sources.list
sudo apt update 
sudo apt install uv4l uv4l-raspicam uv4l-raspicam-extras 
```
  

### Process
#### Python packages install and config
- Clone the repo  
  `git clone git@gitlab.com:atola/swap-box.git`  
  `cd swap-box`
- Install the python dependencies
  - `pipenv install` (go get a coffee)
  - `pipenv run python -m pip install git+https://github.com/ymaktepi/eSSP@upgrades`
  - In `~/.kivy/config.ini` (you might have to run kivy once for it to create the file):
    - add `,param=invert_y=0` to the `%(name)s = probesysfs,provider=hidinput` line under `[input]` 

#### Zbar install
- Move to a clean directory  
  `cd ~/Downloads`  
- Download Zbar and extract it
```bash
wget http://sourceforge.net/projects/zbar/files/zbar/0.10/zbar-0.10.tar.bz2/download -O zbar-0.10.tar.bz2
bunzip2 zbar-0.10.tar.bz2 
tar -xvf zbar-0.10.tar
```
- Configure the compilation, and compile
```bash
mkdir zbar-build && cd zbar-build
../zbar-0.10/configure --prefix=/usr/local --disable-video --without-imagemagick
make -j4
make check
```
- Install the lib and configure the system to use it
```bash
sudo make install
echo "/usr/local/lib" | sudo tee -a /etc/ld.so.conf.d/zbar.conf
sudo ldconfig
```

- You can remove files in the `~/Downloads` folder

#### OpenCV install
> note: Compilation fails with some other versions

- Move to a clean directory  
  `cd ~/Downloads`  
- Download OpenCV2 and extract it
```bash
wget https://github.com/opencv/opencv/archive/2.4.13.6.zip  
unzip 2.4.13.6.zip
```
- Configure the compilation
```bash
cd opencv-2.4.13.6
mkdir build && cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
  -D WITH_QT=ON -D CMAKE_INSTALL_PREFIX=/usr/local -D WITH_OPENGL=ON \
  -D WITH_V4L=ON -D BUILD_NEW_PYTHON_SUPPORT=ON -D WITH_TBB=ON -Wno-dev ..
```
- Compile (and get a large coffee)  
  `make -j4`  
- or if you're using SSH, you may want to use screen if connection closes unexpectedly:  
  `screen make -j4`
- Install the lib and configure the system to use it
```bash
sudo make install
echo "/usr/local/lib" | sudo tee -a /etc/ld.so.conf.d/opencv.conf
sudo ldconfig
```
- You can remove files in the `~/Downloads` folder

#### QR Scanner compilation
- Install OpenCV and Zbar as explained 
- Go to the compilation folder  
  `cd PATH_REPO/qr_scanner/zbar_c`  
- Compile  
  `make`

## Run the application
`DISPLAY=:0 KIVY_GL_BACKEND=sdl2 KIVY_WINDOW=sdl2 pipenv run python template.py develop_pi`

## Service install
- Set the `launch.sh` script to start when the GUI is started:  
  `echo "@PATH_TO_REPO_FOLDER/launch.sh" | sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart`
