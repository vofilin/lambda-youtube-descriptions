FROM public.ecr.aws/lambda/python:3.9

# Install the function's dependencies
COPY requirements.txt  .
RUN  pip install -r requirements.txt

# Copy function code
COPY youtube_descriptions.py .

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "youtube_descriptions.lambda_handler" ]
