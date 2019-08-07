sudo apt install zbar-tools
sudo apt install build-essential cmake pkg-config
sudo apt-get install python-numpy python-scipy python-matplotlib python-pandas python-nose
sudo apt-get install python3-numpy python3-scipy python3-matplotlib python3-pandas python3-nose
sudo apt-get install python-numpy python-scipy python-matplotlib python-pandas python-nose
sudo apt-get install default-jdk ant
sudo apt-get install libgtkglext1-dev
sudo apt-get install bison
sudo apt-get install qt4-dev-tools libqt4-dev libqtcore4 libqtgui4
sudo apt-get install v4l-utils
sudo apt-get install build-essential cmake pkg-config
sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
sudo apt-get install libgtkglext1-dev
wget http://www.linux-projects.org/listing/uv4l_repo/lrkey.asc && sudo apt-key add ./lrkey.asc
curl http://www.linux-projects.org/listing/uv4l_repo/lrkey.asc | sudo apt-key add -
sudo vim /etc/apt/sources.list
# add "deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/stretch stretch main"
sudo apt-get update 
sudo apt-get install uv4l uv4l-raspicam uv4l-raspicam-extras 
#
#
# MAIN DIFFERENCE WITH TUTORIAL IS OPENCV VERSION
#
#
wget https://github.com/opencv/opencv/archive/2.4.13.6.zip
unzip 2.4.13.6.zip 
cd opencv-2.4.13.6/
ls
mkdir build
cd doc/
cd build/
cmake -D CMAKE_BUILD_TYPE=RELEASE -D INSTALL_C_EXEMPLES=ON -D INSTALL_PYTHON_EXEMPLES=ON -D BUILD_EXEMPLES=ON -D WITH_QT=ON -D CMAKE_INSTALL_PREFIX=/usr/local -D WITH_OPENGL=ON -D WITH_V4L=ON -D BUILD_NEW_PYTHON_SUPPORT=ON -D WITH_TBB=ON -Wno-dev .. 
make -j4
cd git/swap-box/qr_scanner/zbar_c/
cd opencv-2.4.13.6/
cd build/
make -j4
cd ..
sudo poweroff 
cd git/swap-box/qr_scanner/
cd zbar_c/
cd opencv-2.4.13.6/
cd build/
make -j4
sudo make install
# add /usr/local/lib in there
sudo nano /etc/ld.so.conf.d/opencv.conf
sudo ldconfig
sudo nano /etc/bash.bashrc
cd ..
make
sudo apt-get install python-gtk2-dev
wget http://sourceforge.net/projects/zbar/files/zbar/0.10/zbar-0.10.tar.bz2/download -O zbar-0.10.tar.bz2
bunzip2 zbar-0.10.tar.bz2 
tar -xvf zbar-0.10.tar 
mkdir zbar-build
cd zbar-
cd zbar-build/
../zbar-0.10/configure     --prefix=/usr/local     --disable-video     --without-imagemagick
make -j4
make check
sudo make install
# add /usr/local/lib in there
sudo nano /etc/ld.so.conf.d/zbar.conf
sudo ldconfig 
cd ..
make
./main.run 
