"""
Base class and utilities for defining neural networks to be used on ComptoxAI
data.

We stick to PyTorch for implementing all neural networks, due to its speed,
expressiveness, and readability. For more documentation on PyTorch, check out 
`PyTorch Documentation<https://pytorch.org/docs/stable/index.html>`_. Several
of the models we have reimplemented for ComptoxAI were previously only
implemented in Tensorflow or another deep learning library. Users are strongly
encouraged to submit pull requests or create a new issue on GitHub if they
discover any errors made in the translation process!
"""

from torch import nn

class NeuralNetwork(object):
    def __init__(self, **kwargs):
        arg_opts = {
            'name',
            'lr',
            'num_epochs',
            'logging',
            'verbose'
        }
        for kwarg in kwargs.keys():
            assert kwarg in arg_opts, 'Invalid argument: {}'.format(kwarg)

        self.verbose = kwargs.get('verbose', False)

    ext_library = 'pytorch'
