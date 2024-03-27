# serverless
Cloud Function Code

#command to upload the code
zip -r function-source.zip function/
gsutil cp function-source.zip gs://csye6225-414117-gcf-source/ 