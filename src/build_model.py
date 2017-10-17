import numpy as np
import tensorflow as tf

# Data sets
TRAINING_FILENAME = 'training.csv'

TESTING_FILENAME = 'testing.csv'

def main():
    # Load datasets.

    training_x = []
    training_y = []
    with open(TRAINING_FILENAME, 'r', newline='') as training_csv:
        reader = csv.reader(training_csv, delimiter=',')
        for row in reader:
            training_y.append(int(row.pop()))
            training_x.append([float(num) for num in row])

    testing_x = []
    testing_y = []
    with open(TESTING_FILENAME, 'r', newline='') as testing_csv:
        reader = csv.reader(testing_csv, delimiter=',')
        for row in reader:
            testing_y.append(int(row.pop()))
            testing_x.append([float(num) for num in row])


    # Specify that all features have real-value data
    feature_columns = [tf.feature_column.numeric_column(
        'x',
        shape=[8]
    )]

    # Build 3 layer DNN with 10, 20, 10 units respectively.
    classifier = tf.estimator.DNNClassifier(
        feature_columns=feature_columns,
        hidden_units=[10, 20, 10],
        n_classes=3,
        model_dir='../models/flu_model'
    )
    # Define the training inputs
    train_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={'x': np.array(training_x)},
        y=np.array(training_y),
        num_epochs=None,
        shuffle=True
    )

    # Train model.
    classifier.train(input_fn=train_input_fn, steps=2000)

    # Define the test inputs
    test_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={'x': np.array(testing_x)},
        y=np.array(testing_y),
        num_epochs=1,
        shuffle=False
    )

    # Evaluate accuracy.
    accuracy_score = classifier.evaluate(input_fn=test_input_fn)['accuracy']

    print('\nTest Accuracy: {0:f}\n'.format(accuracy_score))


if __name__ == '__main__':
    main()
