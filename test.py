from subprocess import Popen, call, PIPE

proc = Popen(['airodump-ng', '-i', 'mon0', '-w', '/tmp/bleh.csv', '--output-format', 'csv'], stdout=PIPE, stderr=PIPE)
result = proc.communicate()
return_code = proc.returncode

if return_code
print return_code