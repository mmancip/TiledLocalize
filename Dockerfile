# Docker file Synfig for localization of event
From mageianvidia

MAINTAINER  "Martial Mancip" <Martial.Mancip@MaisondelaSimulation.fr>

RUN dnf install -y python3-qt5 lib64qt5core5 python3-wheel python3-sip && \
    strip --remove-section=.note.ABI-tag /usr/lib64/libQt5Core.so.5
RUN python3 -m venv --system-site-packages /labelImg
RUN source /labelImg/bin/activate && \
    /labelImg/bin/python3 -m pip install --upgrade pip && \
    pip3 install labelImg && \
    pip3 uninstall -y PyQt5-sip pyqt5

