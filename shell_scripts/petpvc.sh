source /home/miniconda/etc/profile.d/conda.sh &> ./logs/null.txt
conda init bash &> ./logs/null.txt
conda activate petpvc &> ./logs/null.txt
petpvc -i $1 -o $2 --pvc VC -x 6.0 -y 6.0 -z 6.0 &&  echo 'passed' > ./logs/$3 || echo 'failed' > ./logs/$3
