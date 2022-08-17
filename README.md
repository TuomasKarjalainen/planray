# Industrial electric trace heating data
Scripts for the self-made data pipeline including data fetch from REST-API, raw data preprocess, feature engineering, online database (MariaDB) implementation over SSH-connection. After data process and feature engineering, the target feature is predicted with two different types of neural networks: fully connected (FC) regression neural network and 2-dimensional convolution NN (2D-CNN). 

All scripts have a docstring documentation with a brief description of their purpose and parameters.  

![pipeline](https://user-images.githubusercontent.com/91312571/185053006-bf1b71bf-c4f7-474b-a932-270abf1d851f.jpg)

--
There is also **documentation** in Finnish for this, which is not publicly available. 
The document contains, for example, data analysis and images, further development ideas, architecture description, and analysis of the results of machine learning methods. 

## Model's Accuracy

*The model's accuracy for data it hasn't seen before*
![image](https://user-images.githubusercontent.com/91312571/185051492-8eb29ac3-5ad3-49f7-9784-606fb7b5802d.png)

- The model predicts the power of the heating circuit (kWh)
- Mean absolute error (MAE): `0.0672`
