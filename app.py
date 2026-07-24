#!/usr/bin/env python3
import aws_cdk as cdk

# Importera din nyskapade övervakningsstack
from enterprise_observability_stack.observability_stack import ObservabilityStack

app = cdk.App()

# Initiera din centrala övervakning och dashboard
ObservabilityStack(
    app, "EnterpriseObservabilityStack",
    # Vi sätter explicit region till Stockholm så att larmen letar efter rätt resurser
    env=cdk.Environment(region="eu-north-1")
)

app.synth()
