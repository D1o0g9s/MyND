import pandas as pd
import ReadRawData
import dataprocessing as dp
from databrick import DataBrick

Fs = 128
df = ReadRawData.getData()
data = DataBrick(dataframe=df)


print(data.getAlphaPower(lastSecond=True))
