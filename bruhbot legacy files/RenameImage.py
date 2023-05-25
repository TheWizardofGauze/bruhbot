import os

os.chdir(f'{os.path.dirname(__file__)}\\images')
cwd = os.getcwd()+'\\'
images = os.listdir()

for i, image in enumerate(images):
    print(f"{i}: {image}")

choice = input('Choose image to rename: ')
old = images[int(choice)]
ext = '.'+old.split('.',1)[1]
oldtag = old+' - image\n'
new = input('Enter a new name: ')+ext
newtag = new+' - image\n'
src = cwd + old
dst = cwd + new

os.rename(src, dst)

os.chdir('..')
with open('responses.txt', 'r') as f:
    file = f.readlines()
    with open('responses.txt', 'w') as f:
        for line in file:
            if line.lower() != oldtag.lower():
                f.write(line)
            elif line.lower() == oldtag.lower():
                f.write(newtag)
