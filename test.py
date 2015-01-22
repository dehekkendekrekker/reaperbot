from subprocess import Popen, call, PIPE


process = Popen(['airmon-ng', 'start', 'mon0'], stdout=PIPE, stderr=PIPE)
return_text = process.communicate()

if return_text[1]:


