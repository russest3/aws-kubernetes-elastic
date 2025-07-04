#!/usr/bin/env python3
import os
import aws_cdk as cdk
from aws_cdk import (
    Environment
)

from cdk_workspace.cdk_workspace_stack import CdkWorkspaceStack
from cdk_workspace.vpn_stack import VPNStack

app = cdk.App()

env = Environment(account="014420964653", region="us-east-2")

root_stack = cdk.Stack(app, "RootStack", env=env)

vpn_stack = VPNStack(root_stack, "VPNStack")

application_stack = CdkWorkspaceStack(root_stack, "CdkWorkspaceStack", my_vpc=vpn_stack.my_vpc)

app.synth()
