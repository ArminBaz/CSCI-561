## Homework 3 : MLP From Scratch
To run the code:
```console
python data/train_image.csv data/train_label.csv data/test_image.csv NeuralNetwork3.py
```
Where you can replace all of the commands with whatever csv files you want. 
<br /> <br />
Note that if you want to run this locally in the directory you have to specify data/train_image.csv, data/train_label.csv, and data/test_image.csv. 
Additionally, note that you will have to change the code on line 198 to:
```python
pd.DataFrame(pred).to_csv('data/test_predictions.csv', header=None, index=None)
```
