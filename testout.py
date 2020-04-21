import subprocess as sub

filename = "cifar10_tutorial.py"
p = sub.Popen(['python', filename], stdout=sub.PIPE, stderr=sub.STDOUT, encoding='utf-8')
while True:
    next_line = p.stdout.readline()
    if next_line == '' and p.poll() is not None:
        break
    print(next_line)
# for line in iter(p.stdout.readline, b''):
#     print(line,)
# p.stdout.close()