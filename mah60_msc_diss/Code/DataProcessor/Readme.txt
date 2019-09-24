For the data processor the following packages must be installed:

python 3.7.3 

cycler==0.10.0
fpdf==1.7.2
kiwisolver==1.1.0
matplotlib==3.1.1
mysql==0.0.2
mysql-connector-python==8.0.17
mysqlclient==1.4.4
numpy==1.17.1
pandas==0.25.1
pyparsing==2.4.2
python-dateutil==2.8.0
pytz==2019.2
six==1.12.0

You can check what you have in windows 10 command line by :  pip freeze
Version of python can be checked in command line by typing : python

Without these packages or an ealier version the application may not work.

The application can be ran using : python application.py
The Unit tests can be ran using : python data_proccessor_unittests.py

To modify the data being imputed and outputted. Please use the config.py file.