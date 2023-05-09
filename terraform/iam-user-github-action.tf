# tfsec:ignore:aws-iam-no-user-attached-policies
resource "aws_iam_user" "github_action" {
  name = local.resource_name

  tags = {
    Name = local.resource_name
  }
}

resource "aws_iam_access_key" "github_action" {
  user    = aws_iam_user.github_action.name
  pgp_key = var.public_pgp_key
}

data "aws_iam_policy_document" "github_action_user" {
  statement {
    actions   = ["sns:Publish"]
    effect    = "Allow"
    resources = [aws_sns_topic.github_action.arn]
    sid       = "AllowPublishToSns"
  }
}

resource "aws_iam_policy" "github_action_user" {
  name        = local.resource_name
  description = "This policy grants permission for a GitHub actions user to publish to SNS"
  policy      = data.aws_iam_policy_document.github_action_user.json
}

resource "aws_iam_user_policy_attachment" "github_action_user" {
  policy_arn = aws_iam_policy.github_action_user.arn
  user       = aws_iam_user.github_action.name
}
