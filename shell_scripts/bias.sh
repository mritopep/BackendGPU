source /home/miniconda/etc/profile.d/conda.sh &> ./logs/null.txt
conda init bash &> ./logs/null.txt
conda activate simple_itk &> ./logs/null.txt
python soft/bias_field_correction.py $1 $2 &&  echo 'passed' > ./logs/$3 || echo 'failed' > ./logs/$3
