#!/usr/bin/env python
import epylog

if __name__ == '__main__':
    epylog.logparser.notifier.start()
    epylog.routes.app.run(debug=False, host='0.0.0.0')
    epylog.logparser.notifier.stop()
