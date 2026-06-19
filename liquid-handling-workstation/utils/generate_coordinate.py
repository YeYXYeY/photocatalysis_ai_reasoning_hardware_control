import pandas as pd

file_namte = "../coordinates/reaction.xlsx"
df = pd.read_excel(file_namte)

# xy
filtered_df = df.dropna(subset=["X", "Y"])
coor_dict = {}
for index, rows in filtered_df.iterrows():
    no = int(rows['NO'])
    x = rows['X']
    y = rows['Y']
    coor_dict[f'{index+1}'] = [x, y]
x1, y1 = coor_dict['1'][0], coor_dict['1'][1]
x2, y2 = coor_dict['5'][0], coor_dict['5'][1]
x3, y3 = coor_dict['25'][0], coor_dict['25'][1]
del_x = (coor_dict['5'][0] - coor_dict['1'][0]) / 4
del_y = (coor_dict['25'][1] - coor_dict['1'][1]) / 4
print(del_x,del_y)
i = 0
for col in range(0, 5):
    for row in range(0, 5):
        x = x1 + row * del_x
        y = y1 + col * del_y
        print(x,y)
        df.at[i,'X'] = x
        df.at[i,'Y'] = y
        i+=1
        if i >= 25:
            break

df.to_excel(file_namte,index=False)
