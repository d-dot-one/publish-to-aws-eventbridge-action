resource "aws_sqs_queue" "github_action" {
  name                      = "github-action-queue"
  delay_seconds             = 90
  max_message_size          = 2048
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.deadletter.arn
    maxReceiveCount     = 4
  })
  sqs_managed_sse_enabled = true

  #  dynamic "encryption" {
  #    for_each = ""
  #    content {
  #      kms_master_key_id                 = "alias/aws/sqs"
  #      kms_data_key_reuse_period_seconds = 300
  #    }
  #  }

  tags = {
    Name = "github-action-queue"
  }
}

resource "aws_sqs_queue" "deadletter" {
  name = "deadletter-queue"
  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.github_action.arn]
  })

  tags = {
    Name = "deadletter-queue"
  }
}
