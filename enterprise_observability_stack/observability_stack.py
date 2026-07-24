from aws_cdk import (
    Stack,
    Duration,
    aws_cloudwatch as cloudwatch,
    aws_sns as sns,
   # aws_sns_subscriptions as subscriptions,
    aws_iam as iam
)
import aws_cdk.aws_sns_subscriptions as subscriptions  # <-- Flytta ut denna hit!
import aws_cdk.aws_cloudwatch_actions as cw_actions  # <-- LÄGG TILL DENNA RAD!
from constructs import Construct

class ObservabilityStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Skapa en Amazon SNS Topic för incidentnotiser
        # Hit skickas alla larm, och den vidarebefordrar dem till din e-post
        alert_topic = sns.Topic(
            self, "SystemAlertTopic",
            display_name="Enterprise System Alarms"
        )

        # 2. Prenumerera på larmen med din e-postadress
        # OBS: Ändra till din riktiga e-post! Du får ett bekräftelsemejl från AWS efter deploy.
        alert_topic.add_subscription(
            subscriptions.EmailSubscription("mikaelo_66@outlook.com")
        )

        # 3. Skapa larm för din Kinesis Data Firehose (Från projekt 3)
        # Vi övervakar om Firehose misslyckas med att skriva data till din S3 Data Lake
        delivery_failed_metric = cloudwatch.Metric(
            namespace="AWS/Firehose",
            metric_name="DeliveryToS3.Failure",
            dimensions_map={
                # Ändra detta namn så det matchar det exakta namnet på din Firehose-ström från projekt 3
                "DeliveryStreamName": "ServerlessDataPipelineStack-RealTimeDataDeliveryStre-XXXX"
            },
            period=Duration.minutes(5)
        )

        firehose_alarm = delivery_failed_metric.create_alarm(
            self, "KinesisS3FailureAlarm",
            threshold=1, # Triggast om 1 eller fler felaktiga skrivningar sker inom 5 minuter
            evaluation_periods=1,
            alarm_description="Kinesis Firehose failed to deliver data to the S3 Data Lake.",
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING
        )

        # Koppla larmet till vår SNS Topic så du får ett mejl när det blir rött!
        #firehose_alarm.add_alarm_action(cloudwatch.ActionsProvider.from_sns_topic(alert_topic))
        firehose_alarm.add_alarm_action(cw_actions.SnsAction(alert_topic))

        # 4. Skapa larm för dina ECS Fargate Containers (Från projekt 2)
        # Vi använder AnomalyDetectionAlarm med rätt Python-parametrar
        cpu_metric = cloudwatch.Metric(
            namespace="AWS/ECS",
            metric_name="CPUUtilization",
            dimensions_map={
                "ClusterName": "EnterpriseCluster",
                "ServiceName": "FargateWebService"
            },
            period=Duration.minutes(1)
        )

        anomaly_alarm = cloudwatch.AnomalyDetectionAlarm(
            self, "EcsCpuAnomalyAlarm",
            metric=cpu_metric,
            std_devs=3, # Antal standardavvikelser (bandets bredd)
            evaluation_periods=2,
            datapoints_to_alarm=2,
            alarm_description="ECS Fargate CPU utilization is behaving anomalously.",
            # Larma om metriken går utanför det förväntade bandet (antingen över eller under)
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_LOWER_OR_GREATER_THAN_UPPER_THRESHOLD
        )
        anomaly_alarm.add_alarm_action(cw_actions.SnsAction(alert_topic))



        # 5. Skapa den centrala CloudWatch Dashboarden (Grafiska panelen)
        dashboard = cloudwatch.Dashboard(
            self, "EnterpriseOperationsDashboard",
            dashboard_name="Enterprise-Core-Infrastructure-Status"
        )

        # Lägg till grafer och textblock på panelen i rader och kolumner
        dashboard.add_widgets(
            cloudwatch.TextWidget(
                markdown="# 📈 Enterprise Core Infrastructure Monitoring\nReal-time observability dashboard for ECS containers and Serverless Kinesis pipelines.",
                width=24,
                height=2
            )
        )

        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="🔥 ECS Container CPU Usage & Anomalies",
                left=[cpu_metric],
                width=12,
                height=6
            ),
            cloudwatch.GraphWidget(
                title="⚠️ Kinesis Firehose Delivery Failures",
                left=[delivery_failed_metric],
                width=12,
                height=6
            )
        )

