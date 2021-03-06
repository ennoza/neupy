import numpy as np

from neupy import layers
from neupy.utils import asfloat

from base import BaseTestCase


class UsageTestCase(BaseTestCase):
    def test_network_wrong_number_of_input_values(self):
        network = layers.join(
            layers.Input(2),
            layers.Relu(10),
            layers.Relu(1),
        )

        input_value_1 = asfloat(np.random.random((10, 2)))
        input_value_2 = asfloat(np.random.random((10, 2)))

        with self.assertRaisesRegexp(ValueError, "but 2 inputs was provided"):
            network.output(input_value_1, input_value_2)

    def test_multi_outputs_propagation(self):
        network = layers.join(
            layers.Input(4),
            layers.parallel(
                layers.Linear(2),
                layers.Linear(3),
                layers.Linear(4),
            )
        )
        x = asfloat(np.random.random((7, 4)))
        out1, out2, out3 = self.eval(network.output(x))

        self.assertEqual((7, 2), out1.shape)
        self.assertEqual((7, 3), out2.shape)
        self.assertEqual((7, 4), out3.shape)

    def test_multi_inputs_propagation(self):
        network = layers.join(
            layers.parallel(
                layers.Input(10, name='input-1'),
                layers.Input(4, name='input-2'),
            ),
            layers.Concatenate(),
        )
        x1 = asfloat(np.random.random((3, 10)))
        x2 = asfloat(np.random.random((3, 4)))

        out1 = self.eval(network.output(x1, x2))
        out2 = self.eval(network.output({'input-2': x2, 'input-1': x1}))

        self.assertEqual((3, 14), out1.shape)
        np.testing.assert_array_almost_equal(out1, out2)

    def test_different_input_types(self):
        input_layer = layers.Input(10, name='input')
        network = layers.join(
            input_layer,
            layers.Sigmoid(5),
            layers.Sigmoid(4),
        )

        x_matrix = asfloat(np.random.random((3, 10)))
        out1 = self.eval(network.output(x_matrix))
        self.assertEqual((3, 4), out1.shape)

        out2 = self.eval(network.output({input_layer: x_matrix}))
        np.testing.assert_array_almost_equal(out1, out2)

        out3 = self.eval(network.output({'input': x_matrix}))
        np.testing.assert_array_almost_equal(out2, out3)

        unknown_layer = layers.Input(5, name='unk')
        message = "The `unk` layer doesn't appear in the network"
        with self.assertRaisesRegexp(ValueError, message):
            network.output({unknown_layer: x_matrix})

    def test_not_an_input_layer_exception(self):
        network = layers.join(
            layers.Input(10),
            layers.Sigmoid(2, name='sigmoid-2'),
            layers.Sigmoid(10),
        )
        x_test = asfloat(np.ones((7, 5)))

        with self.assertRaisesRegexp(ValueError, "is not an input layer"):
            network.output({'sigmoid-2': x_test})

    def test_if_layer_in_the_graph(self):
        network = layers.join(
            layers.Input(10),
            layers.Relu(2),
        )
        final_layer = layers.Sigmoid(1)
        self.assertNotIn(final_layer, network)

        network_2 = layers.join(network, final_layer)
        self.assertIn(final_layer, network_2)

    def test_graph_length(self):
        network = layers.join(
            layers.Input(10),
            layers.Relu(3),
        )
        self.assertEqual(2, len(network))

        network_2 = layers.join(
            network,
            layers.parallel(
                layers.Relu(1),
                layers.Relu(2),
            ),
        )
        self.assertEqual(2, len(network))
        self.assertEqual(4, len(network_2))

    def test_graph_predictions(self):
        network = layers.join(
            layers.Input(10),
            layers.Relu(5),
            layers.Relu(3),
        )

        input = np.random.random((100, 10))
        output = network.predict(input, verbose=False)
        self.assertEqual(output.shape, (100, 3))

        output = network.predict(input, batch_size=10, verbose=False)
        self.assertEqual(output.shape, (100, 3))

        with self.assertRaisesRegexp(TypeError, "Unknown arguments"):
            network.predict(input, batchsize=10)
