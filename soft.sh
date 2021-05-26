# zip parts
wget https://www.dropbox.com/s/60ge49tfqie5m1d/new.zip?dl=0
mv 'new.zip?dl=0' new.zip
wget https://www.dropbox.com/s/tev9cgmni7f1bli/new.z01?dl=0
mv 'new.z01?dl=0' new.z01
wget https://www.dropbox.com/s/hzrfurk77mqfm4a/new.z02?dl=0
mv 'new.z02?dl=0' new.z02
zip -F new.zip --out soft.zip
unzip soft.zip
rm soft.zip
