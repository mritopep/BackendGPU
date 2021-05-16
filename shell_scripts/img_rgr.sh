source /home/miniconda/etc/profile.d/conda.sh &> ./logs/null.txt
conda init bash &> ./logs/null.txt
conda activate simple_itk &> ./logs/null.txt
python soft/image_rgr.py $1 $2 $3 &&  echo 'passed' > ./logs/$4 || echo 'failed' > ./logs/$4
