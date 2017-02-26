# =============================================================================
# Install Python
# =============================================================================
apt-get update
apt-get install -y libssl-dev libbz2-dev
cd /usr/src
wget https://www.python.org/ftp/python/2.7.12/Python-2.7.12.tgz
tar xzf Python-2.7.12.tgz
rm Python-2.7.12.tgz
cd Python-2.7.12
./configure
make altinstall
cd ..
rm -rf Python-2.7.12
python2.7 --version

# =============================================================================
# Install Pip
# =============================================================================
cd /usr/src
wget https://pypi.python.org/packages/source/d/distribute/distribute-0.7.3.zip
unzip distribute-0.7.3.zip
cd distribute-0.7.3
python2.7 setup.py install
easy_install-2.7 pip


# =============================================================================
# Install my version of python-lightify
# =============================================================================
pip2.7 install https://github.com/durera/python-lightify/archive/master.zip

# =============================================================================
# Install Supervisord
# =============================================================================
apt-get install -y supervisor

# =============================================================================
# Install the application itself
# =============================================================================
mkdir -p /opt/ibm/gateway-lightify
cd /opt/ibm/gateway-lightify
wget https://raw.githubusercontent.com/ibm-watson-iot/gateway-hue/master/gateway-lightify.py
wget https://raw.githubusercontent.com/ibm-watson-iot/gateway-hue/master/supervisord/gateway-lightify.conf -O /etc/supervisor/conf.d/gateway-lightify.conf
