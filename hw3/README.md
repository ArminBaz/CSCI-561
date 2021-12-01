## Homework 3 : MLP From Scratch
This code is very simple to run:
```console
>> python train_image.csv train_label.csv test_image.csv
```
Where you can replace all of the commands with whatever csv files you want. 
<br /> <br />
Note that if you want to run this locally in the directory you have to specify data/train_image.csv, data/train_label.csv, and data/test_image.csv. 
Additionally, note that you will have to change the code on line 198 to:
```python
pd.DataFrame(pred).to_csv('data/test_predictions.csv', header=None, index=None)
```
