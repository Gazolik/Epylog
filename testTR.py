import time
# import pyinotify

# wm = pyinotify.WatchManager()
# mask = pyinotify.IN_MODIFY
# notifier = pyinotify.Notifier(wm)
# wdd = wm.add_watch('fichierTest',mask, rec = True)
def analyseFichier():
    fileName = input('Name of file ?')

    try:
        file = open(fileName,'r')
    except IOError as e:
        print('IO error')

    while 1:
        where = file.tell()
        line = file.readline()
        if not line:
            time.sleep(5)
            #notifier.check_events()
            print('sleep')
            file.close()
            try:
                file = open(fileName,'r')
            except IOError as e:
                print('IO error')
            else:
                file.seek(where)
        else:
            print(line)

    file.close()
