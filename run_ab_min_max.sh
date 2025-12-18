#!/bin/bash
#SBATCH -J try
#SBATCH --output=minmax_ab.txt
#SBATCH -N 1      # num. nodes
#SBATCH -c 30 # Number of Cores per Task
#SBATCH --mem=20G # Requested Memory
#SBATCH -t 10:00:00 # Job time limit

module load conda/latest
conda activate sage
cd /work/pi_jcrouser_smith_edu/chess_bot
python try.py