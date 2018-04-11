import datetime

# this script is called by MAT using the following command (must use absolute paths)
# MAT_Process("C:\\Program Files\\Python 3.5\\python.exe C:\\Users\\abc\\Desktop\\notch_filter\\MAT_test.py", 0, 1, INFINITE);

print(datetime.datetime.utcnow())
print("Interface with MAT is good!")