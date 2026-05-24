# cleanup_bcrypt.py
import site, shutil, glob, os

paths = set(site.getsitepackages() + [site.getusersitepackages()])
for p in paths:
    for t in ('bcrypt', 'bcrypt-*dist-info', 'bcrypt-*egg-info'):
        for q in glob.glob(os.path.join(p, t + '*')):
            print('Removing', q)
            shutil.rmtree(q, ignore_errors=True)
