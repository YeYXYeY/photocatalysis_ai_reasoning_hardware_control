import pandas as pd

dosing_head_df = pd.read_excel(R'E:\Users\1250\Desktop\photocatalytic-automation\coordinates\dosing_head.xlsx')
x_solvent, y_solvent, z_solvent, addr_solvent = dosing_head_df.loc[
    dosing_head_df["usage"] == "D1", ["X", "Y", "Z", "addr"]
].values[0]
addr_solvent = "0" + str(addr_solvent)[0]
print(type(addr_solvent))
print(addr_solvent)
