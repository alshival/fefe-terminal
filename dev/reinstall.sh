#!/bin/bash
# Move to the script's directory
cd "/home/samuel/Documents/Github/fefe-terminal/"

# Remove any existing .deb file
rm -f ./fefe.deb

# Remove any existing virtual environment
rm -rf build/usr/share/fefe/fefe-env

# Create a new virtual environment in the build directory
python3 -m venv build/usr/share/fefe/fefe-env

# Install necessary packages in the virtual environment
build/usr/share/fefe/fefe-env/bin/pip3 install -r build/usr/share/fefe/requirements.txt

# Recreate symbolic links in the build directory
rm build/usr/bin/fefe
ln -s /usr/share/fefe/fefe.py build/usr/bin/fefe
rm build/usr/bin/Fefe
ln -s /usr/share/fefe/fefe.py build/usr/bin/Fefe

rm build/usr/bin/fefe-setup
ln -s /usr/share/fefe/fefe-setup.py build/usr/bin/fefe-setup
rm build/usr/bin/Fefe-setup
ln -s /usr/share/fefe/fefe-setup.py build/usr/bin/Fefe-setup

# Build the .deb package from the build directory
dpkg-deb --build build ./fefe.deb

# Check if the .fefe.db file exists before removing
if [ -f ~/.fefe.db ]; then
    sudo rm ~/.fefe.db
fi
# Uninstall the old package
sudo dpkg -r fefe

# Install the newly built package
sudo dpkg -i fefe.deb
