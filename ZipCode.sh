python3 -m venv /tmp/myvenv
source /tmp/myvenv/bin/activate

pip3 install -r requirements.txt

PACKAGE_PATH=/tmp/myvenv/lib/python3.*/site-packages
DIRECTORY_NAME=penny
TEMP_DIR=/tmp/$DIRECTORY_NAME
mkdir -p $TEMP_DIR

#Copy Package
rsync -rv $PACKAGE_PATH/ $TEMP_DIR/ --exclude=.git
#Copy Code
rsync -rv . $TEMP_DIR/ --exclude=.git

#Archive
cd $TEMP_DIR
zip -r $DIRECTORY_NAME.zip . -x '*.git*'
echo " $DIRECTORY_NAME.zip Created at $TEMP_DIR/" 