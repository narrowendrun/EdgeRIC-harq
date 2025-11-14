apt remove --purge libuhd* uhd-host -y
apt autoremove -y

apt-get install autoconf automake build-essential ccache cmake cpufrequtils doxygen ethtool \
g++ git inetutils-tools libboost-all-dev libncurses5 libncurses5-dev libusb-1.0-0 libusb-1.0-0-dev \
libusb-dev python3-dev python3-mako python3-numpy python3-requests python3-scipy python3-setuptools \
python3-ruamel.yaml -y

cd /usr/local/src/uhd
git checkout UHD-4.9

cd host/build
cmake ../
make -j `nproc`
make install
ldconfig
uhd_images_downloader
uhd_find_devices


#git checkout UHD-4.7
#cmake ../
#make -j `nproc`
#make install



cd /home/EdgeRIC-A-real-time-RIC

