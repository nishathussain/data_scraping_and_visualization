# How to RUN
## Assignment no. 1

#### clone the repository on your machine
```
git clone https://github.com/nishathussain/data_scraping_and_visualization
cd data_scraping_and_visualization
```
#### create environment
```
conda create -n tmp_env python=3.9
conda activate tmp_env
```
#### Install requirements
```pip install -r requirements.txt```

#### Download files and preprocess them
```
cd assignment_part1
python download_EIA_data.py
python preprocess_EIA_data.py
```
#### Now either run the jupyter notebook or python script
### Notebook
```
pip install ipykernel
sudo python -m ipykernel install --name tmp_env
jupyter-notebook --ip 0.0.0.0 --port 5023
Open the notebook analysis_EIA_data.ipynb
```

### python script
```
python analysis_EIA_data.py
```
Plots will be saved inside plots folder 

## Assignment no. 2
#### Download files
```python download_EIA_dnav_monthly_data.py```

### Now either run the jupyter notebook or python script
#### Notebook
open ```analysis_EIA_data_MonthlyVsWeekly.ipynb```

#### python script to get plots 
```
python analysis_EIA_data_MonthlyVsWeekly.py
```
Plots will be saved inside plots folder 





