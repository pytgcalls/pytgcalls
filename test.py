import os
import sys
dist_package = ''
for item in sys.path:
    if 'site-packages' in item or 'site-packages' in item:
        dist_package = item
        break
print(dist_package)

# result_cmd = os.popen(f'python3.8 -m site').read()