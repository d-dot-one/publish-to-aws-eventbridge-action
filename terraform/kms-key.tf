resource "aws_kms_key" "github_action" {
  enable_key_rotation     = true
  description             = "This key is used to secure the data processed by a GitHub action"
  deletion_window_in_days = 30
  key_usage               = "ENCRYPT_DECRYPT"
  policy                  = data.aws_iam_policy_document.github_action_kms_key.json

  tags = {
    Name = local.resource_name
  }
}

resource "aws_kms_alias" "github_action" {
  name          = local.resource_name
  target_key_id = aws_kms_key.github_action.key_id
}

data "aws_iam_policy_document" "github_action_kms_key" {
  statement {
    actions = ["kms:*"] # tfsec:ignore:aws-iam-no-policy-wildcards
    effect  = "Allow"
    principals {
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
      type        = "AWS"
    }
    resources = [aws_kms_key.github_action.key_id]
    sid       = "PreventKeyLockout"
  }
  # todo: add specific required permissions for the Lambda IAM role below here
}
