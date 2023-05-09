resource "aws_cloudwatch_event_bus" "github" {
  name = "github-eventbus"
  tags = {
    Name = "github-eventbus"
  }
}

resource "aws_cloudwatch_event_rule" "github" {
  name = 'github-events'
}

resource "aws_cloudwatch_event_endpoint" "github" {
  event_bus {
    event_bus_arn = aws_cloudwatch_event_bus.github.arn
  }

  replication_config {
    state = "DISABLED"
  }

  routing_config {
    failover_config {
      primary {
        health_check = aws_route53_health_check.primary.arn
      }

      secondary {
        route = "us-east-2"
      }
    }
  }
}