resource "aws_iam_role" "github_action" {
  assume_role_policy = data.aws_iam_policy_document.github_action_role.json
}

data "aws_iam_policy_document" "github_action_role" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      identifiers = ["lambda.amazonaws.com"]
      type        = "Service"
    }
    principals {
      identifiers = ["arn:aws:iam::${var.account_number}:user/${var.user_name}"]
      type        = "AWS"
    }
  }
}

data "aws_iam_policy_document" "github_action" {
  statement {
    actions   = ["*"] # todo: scope these actions to least-access, least-privilege
    effect    = "Allow"
    resources = ["*"] # todo: scope this to the resources that you need
  }

  statement {
    actions   = ["kms:*"] # todo: scope this to only the actions that the Lambda role requires
    effect    = "Allow"
    resources = [aws_kms_key.github_action.key_id]
    sid       = "AllowKmsKeyUsage"
  }
}

resource "aws_iam_policy" "github_action" {
  name        = local.resource_name
  description = "This policy grants permission to a Lambda function to work"
  policy      = data.aws_iam_policy_document.github_action_kms_key.json
}

resource "aws_iam_role_policy_attachment" "github_action" {
  policy_arn = aws_iam_policy.github_action.arn
  role       = aws_iam_role.github_action.name
}
