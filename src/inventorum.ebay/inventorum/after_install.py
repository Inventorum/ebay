#!/usr/bin/env python
import os
import subprocess

"""
script running as post-install deb-package script.

unfortunately this is executed in ``/var/lib`` which forces us
to hardcode paths.
"""

print "performing after install actions..."

install_dir = '/%s' % os.path.join('opt', 'inventorum', 'ebay')

try:
    # remove old install config
    os.remove('/' + os.path.join('etc', 'uwsgi', 'apps-enabled', 'com.inventorum.ebay.ini'))
except OSError:
    pass

links = [
    (os.path.join(install_dir, 'etc', 'uwsgi', 'apps-available', 'com.inventorum.ebay.ini'),
        '/' + os.path.join('etc', 'uwsgi', 'apps-enabled', 'com.inventorum.ebay.ini', )),
]

for tup in links:
    src = tup[0]
    dst = tup[1]
    if not os.path.exists(dst):
        print '[inv-ebay] creating symlink for %s to %s...' % (src, dst)
        # might be a broken link
        try:
            os.remove(dst)
        except OSError:
            pass
        os.symlink(src, dst)

log_path = os.path.join('/', 'var', 'log', 'uwsgi')
print '[inv-ebay] set permissions of log locations: %s...' % (log_path,)
permissions_cmd = [
    'chmod', '-R', '0777',
    log_path,
]
proc = subprocess.Popen(permissions_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
_out, _err = proc.communicate()
print '[inv-ebay] %s' % _out
if proc.returncode != 0:
    print '[inv-ebay] %s' % _err
    exit(proc.returncode)

print ""
print "[inv-ebay] restart you application services::"
print ""
print "    service nginx reload"
print "    service uwsgi reload"
print ""
