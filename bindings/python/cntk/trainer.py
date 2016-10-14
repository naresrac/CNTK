# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root
# for full license information.
# ==============================================================================

from . import cntk_py
from .cntk_py import DeviceDescriptor
from .utils import sanitize_var_map, sanitize_function, typemap, value_to_seq

__doc__= '''
A trainer supervises the overall training process and commands one or more
:doc:`learner <cntk.learner>` that learn the parameters.
'''
class Trainer(cntk_py.Trainer):
    '''
    Trainer to train the specified `model` with the specified `training_loss`
    as the training criterion, the specified `evaluation_function` as the
    criterion for evaluating the trained model's quality, and using the
    specified set of `parameter_learners` for updating the model's parameters
    using computed gradients.

    Args:
       model (:class:`cntk.ops.function.Function`): root node of the function to train
       loss_function (:class:`cntk.ops.functions.Function`): loss function 
       eval_function (:class:`cntk.ops.functions.Function`): evaluation function
       parameter_learners (`list`): list of learners from :cntk:`cntk.learner`
    '''
    def __init__(self, model, loss_function, eval_function, parameter_learners):
        # TODO sanitizing should be removed once Swig's typemaps are in place
        model = sanitize_function(model)
        loss_function = sanitize_function(loss_function)
        eval_function = sanitize_function(eval_function)

        super(Trainer, self).__init__(model, loss_function, eval_function,
                parameter_learners)

    def train_minibatch(self, arguments, outputs=None, device=None):
        '''
        Optimize model parameters using the specified 'arguments' minibatch of training samples.

        Args:
            arguments (`dict` or `list` or `tuple`): maps variables to their
             input data. The interpretation depends on the input type:
               * `dict`: keys are input variable or names and values are the input data. 
               * `list`: elements are input data in the order their respective variables have been defined in the network. 
             In both cases, every every sample in the data will be interpreted
             as a new sequence. To mark samples as continuations of the
             previous sequence, specify `arguments` as `tuple`: the
             first element will be used as `arguments`, and the second one will
             be used as a list of bools, denoting whether a sequence is a new
             one (`True`) or a continuation of the previous one (`False`).
             Data should be either NumPy arrays or a
             :class:`cntk.io.MinibatchData` instance.
            outputs (iterable): outputs to fetch values for.
            device (:class:`cntk.DeviceDescriptor`): the device descriptor that
             contains the type and id of the device on which the computation is
             to be performed.

        Returns:
            `bool` or `tuple`: 
            If `outputs` have not been provided, the returned value is `True`
            if updates have been performed, `False` if all parameter learners
            indicate end of learning (through their `update`. Otherwise, the
            return value is a tuple of the that `bool` and a dictionary that
            maps the variables in `outputs` to their respective NumPy arrays.
        '''
        if not device:
            device=DeviceDescriptor.use_default_device()        
        arguments = sanitize_var_map(self.model().arguments(), arguments)

        if outputs:
            output_map = {v: None for v in outputs}
            updated = super(Trainer, self).train_minibatch(arguments,
                    output_map, device)
            for k,v in output_map.items():
                output_map[k] = value_to_seq(v)

            return updated, output_map
        else:
            updated = super(Trainer, self).train_minibatch(arguments, device)

        return updated


    def test_minibatch(self, arguments, seq_starts=None, device=None):
        '''
        Test the model on the specified batch of samples using the evaluation
        Function specified during construction of the Trainer. 
        of samples.

        Args:
            arguments (`dict` or `list` or `tuple`): maps variables to their
             input data. The interpretation depends on the input type:
               * `dict`: keys are input variable or names and values are the input data. 
               * `list`: elements are input data in the order their respective variables have been defined in the network. 
             In both cases, every every sample in the data will be interpreted
             as a new sequence. To mark samples as continuations of the
             previous sequence, specify `arguments` as `tuple`: the
             first element will be used as `arguments`, and the second one will
             be used as a list of bools, denoting whether a sequence is a new
             one (`True`) or a continuation of the previous one (`False`).
             Data should be either NumPy arrays or a
             :class:`cntk.io.MinibatchData` instance.
            seq_starts (`list` of `bool`s or `None`): if `None`, every sequence is
             treated as a new sequence. Otherwise, it is interpreted as a list of
             Booleans that tell whether a sequence is a new sequence (`True`) or a
             continuation of the previous one (`False`)
            device (:class:`cntk.DeviceDescriptor`): the device descriptor that
             contains the type and id of the device on which the computation is
             to be performed.
        Returns:
            `float`: the average evaluation criterion value per sample for the
              tested minibatch.
        '''
        if not device:
            device=DeviceDescriptor.use_default_device()        
        arguments = sanitize_var_map(self.model().arguments(), arguments,
                seq_starts)

        return super(Trainer, self).test_minibatch(arguments, device)

    def save_checkpoint(self, filename):
        '''
        Saves a checkpoint of the model and other Trainer state at the
        specified file location.

        Args:
            filename (`str`): filename to store the checkpoint
        '''

        super(Trainer, self).save_checkpoint(filename)

    def restore_from_checkpoint(self, filename):
        '''
        Saves a checkpoint of the model and other Trainer state at the
        specified file location.

        Args:
            filename (`str`): filename to restore the checkpoint from
        '''

        super(Trainer, self).restore_from_checkpoint(filename)

    @typemap
    def model(self):
        '''
        Returns the model that the trainer is training.

        Returns:
            :class:`cntk.ops.functions.Function`
        '''
        return super(Trainer, self).model()
        
    @typemap
    def loss_function(self):
        '''
        Returns the loss function that the trainer is using.

        Returns:
            :class:`cntk.ops.functions.Function`
        '''
        return super(Trainer, self).loss_function()

    @typemap
    def evaluation_function(self):
        '''
        Returns the evaluation function that the trainer is using.

        Returns:
            :class:`cntk.ops.functions.Function`
        '''
        return super(Trainer, self).evaluation_function()

    @typemap
    def parameter_learners(self):
        '''
        Returns the parameter learners that the trainer is using.

        Returns:
            `list` of :class:`cntk.learner.Learner`
        '''
        return super(Trainer, self).parameter_learners()

    def previous_minibatch_loss_average(self):
        '''
        Returns the average training loss per sample for the last minibatch trained

        Returns:
            `double`
        '''
        return super(Trainer, self).previous_minibatch_loss_average()

    def previous_minibatch_evaluation_average(self):
        '''
        Returns the average evaluation criterion value per sample for the last minibatch trained

        Returns:
            `double`
        '''
        return super(Trainer, self).previous_minibatch_evaluation_average()

    def previous_minibatch_sample_count(self):
        '''
        Returns the number of samples in the last minibatch trained with

        Returns:
            `int`
        '''
        return super(Trainer, self).previous_minibatch_sample_count()

