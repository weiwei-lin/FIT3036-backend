import numpy as np
import tensorflow as tf

def predict(symptoms):
    """
    :return:
    """

    # Specify that all features have real-value data
    feature_columns = [tf.feature_column.numeric_column('x', shape=[8])]

    classifier = tf.estimator.DNNClassifier(
        feature_columns=feature_columns,
        hidden_units=[10, 20, 10],
        n_classes=3,
        model_dir='../models/flu_model'
    )

    test_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={'x': np.array([symptoms])},
        num_epochs=1,
        shuffle=False
    )
    for prediction in classifier.predict(test_input_fn):
        probabilities = prediction.get('probabilities')
        return {
            'no': float(probabilities[0]),
            'yes': float(probabilities[1])
        }


if __name__ == '__main__':
    result = predict([0, 0, 1, 1, 0, 0, 1, 1])
    print(result)
