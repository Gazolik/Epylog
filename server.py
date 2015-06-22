#!/usr/bin/env python
import epylog

if __name__ == "__main__":
    epylog.routes.app.run(debug=True, host = '0.0.0.0')
    epylog.logparser.notifier.stop()
