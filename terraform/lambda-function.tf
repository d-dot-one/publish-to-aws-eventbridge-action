data "archive_file" "github_action" {
  output_path = "${path.module}/lambda.zip"
  source_dir  = "${path.module}/../action/"
  type        = "zip"
}

# tfsec:ignore:aws-lambda-enable-tracing
resource "aws_lambda_function" "github_action" {
  description   = "This Lambda function ..." # todo: update with a good description
  filename      = "${path.module}/lambda.zip"
  function_name = local.resource_name
  handler       = "app.lambda_handler"
  kms_key_arn   = aws_kms_key.github_action.arn
  role          = aws_iam_role.github_action.arn
  runtime       = "python3.9"
  timeout       = 60

  environment {
    variables = {
      ENV_VAR_1 = "some_interesting_environment_variable_that_lambda_needs" # todo: update this
    }
  }
}

resource "aws_lambda_permission" "github_action_allow_sns_invoke" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.github_action.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_cloudwatch_event_endpoint.
  statement_id  = "AllowExecutionFromSNS"
}
