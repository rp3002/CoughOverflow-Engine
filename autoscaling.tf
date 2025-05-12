# ========================
# ECS Autoscaling Setup
# ========================

resource "aws_appautoscaling_target" "coughoverflow" {
  max_capacity       = 4
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.coughoverflow_cluster.name}/${aws_ecs_service.coughoverflow_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  depends_on = [aws_ecs_service.coughoverflow_service]
}

resource "aws_appautoscaling_policy" "coughoverflow_cpu" {
  name               = "coughoverflow-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.coughoverflow.resource_id
  scalable_dimension = aws_appautoscaling_target.coughoverflow.scalable_dimension
  service_namespace  = aws_appautoscaling_target.coughoverflow.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 40
  }
}
