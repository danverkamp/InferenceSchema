# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import numpy as np
import pandas as pd
import pyspark

from inference_schema.parameter_types.numpy_parameter_type import NumpyParameterType
from inference_schema.parameter_types.pandas_parameter_type import PandasParameterType
from inference_schema.parameter_types.spark_parameter_type import SparkParameterType
from inference_schema.parameter_types.standard_py_parameter_type import StandardPythonParameterType
from inference_schema.schema_decorators import input_schema, output_schema
from pyspark.sql.session import SparkSession


numpy_input_data = [('Sarah', (8.0, 7.0)), ('John', (6.0, 7.0))]
numpy_sample_input = np.array(numpy_input_data,
                              dtype=np.dtype([('name', np.unicode_, 16), ('grades', np.float64, (2,))]))
numpy_output_data = [(8.0, 7.0), (6.0, 7.0)]
numpy_sample_output = np.array(numpy_output_data, dtype='float64, float64')


@input_schema('param', NumpyParameterType(numpy_sample_input))
@output_schema(NumpyParameterType(numpy_sample_output))
def numpy_func(param):
    """

    :param param:
    :type param: np.ndarray
    :return:
    :rtype: np.ndarray
    """
    assert type(param) is np.ndarray
    return param['grades']


pandas_input_data = {'name': ['Sarah', 'John'], 'age': [25, 26]}
pandas_sample_input = pd.DataFrame(data=pandas_input_data)
pandas_output_data = {'age': [25, 26]}
pandas_sample_output = pd.DataFrame(data=pandas_output_data)


@input_schema('param', PandasParameterType(pandas_sample_input))
@output_schema(PandasParameterType(pandas_sample_output))
def pandas_func(param):
    """

    :param param:
    :type param: pd.DataFrame
    :return:
    :rtype: pd.DataFrame
    """
    assert type(param) is pd.DataFrame
    return pd.DataFrame(param['age'])


pandas_sample_timestamp_input = pd.DataFrame({'datetime': pd.Series(['2013-12-31T00:00:00.000Z'],
                                                                    dtype='datetime64[ns]')})


@input_schema('param', PandasParameterType(pandas_sample_timestamp_input))
def pandas_datetime_func(param):
    """

    :param param:
    :type param: pd.DataFrame
    :return:
    :rtype: pd.DataFrame
    """
    assert type(param) is pd.DataFrame
    return pd.DataFrame(param['datetime'])


spark_session = SparkSession.builder.getOrCreate()
spark_input_data = pd.DataFrame({'name': ['Sarah', 'John'], 'age': [25, 26]})
spark_sample_input = spark_session.createDataFrame(spark_input_data)
spark_output_data = pd.DataFrame({'age': [25, 26]})
spark_sample_output = spark_session.createDataFrame(spark_output_data)


@input_schema('param', SparkParameterType(spark_sample_input))
@output_schema(SparkParameterType(spark_sample_output))
def spark_func(param):
    """

    :param param:
    :type param: pyspark.sql.dataframe.DataFrame
    :return:
    :rtype: pyspark.sql.dataframe.DataFrame
    """
    assert type(param) is pyspark.sql.dataframe.DataFrame
    return param.select('age')


standard_sample_input = {'name': ['Sarah', 'John'], 'age': [25, 26]}
standard_sample_output = {'age': [25, 26]}


@input_schema('param', StandardPythonParameterType(standard_sample_input))
@output_schema(StandardPythonParameterType(standard_sample_output))
def standard_py_func(param):
    assert type(param) is dict
    return {'age': param['age']}


# input0 are not wrapped by any ParameterTypes hence will be neglected
nested_sample_input = StandardPythonParameterType(
    {'input1': PandasParameterType(pandas_sample_input),
     'input2': NumpyParameterType(numpy_sample_input),
     'input3': StandardPythonParameterType(standard_sample_input),
     'input0': 0}
)
nested_input_data = {'input1': pandas_input_data,
                     'input2': numpy_input_data,
                     'input3': standard_sample_input,
                     'input0': 0}
nested_sample_output = StandardPythonParameterType(
    {'output1': PandasParameterType(pandas_sample_output),
     'output2': NumpyParameterType(numpy_sample_output),
     'output3': StandardPythonParameterType(standard_sample_output),
     'output0': 0}
)
nested_output_data = {'output1': pandas_output_data,
                      'output2': numpy_output_data,
                      'output3': standard_sample_output,
                      'output0': 0}


@input_schema('param', nested_sample_input)
@output_schema(nested_sample_output)
def nested_func(param):
    """

    :param param:
    :type param: pd.DataFrame
    :return:
    :rtype: pd.DataFrame
    """
    assert type(param) is dict
    assert 'input0' in param.keys()
    assert 'input1' in param.keys() and type(param['input1']) is pd.DataFrame
    assert 'input2' in param.keys() and type(param['input2']) is np.ndarray
    assert 'input3' in param.keys() and type(param['input3']) is dict
    output1 = pd.DataFrame(param['input1']['age'])
    output2 = param['input2']['grades']
    output3 = {'age': param['input3']['age']}
    return {'output0': param['input0'], 'output1': output1, 'output2': output2, 'output3': output3}
