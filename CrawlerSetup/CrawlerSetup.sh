# for mac
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew reinstall python
sudo easy_install pip
sudo mv chromedriver /usr/local/bin/
cd beautifulsoup4-4.1.0/
sudo python setup.py install
