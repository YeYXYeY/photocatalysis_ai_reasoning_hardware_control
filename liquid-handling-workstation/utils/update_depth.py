from sklearn.linear_model import LinearRegression
import numpy as np

model = LinearRegression()

depths = []
outputs = []


def update_model(depth, output):
    depths.append(depth)
    outputs.append([output])

    model.fit(np.array(outputs), np.array(depths))


def predict_depth(output):
    predicted_depth = model.predict(np.array([[output]]))
    return predicted_depth[0]


# ,20
update_model(1, 0.6)
update_model(2, 1.4)
update_model(3, 1.8)
update_model(4, 2.6)
update_model(5, 3.0)
update_model(6, 3.4)
update_model(7, 4.3)
update_model(8, 4.6)
update_model(9, 5.5)

# matplotlib
import matplotlib.pyplot as plt

plt.scatter(outputs, depths)
plt.plot(outputs, model.predict(np.array(outputs).reshape(-1, 1)), color="red")
plt.xlabel("Output")
plt.ylabel("Depth")
plt.show()


print(predict_depth(7.5))
