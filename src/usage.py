import os
import numpy as np
import boto3
import sagemaker
from dotenv import load_dotenv

load_dotenv()

session = boto3.Session(
	aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
	aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
	region_name='us-west-2',
)
session = sagemaker.Session(boto_session=session)

endpoint_name = 'dsci560-ast-endpoint0'
predictor = sagemaker.predictor.Predictor(endpoint_name=endpoint_name, sagemaker_session=session)
predictor.serializer = sagemaker.serializers.NumpySerializer()

block = np.random.rand(20000) * 0.2 - 0.1
print(predictor.predict(block))