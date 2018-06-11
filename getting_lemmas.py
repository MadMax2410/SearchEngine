from os import listdir
from os.path import isfile, join

languages = ['es', 'en']
for language in languages:
    files_dir = join('data/FreeLing_outputs', language)
    output_dir = join('data/lemmas', language)
    flfiles = [f for f in listdir(files_dir) if isfile(join(files_dir, f))]
    for flfile in flfiles:
        print(flfile)
        output_file = join(output_dir, flfile)
        output = ''
        with open(join(files_dir, flfile), 'r') as f:
            for line in f:
                part = line.split()
                if len(part) == 4:
                    if part[2] == 'W': # when it is a date, we take the date as it is
                        output += part[0] + ' '
                    else:
                        output += part[1] + ' '
        with open(output_file, 'w') as f:
            f.write(output[:-1])