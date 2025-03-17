## additional functionality
#1. Implimented logic to optimise code by stopping iteration over rows once needed data is found
#2. Added a forecast column to mark forecasted and actual data

import openpyxl, os, re, datetime, pandas, glob
BASE_DIR = "./";  inp='EIA_Excel_Files';  out='processed' #"./assignment/"
all_files= [file for file in glob.glob(BASE_DIR+inp+'/**/*', recursive=True) if os.path.isfile(file)]

def get_date(addr,prefix='_base.xls'):
    """Get month and year"""
    pattern = r"([a-z]{3})(\d{2})"+prefix
    match = re.search(pattern, addr.lower())
    if match:
        month = match.group(1); year='20'+match.group(2)
        return (month,year)
# foremats: 2014-2022
for file_path in all_files:
    #file_path='./EIA_Excel_Files/2018/oct/oct18_base.xlsx'
    month,year=get_date(file_path)
    sheet_name='4atab'; found_cols=0
    xlsx_data = openpyxl.load_workbook(file_path, data_only=True)  # data_only=True ensures formulas return values
    try   : sheet = xlsx_data[sheet_name]
    except: print(f"Sheet '{sheet_name}' not found in the xlsx_data.")
    for row in sheet.iter_rows(values_only=True):  # values_only=True returns values instead of cell objects    
        if isinstance(row[0], str) and "COPRPUS" in row[0].upper():        # extract Forecasted values
            values=row[2:]; found_cols+=1
        if isinstance(row[2], int) and re.search(r"20\d{2}", str(row[2])): # extract forecasted year 
            years=list(row[2:]); found_cols+=1
            for ii in range(len(years)):
                if years[ii] is None: years[ii]=years[ii-1]
        if isinstance(row[2], str) and ('jan' == row[2].lower()): # extract forecasted month
            ds=row[2:]; found_cols+=1
            ds = [d+' '+str(y) for d,y in zip(ds,years)] # attaching year to month
            ds = [datetime.datetime.strptime(d, '%b %Y') for d in ds]
            ds = [str(d.date().year)+'-'+str(d.date().month)+'-'+str(d.date().day) for d in ds]
        if found_cols>2:
            break # optimise code to stop searching once required data is found
    
    ## Storing data frame
    data= pandas.DataFrame(data={'ds':pandas.Series(ds), 'values':pandas.Series(values)})
    data['ds']= pandas.to_datetime(data['ds']);  data['forecast']=0
    data.loc[data['ds']>=datetime.datetime.strptime(month+year,'%b%Y'),'forecast'] = 1
    
    out_file=f"{BASE_DIR}{out}/{year}/{month}/{month}{year}_base.csv"; print(f'processing: {out_file}')
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    data.to_csv(out_file, index=False)