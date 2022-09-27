import numpy as np
def name_2lines(s, min_string_size=0):
    if len(s)<=min_string_size:
        return s
    s = s.replace('\n', ' ')
    if len(s.split(' '))<=1:
        return s
    half1, half2 = s[:len(s)//2],s[len(s)//2:]
    if half1[-1] == ' ' or half2[0] == ' ':
        name = half1.strip() + '\n' + half2.strip()
    elif len(half1.split()[-1])>=len(half2.split()[0]):
        name = half1 + half2.split()[0] + '\n' + ' '.join(half2.split()[1:])
    else:
        name = ' '.join(half1.split()[0:-1]) + '\n' + half1.split()[-1] + half2
    return name

name_2lines = np.vectorize(name_2lines)